## Key Features

1. Adding Files to Knowledge Base:

- add_file(file_path) - Add individual files
- add_directory(directory_path) - Add all files from a directory
- Supports multiple formats: PDF, DOCX, TXT, MD, CSV, JSON
- Automatically chunks documents for optimal retrieval

2. Semantic Search:

search(query, top_k) - Returns raw search results with scores
query_with_response(query) - Returns AI-generated response based on search
Uses vector embeddings for semantic similarity matching


3. Misc requirements:
- Embedding model should be configurable: By default let's use google genimi embedding model, but other embedding model can be used if configured in core/settings.py
- Let's use llama-index and related packages to manage the embeddings and LLM calls.


## Quick Start Example

```python
# Initialize knowledge base
kb = FileKnowledgeBase()

# Add your files
kb.add_directory("/tmp/kb/knowledge/mysas")
kb.add_file("./tmp/kb/knowledge/mysas/user_preference.txt")

# Search for relevant content
results = kb.search("What tables are related to ACH transactions?", top_k=5, target_directories="/tmp/kb/knowledge/mysas/business/")

# Search with path glob pattern
results = kb.search("What tables are related to ACH transactions?", top_k=5, target_directories="/tmp/kb/knowledge/mysas/**/*.md")
```
