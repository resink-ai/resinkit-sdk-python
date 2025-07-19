"""
SQL Generator Workflow - A sophisticated text-to-SQL AI agent using LlamaIndex Workflows.

This workflow follows the design pattern:
1. User query → Build comprehensive prompt with templates
2. Discovery phase → Explore data sources and schemas
3. Planning phase → Create execution plan
4. Execution phase → Generate and validate SQL
5. Presentation phase → Format and present results

Supports MCP server integration for extensible tool calling.
"""

import logging
from typing import Any, Dict, List, Optional

from llama_index.core.base.llms.base import BaseLLM
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

from resinkit.ai.agent import AgentManager
from resinkit.ai.tools.resinkit_api_tools import get_resinkit_api_tools

from .mcp_defaults import create_mcp_manager_with_defaults

# Configure logging
logger = logging.getLogger(__name__)


class QueryAnalysisEvent(Event):
    """Event triggered after initial query analysis."""

    user_query: str
    analysis: Dict[str, Any]


class DiscoveryEvent(Event):
    """Event triggered after data source discovery."""

    sources: List[Dict[str, Any]]
    schemas: List[Dict[str, Any]]


class PlanningEvent(Event):
    """Event triggered after execution planning."""

    plan: Dict[str, Any]
    steps: List[Dict[str, Any]]


class ExecutionEvent(Event):
    """Event triggered after SQL execution."""

    sql_query: str
    results: Optional[Dict[str, Any]]
    execution_details: Dict[str, Any]


class PresentationEvent(Event):
    """Event triggered for final result presentation."""

    final_sql: str
    explanation: str
    results_summary: Optional[str]


