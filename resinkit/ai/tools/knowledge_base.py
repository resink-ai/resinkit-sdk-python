import fnmatch
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from llama_index.core import Document, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

from resinkit.core.settings import get_settings

logger = logging.getLogger(__name__)


class FileKnowledgeBase:
    """
    A knowledge base that supports adding files and directories, with semantic search capabilities.
    """

    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        test_mode: bool = False,
        kb_id: str = "default",
    ):
        """
        Initialize the FileKnowledgeBase.

        Args:
            persist_dir: Directory to persist the vector store data
            test_mode: If True, uses mock embeddings and LLM for testing without API keys
            kb_id: Unique identifier for this knowledge base instance
        """
        self.persist_dir = persist_dir
        self.test_mode = test_mode
        self.kb_id = kb_id
        self.settings = get_settings()

        # Initialize state file path
        self.state_file_path = self._get_state_file_path()

        # Initialize embedding model
        self.embed_model = self._get_embedding_model()

        # Initialize LLM (only if not in test mode)
        self.llm = self._get_llm() if not test_mode else None

        # Initialize vector store
        self.vector_store = self._initialize_vector_store()

        # Initialize storage context
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

        # Initialize index
        self.index = VectorStoreIndex.from_vector_store(self.vector_store, embed_model=self.embed_model)

        # Node parser for chunking
        self.node_parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=200)

        # Keep track of added files to avoid duplicates
        self._added_files = set()

        # Load previous state if exists
        self._load_state()

    def _get_state_file_path(self) -> Path:
        """Get the path to the state file for this knowledge base."""
        persist_root = Path(self.settings.knowledge_base_config.persist_root_dir)
        persist_root.mkdir(parents=True, exist_ok=True)
        return persist_root / f"kb_{self.kb_id}_state.json"

    def _save_state(self) -> None:
        """Save the current state to disk."""
        try:
            if not self.settings.knowledge_base_config.auto_persist:
                return

            state_data = {
                "kb_id": self.kb_id,
                "persist_dir": str(self.persist_dir),
                "added_files": list(self._added_files),
                "test_mode": self.test_mode,
                "embedding_provider": self.settings.embedding_config.provider,
                "embedding_model": self.settings.embedding_config.model,
                "llm_provider": self.settings.llm_config.provider,
                "llm_model": self.settings.llm_config.model,
            }

            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Saved knowledge base state to {self.state_file_path}")

        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _load_state(self) -> None:
        """Load the previous state from disk."""
        try:
            if not self.state_file_path.exists():
                logger.debug(f"No previous state found at {self.state_file_path}")
                return

            with open(self.state_file_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)

            # Validate state compatibility
            if state_data.get("kb_id") != self.kb_id:
                logger.warning(f"State file kb_id mismatch: expected {self.kb_id}, got {state_data.get('kb_id')}")
                return

            if state_data.get("persist_dir") != str(self.persist_dir):
                logger.warning(
                    f"State file persist_dir mismatch: expected {self.persist_dir}, got {state_data.get('persist_dir')}"
                )
                return

            # Load added files
            added_files = state_data.get("added_files", [])
            if added_files:
                # Validate that files still exist
                valid_files = []
                for file_path in added_files:
                    if Path(file_path).exists():
                        valid_files.append(file_path)
                    else:
                        logger.warning(f"Previously added file no longer exists: {file_path}")

                self._added_files = set(valid_files)
                logger.info(f"Loaded {len(self._added_files)} previously added files")

            logger.debug(f"Loaded knowledge base state from {self.state_file_path}")

        except Exception as e:
            logger.error(f"Failed to load state: {e}")

    def _get_embedding_model(self) -> BaseEmbedding:
        """Get the configured embedding model."""
        # Use default embedding model for test mode
        if self.test_mode:
            from llama_index.core.embeddings import MockEmbedding

            return MockEmbedding(embed_dim=768)

        embedding_config = self.settings.embedding_config

        if embedding_config.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required for Google embeddings")
            return GoogleGenAIEmbedding(model=embedding_config.model, api_key=api_key)
        elif embedding_config.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI embeddings")
            return OpenAIEmbedding(model=embedding_config.model, api_key=api_key)
        else:
            raise ValueError(f"Unsupported embedding provider: {embedding_config.provider}")

    def _get_llm(self) -> LLM:
        """Get the configured LLM."""
        llm_config = self.settings.llm_config

        if llm_config.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI LLM")
            return OpenAI(
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                api_key=api_key,
            )
        elif llm_config.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic LLM")
            return Anthropic(
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                api_key=api_key,
            )
        elif llm_config.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is required for Google LLM")
            return GoogleGenAI(
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=llm_config.max_tokens,
                api_key=api_key,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_config.provider}")

    def _initialize_vector_store(self) -> ChromaVectorStore:
        """Initialize the ChromaDB vector store."""
        # Create ChromaDB client
        chroma_client = chromadb.PersistentClient(path=self.persist_dir)

        # Create or get collection
        chroma_collection = chroma_client.get_or_create_collection("knowledge_base")

        # Create vector store
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        return vector_store

    def add_file(self, file_path: str) -> None:
        """
        Add a single file to the knowledge base.

        Args:
            file_path: Path to the file to add
        """
        file_path = Path(file_path).resolve()

        if str(file_path) in self._added_files:
            logger.info(f"File {file_path} already added, skipping.")
            return

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Load document
            documents = SimpleDirectoryReader(input_files=[str(file_path)], filename_as_id=True).load_data()

            if not documents:
                logger.warning(f"No content loaded from {file_path}")
                return

            # Add metadata
            for doc in documents:
                doc.metadata["source_file"] = str(file_path)
                doc.metadata["file_name"] = file_path.name
                doc.metadata["file_type"] = file_path.suffix

            # Parse nodes
            nodes = self.node_parser.get_nodes_from_documents(documents)

            # Add to index
            self.index.insert_nodes(nodes)

            # Track added file
            self._added_files.add(str(file_path))

            logger.info(f"Added file {file_path} to knowledge base ({len(nodes)} nodes)")

            # Persist state after successful addition
            self._save_state()

        except Exception as e:
            logger.error(f"Error adding file {file_path}: {str(e)}")
            raise

    def add_directory(self, directory_path: str) -> None:
        """
        Add all files from a directory to the knowledge base.

        Args:
            directory_path: Path to the directory to add
        """
        directory_path = Path(directory_path).resolve()

        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if not directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")

        try:
            # Load all documents from directory
            documents = SimpleDirectoryReader(
                input_dir=str(directory_path), recursive=True, filename_as_id=True
            ).load_data()

            if not documents:
                logger.warning(f"No documents loaded from {directory_path}")
                return

            # Add metadata and filter out already added files
            filtered_docs = []
            for doc in documents:
                source_file = doc.metadata.get("file_path", "")
                if source_file not in self._added_files:
                    doc.metadata["source_file"] = source_file
                    doc.metadata["file_name"] = Path(source_file).name
                    doc.metadata["file_type"] = Path(source_file).suffix
                    filtered_docs.append(doc)
                    self._added_files.add(source_file)

            if not filtered_docs:
                logger.info(f"All files in {directory_path} already added")
                return

            # Parse nodes
            nodes = self.node_parser.get_nodes_from_documents(filtered_docs)

            # Add to index
            self.index.insert_nodes(nodes)

            logger.info(
                f"Added {len(filtered_docs)} files from {directory_path} to knowledge base ({len(nodes)} nodes)"
            )

            # Persist state after successful addition
            self._save_state()

        except Exception as e:
            logger.error(f"Error adding directory {directory_path}: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 5, target_directories: Optional[str] = None) -> List[NodeWithScore]:
        """
        Search for relevant content in the knowledge base.

        Args:
            query: Search query
            top_k: Number of top results to return
            target_directories: Optional directory path or glob pattern to filter results

        Returns:
            List of nodes with scores
        """
        try:
            # Create retriever
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=top_k * 2,  # Get more results for filtering
            )

            # Retrieve nodes
            nodes = retriever.retrieve(query)

            # Filter by target directories if specified
            if target_directories:
                filtered_nodes = []
                for node in nodes:
                    source_file = node.metadata.get("source_file", "")
                    if self._matches_target_directory(source_file, target_directories):
                        filtered_nodes.append(node)
                nodes = filtered_nodes

            # Return top_k results
            return nodes[:top_k]

        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            raise

    def query_with_response(self, query: str, top_k: int = 5, target_directories: Optional[str] = None) -> str:
        """
        Query the knowledge base and get an AI-generated response.

        Args:
            query: Query string
            top_k: Number of top results to use for response generation
            target_directories: Optional directory path or glob pattern to filter results

        Returns:
            AI-generated response based on search results
        """
        try:
            # Get relevant nodes
            nodes = self.search(query, top_k, target_directories)

            if not nodes:
                return "No relevant information found in the knowledge base."

            # In test mode, return a simple response
            if self.test_mode:
                return f"Found {len(nodes)} relevant results for query: {query}"

            # Create query engine
            response_synthesizer = get_response_synthesizer(llm=self.llm, response_mode="tree_summarize")

            query_engine = RetrieverQueryEngine(
                retriever=VectorIndexRetriever(index=self.index, similarity_top_k=top_k),
                response_synthesizer=response_synthesizer,
            )

            # Generate response
            response = query_engine.query(query)

            return str(response)

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def _matches_target_directory(self, file_path: str, target_pattern: str) -> bool:
        """
        Check if a file path matches the target directory pattern.

        Args:
            file_path: Path to check
            target_pattern: Directory path or glob pattern

        Returns:
            True if the file matches the pattern
        """
        file_path = Path(file_path).resolve()

        # If target_pattern contains wildcards, use glob matching
        if "*" in target_pattern or "?" in target_pattern:
            return fnmatch.fnmatch(str(file_path), target_pattern)
        else:
            # Simple directory matching
            target_path = Path(target_pattern).resolve()
            try:
                file_path.relative_to(target_path)
                return True
            except ValueError:
                return False

    def save_state(self) -> None:
        """
        Manually save the current state to disk.

        This method can be called to force persistence even if auto_persist is disabled.
        """
        # Temporarily enable auto_persist to force save
        original_auto_persist = self.settings.knowledge_base_config.auto_persist
        self.settings.knowledge_base_config.auto_persist = True

        try:
            self._save_state()
            logger.info(f"Manually saved knowledge base state to {self.state_file_path}")
        finally:
            # Restore original setting
            self.settings.knowledge_base_config.auto_persist = original_auto_persist

    def clear_knowledge_base(self) -> None:
        """
        Clear all files from the knowledge base and remove the state file.

        Warning: This will permanently remove all data from the knowledge base.
        """
        try:
            # Clear the vector store by creating a new collection
            self.vector_store = self._initialize_vector_store()

            # Reinitialize the index
            self.index = VectorStoreIndex.from_vector_store(self.vector_store, embed_model=self.embed_model)

            # Clear added files
            self._added_files.clear()

            # Remove state file
            if self.state_file_path.exists():
                self.state_file_path.unlink()
                logger.info(f"Removed state file: {self.state_file_path}")

            logger.info("Knowledge base cleared successfully")

        except Exception as e:
            logger.error(f"Error clearing knowledge base: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary containing statistics
        """
        return {
            "kb_id": self.kb_id,
            "total_files": len(self._added_files),
            "persist_dir": self.persist_dir,
            "state_file": str(self.state_file_path),
            "auto_persist": self.settings.knowledge_base_config.auto_persist,
            "embedding_model": f"{self.settings.embedding_config.provider}:{self.settings.embedding_config.model}",
            "llm_model": f"{self.settings.llm_config.provider}:{self.settings.llm_config.model}",
        }


def knowledge_files_search(
    query: str,
    target_directories: list[str] = None,
    top_k: int = 5,
) -> str:
    """
    Find relevant knowledge files most relevant to the search query. This is a semantic search tool, so the query should ask for something semantically matching what is needed. If it makes sense to only search in particular directories, please specify them in the target_directories field. Unless there is a clear reason to use your own search query, please just reuse the user's exact query with their wording. Their exact wording/phrasing can often be helpful for the semantic search query. Keeping the same exact question format can also be helpful.
    """
    kb = FileKnowledgeBase()
    # If target_directories is a list, join with comma for compatibility
    if target_directories:
        # If only one string is provided, use it directly
        if isinstance(target_directories, str):
            target_pattern = target_directories
        elif isinstance(target_directories, list):
            # If list, join with comma or use the first element (llama-index tools expect a string pattern)
            target_pattern = target_directories[0] if len(target_directories) == 1 else ",".join(target_directories)
        else:
            target_pattern = None
    else:
        target_pattern = None
    return kb.query_with_response(query=query, top_k=top_k, target_directories=target_pattern)


def get_knowledge_files_search_tool() -> FunctionTool:
    """
    Returns a FunctionTool for semantic search over the knowledge base, matching the tool schema in Knowledge_Base_Design.md.
    """
    return FunctionTool.from_defaults(
        knowledge_files_search,
        name="knowledge_files_search",
        description=(
            "Find relevant knowledge files most relevant to the search query. "
            "This is a semantic search tool, so the query should ask for something semantically matching what is needed. "
            "If it makes sense to only search in particular directories, please specify them in the target_directories field. "
            "Unless there is a clear reason to use your own search query, please just reuse the user's exact query with their wording. "
            "Their exact wording/phrasing can often be helpful for the semantic search query. Keeping the same exact question format can also be helpful."
        ),
    )


# def main():
#     kb = FileKnowledgeBase()
#     kb.add_directory("/tmp/kb/knowledge/mysas")
#     kb.add_file("/tmp/kb/knowledge/user_preference.txt")
#     results = kb.search(
#         "What tables are related to ACH transactions?",
#         top_k=5,
#         target_directories="/tmp/kb/knowledge/mysas/business/",
#     )
#     print(results)
#     results = kb.search(
#         "What tables are related to ACH transactions?",
#         top_k=5,
#         target_directories="/tmp/kb/knowledge/mysas/**/*.md",
#     )
#     print(results)

# if __name__ == "__main__":
#     main()