class SqlGeneratorWorkflow(Workflow):
    """
    SQL Generator Workflow using LlamaIndex Workflows.

    This workflow implements a sophisticated text-to-SQL generation process
    with discovery, planning, execution, and presentation phases.
    """

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        tools: Optional[List[FunctionTool]] = None,
        mcp_config: Optional[Dict[str, Any]] = None,
        enable_mcp: bool = True,
        verbose: bool = True,
        timeout: float = 300.0,
    ):
        """
        Initialize the SQL Generator Workflow.

        Args:
            llm: LLM instance to use for the workflow
            tools: Additional tools beyond the default ones
            mcp_config: MCP server configuration
            enable_mcp: Whether to enable MCP integration
            verbose: Enable verbose logging
            timeout: Workflow timeout in seconds
        """
        super().__init__(timeout=timeout, verbose=verbose)

        # Initialize agent manager for LLM creation
        self.agent_manager = AgentManager()
        self.llm = llm or self.agent_manager.get_llm()

        # Initialize MCP manager
        self.mcp_manager = None
        self.enable_mcp = enable_mcp
        self.mcp_config = mcp_config or {}

        # Initialize default tools
        api_tools = get_resinkit_api_tools()
        default_tools = api_tools.get_all_tools()

        # Add any additional tools
        self.tools = default_tools + (tools or [])

        # Initialize prompt templates
        self._init_templates()

    async def _initialize_mcp(self) -> None:
        """Initialize MCP integration and load tools."""
        if not self.enable_mcp:
            logger.info("MCP integration is disabled")
            return

        try:
            # Create MCP manager
            self.mcp_manager = await create_mcp_manager_with_defaults(
                verbose=self.verbose
            )

            # Initialize from custom config if provided
            if self.mcp_config:
                await self.mcp_manager.initialize_from_config(self.mcp_config)
            else:
                # Connect to default servers (if any are enabled)
                await self.mcp_manager.connect_all_servers()
                await self.mcp_manager.load_all_tools()

            # Add MCP tools to the workflow tools
            mcp_tools = self.mcp_manager.get_all_tools()
            self.tools.extend(mcp_tools)

            if self.verbose and mcp_tools:
                logger.info(f"Added {len(mcp_tools)} tools from MCP servers")

        except Exception as e:
            logger.warning(f"Failed to initialize MCP integration: {e}")
            self.mcp_manager = None

    async def _cleanup_mcp(self) -> None:
        """Clean up MCP connections."""
        if self.mcp_manager:
            try:
                await self.mcp_manager.disconnect_all_servers()
                if self.verbose:
                    logger.info("MCP connections cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up MCP connections: {e}")

    async def get_available_tools(self) -> List[FunctionTool]:
        """
        Get all available tools including MCP tools.

        Returns:
            List of all available tools
        """
        # Ensure MCP is initialized
        if self.enable_mcp and self.mcp_manager is None:
            await self._initialize_mcp()

        return self.tools.copy()

    def _init_templates(self):
        """Initialize prompt templates for different phases."""

        self.query_analysis_template = """
You are a proficient data scientist, specializing in converting natural language queries into accurate SQL statements and managing database operations.

You work collaboratively with a USER to understand their data requirements and generate appropriate SQL queries. Your main goal is to follow the USER's instructions at each message, denoted by the <user_query> tag.

<tool_calling>
You have access to specialized database and SQL tools. Use them to:
1. Explore available data sources and understand database schemas
2. Search for relevant documentation and business context
3. Execute SQL queries to validate and test your approach
4. Present results in a clear, structured format

IMPORTANT: Always use parallel tool calls when possible to maximize efficiency.
</tool_calling>

<search_and_discovery>
Before generating SQL, thoroughly explore the available data sources:
1. List available SQL data sources to understand what databases are available
2. Examine table schemas and relationships
3. Search for documentation or business context that might inform the query
4. Consider data types, constraints, and potential edge cases
</search_and_discovery>

<user_query>
{user_query}
</user_query>

Based on this query, analyze what information you need to discover before generating SQL. Plan your discovery approach and identify what tools you'll need to call.

Please respond with:
1. Your analysis of the user's request
2. What data sources and schemas you need to explore
3. Any additional context or business logic you need to understand
"""

        self.discovery_template = """
Based on your analysis, now perform the discovery phase. Use the available tools to:

1. **List Data Sources**: Discover what SQL databases are available
2. **Explore Schemas**: Examine table structures, columns, and relationships 
3. **Search Context**: Look for relevant documentation or business context

User Query: {user_query}
Your Analysis: {analysis}

Execute the necessary discovery steps using parallel tool calls where possible.
"""

        self.planning_template = """
Now that you have discovered the available data sources and schemas, create a detailed execution plan for generating the SQL query.

User Query: {user_query}
Available Sources: {sources}
Schema Information: {schemas}

Create a plan that includes:
1. **Target Tables**: Which tables you'll query
2. **Join Strategy**: How you'll join tables if needed
3. **Filter Logic**: What WHERE conditions you'll apply
4. **Aggregation**: Any GROUP BY, ORDER BY, or window functions needed
5. **Validation**: How you'll test and validate the query

Provide a step-by-step plan for SQL generation.
"""

        self.execution_template = """
Execute your plan to generate the final SQL query.

User Query: {user_query}
Execution Plan: {plan}
Available Sources: {sources}

Generate the complete, executable SQL query. If possible, test it using the SQL execution tools to validate syntax and logic.

Provide:
1. The complete SQL query
2. Explanation of the approach
3. Any validation results if you tested the query
"""

        self.presentation_template = """
Present the final SQL query and results in a clear, professional format.

User Query: {user_query}
Generated SQL: {sql_query}
Execution Results: {results}

Provide:
1. **Complete SQL Query**: Well-formatted, commented SQL
2. **Query Explanation**: Clear explanation of the approach and logic
3. **Key Features**: Highlight important aspects of the query
4. **Results Summary**: If available, summarize the query results
"""

    @step
    async def analyze_query(self, ctx: Context, ev: StartEvent) -> QueryAnalysisEvent:
        """
        Step 1: Analyze the user query to understand requirements.
        """
        logger.info("Starting query analysis phase")

        user_query = ev.get("query", "")
        if not user_query:
            raise ValueError("No query provided in StartEvent")

        # Store the original query in context
        await ctx.set("original_query", user_query)

        # Create agent for analysis
        agent = self.agent_manager.create_function_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt="You are a SQL expert analyzing user queries for data requirements.",
            verbose=True,
        )

        # Analyze the query
        analysis_prompt = self.query_analysis_template.format(user_query=user_query)

        try:
            handler = agent.run(user_msg=analysis_prompt)
            analysis_result = await handler

            # Extract analysis from the response
            analysis = {
                "query": user_query,
                "response": str(analysis_result),
                "requires_discovery": True,
                "complexity": "medium",  # Could be enhanced with complexity analysis
            }

            logger.info(f"Query analysis completed: {analysis}")
            return QueryAnalysisEvent(user_query=user_query, analysis=analysis)

        except Exception as e:
            logger.error(f"Error in query analysis: {e}")
            # Provide fallback analysis
            analysis = {
                "query": user_query,
                "response": f"Analysis failed: {e}",
                "requires_discovery": True,
                "complexity": "unknown",
            }
            return QueryAnalysisEvent(user_query=user_query, analysis=analysis)

    @step
    async def discover_sources(
        self, ctx: Context, ev: QueryAnalysisEvent
    ) -> DiscoveryEvent:
        """
        Step 2: Discover available data sources and schemas.
        """
        logger.info("Starting discovery phase")

        # Create agent for discovery
        agent = self.agent_manager.create_function_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt="You are a database explorer discovering schemas and data sources.",
            verbose=True,
        )

        # Perform discovery
        discovery_prompt = self.discovery_template.format(
            user_query=ev.user_query, analysis=ev.analysis
        )

        try:
            handler = agent.run(user_msg=discovery_prompt)
            discovery_result = await handler

            # Store discovery results (in real implementation, would parse structured data)
            sources = [{"discovery_response": str(discovery_result)}]
            schemas = [{"schema_info": "extracted from discovery"}]

            await ctx.set("discovery_result", discovery_result)
            logger.info("Discovery phase completed")

            return DiscoveryEvent(sources=sources, schemas=schemas)

        except Exception as e:
            logger.error(f"Error in discovery phase: {e}")
            # Provide fallback discovery
            return DiscoveryEvent(
                sources=[{"error": str(e)}], schemas=[{"error": str(e)}]
            )

    @step
    async def create_plan(self, ctx: Context, ev: DiscoveryEvent) -> PlanningEvent:
        """
        Step 3: Create execution plan based on discovered sources.
        """
        logger.info("Starting planning phase")

        # Get original query from context
        original_query = await ctx.get("original_query", default="")

        # Create agent for planning
        agent = self.agent_manager.create_function_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt="You are a SQL architect creating detailed execution plans.",
            verbose=True,
        )

        # Create execution plan
        planning_prompt = self.planning_template.format(
            user_query=original_query, sources=ev.sources, schemas=ev.schemas
        )

        try:
            handler = agent.run(user_msg=planning_prompt)
            planning_result = await handler

            # Create plan structure
            plan = {
                "approach": str(planning_result),
                "complexity": "medium",
                "estimated_tables": len(ev.sources),
            }

            steps = [
                {
                    "step": 1,
                    "action": "Generate SQL",
                    "description": "Create the SQL query",
                },
                {
                    "step": 2,
                    "action": "Validate",
                    "description": "Test the query if possible",
                },
                {"step": 3, "action": "Present", "description": "Format final results"},
            ]

            await ctx.set("plan", plan)
            logger.info("Planning phase completed")

            return PlanningEvent(plan=plan, steps=steps)

        except Exception as e:
            logger.error(f"Error in planning phase: {e}")
            # Provide fallback plan
            return PlanningEvent(
                plan={"error": str(e)},
                steps=[{"step": 1, "action": "Generate SQL", "error": str(e)}],
            )

    @step
    async def execute_plan(self, ctx: Context, ev: PlanningEvent) -> ExecutionEvent:
        """
        Step 4: Execute the plan to generate SQL.
        """
        logger.info("Starting execution phase")

        # Get stored context
        original_query = await ctx.get("original_query", default="")
        discovery_result = await ctx.get("discovery_result", default="")

        # Create agent for execution
        agent = self.agent_manager.create_function_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt="You are a SQL generator creating optimized, executable queries.",
            verbose=True,
        )

        # Generate SQL
        execution_prompt = self.execution_template.format(
            user_query=original_query, plan=ev.plan, sources=discovery_result
        )

        try:
            handler = agent.run(user_msg=execution_prompt)
            execution_result = await handler

            # Extract SQL from response (in real implementation, would parse more carefully)
            sql_query = str(execution_result)

            # Store execution details
            execution_details = {
                "generated_at": "workflow_execution",
                "method": "llm_generation",
                "validated": False,  # Could add validation step
            }

            await ctx.set("sql_query", sql_query)
            await ctx.set("execution_result", execution_result)
            logger.info("Execution phase completed")

            return ExecutionEvent(
                sql_query=sql_query,
                results=None,  # Would contain actual execution results
                execution_details=execution_details,
            )

        except Exception as e:
            logger.error(f"Error in execution phase: {e}")
            return ExecutionEvent(
                sql_query="-- Error generating SQL",
                results=None,
                execution_details={"error": str(e)},
            )

    @step
    async def present_results(self, ctx: Context, ev: ExecutionEvent) -> StopEvent:
        """
        Step 5: Present the final results in a structured format.
        """
        logger.info("Starting presentation phase")

        # Get stored context
        original_query = await ctx.get("original_query", default="")

        # Create agent for presentation
        agent = self.agent_manager.create_function_agent(
            tools=self.tools,
            llm=self.llm,
            system_prompt="You are a technical writer presenting SQL results clearly.",
            verbose=True,
        )

        # Create presentation
        presentation_prompt = self.presentation_template.format(
            user_query=original_query,
            sql_query=ev.sql_query,
            results=ev.results or "No execution results available",
        )

        try:
            handler = agent.run(user_msg=presentation_prompt)
            presentation_result = await handler

            # Create final result structure
            final_result = {
                "user_query": original_query,
                "generated_sql": ev.sql_query,
                "explanation": str(presentation_result),
                "execution_details": ev.execution_details,
                "workflow_completed": True,
            }

            logger.info("Presentation phase completed")
            return StopEvent(result=final_result)

        except Exception as e:
            logger.error(f"Error in presentation phase: {e}")
            # Return basic result even if presentation fails
            return StopEvent(
                result={
                    "user_query": original_query,
                    "generated_sql": ev.sql_query,
                    "explanation": f"Presentation failed: {e}",
                    "execution_details": ev.execution_details,
                    "workflow_completed": False,
                }
            )

    async def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Run the complete SQL generation workflow.

        Args:
            query: Natural language query to convert to SQL
            **kwargs: Additional parameters

        Returns:
            Dict containing the generated SQL and explanation
        """
        logger.info(f"Starting SQL generation workflow for query: {query}")

        try:
            # Initialize MCP integration if enabled
            if self.enable_mcp and self.mcp_manager is None:
                await self._initialize_mcp()

            # Run the workflow
            result = await super().run(query=query, **kwargs)

            logger.info("SQL generation workflow completed successfully")
            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "user_query": query,
                "generated_sql": "-- Error: Workflow execution failed",
                "explanation": f"The SQL generation workflow encountered an error: {e}",
                "execution_details": {"error": str(e)},
                "workflow_completed": False,
            }
        finally:
            # Clean up MCP connections
            await self._cleanup_mcp()


# Helper functions for external usage


async def generate_sql_with_workflow(
    query: str,
    llm: Optional[BaseLLM] = None,
    tools: Optional[List[FunctionTool]] = None,
    mcp_config: Optional[Dict[str, Any]] = None,
    enable_mcp: bool = True,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to generate SQL using the workflow.

    Args:
        query: Natural language query
        llm: Optional LLM instance
        tools: Optional additional tools
        mcp_config: Optional MCP server configuration
        enable_mcp: Whether to enable MCP integration
        verbose: Enable verbose logging

    Returns:
        Dict containing generated SQL and explanation
    """
    workflow = SqlGeneratorWorkflow(
        llm=llm,
        tools=tools,
        mcp_config=mcp_config,
        enable_mcp=enable_mcp,
        verbose=verbose,
    )
    return await workflow.run(query)


# Example usage function for testing
async def example_usage():
    """Example usage of the SQL Generator Workflow."""

    # Example queries
    queries = [
        "What were the total sales for each product category in the last quarter?",
        "Find the top 10 customers by order value this year",
        "Show me the monthly revenue trend for the past 6 months",
    ]

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("=" * 60)

        try:
            result = await generate_sql_with_workflow(query, verbose=True)

            print("\nGenerated SQL:")
            print(result.get("generated_sql", "No SQL generated"))
            print("\nExplanation:")
            print(result.get("explanation", "No explanation available"))

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
