import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import panel as pn
from llama_index.core.tools import FunctionTool

from resinkit.ai.agent import AgentManager
from resinkit.ai.tools.knowledge_base import get_rsk_kb_tool
from resinkit.ai.tools.list_sql_sources import create_list_sql_sources_tool
from resinkit.ai.tools.run_sql import create_sql_tool


class AIToolsUI:
    def __init__(self):
        pn.extension("tabulator", "ace")

        # Available tools mapping
        self.available_tools = {
            "list_sql_sources": create_list_sql_sources_tool(),
            "run_sql": create_sql_tool(
                "sqlite:///:memory:"
            ),  # Default in-memory SQLite for testing
            "knowledge_base": get_rsk_kb_tool(),
        }

        # Initialize agent manager
        self.agent_manager = AgentManager()

        # Available LLM models and their configuration
        self.available_llms = self.agent_manager.get_available_llms()

        # Initialize UI components
        self._init_components()

        # Layout the UI
        self.layout = self._create_layout()

    def _init_components(self):
        """Initialize UI components."""
        # Tool selection dropdown
        self.tool_select = pn.widgets.Select(
            name="Select Tool",
            value=list(self.available_tools.keys())[0]
            if self.available_tools
            else None,
            options=list(self.available_tools.keys()),
            width=300,
        )
        self.tool_select.param.watch(self._on_tool_changed, "value")

        # LLM model selection dropdown
        llm_options = (
            list(self.available_llms.keys())
            if self.available_llms
            else ["No LLMs available"]
        )
        self.llm_select = pn.widgets.Select(
            name="Select LLM Model",
            value=llm_options[0],
            options=llm_options,
            width=300,
        )

        # Tool info display
        self.tool_info = pn.pane.JSON(
            object={}, name="Tool Information", height=200, width=600
        )

        # System prompt input
        self.system_prompt = pn.widgets.TextAreaInput(
            name="System Prompt",
            value="",
            placeholder="Enter system prompt (optional)...",
            height=100,
            width=600,
        )

        # User message input
        self.user_message = pn.widgets.TextAreaInput(
            name="User Message",
            value="",
            placeholder="Enter your message here...",
            height=100,
            width=600,
        )

        # Execute button
        self.execute_btn = pn.widgets.Button(
            name="Execute Tool", button_type="primary", width=150
        )
        self.execute_btn.on_click(self._on_execute_clicked)

        # Results display
        self.results_display = pn.pane.JSON(
            object={"message": "No results yet"}, name="Results", height=400, width=600
        )

        # Status indicator
        self.status = pn.pane.HTML(
            "<div style='color: blue;'>Ready</div>", width=600, height=30
        )

        # Initialize tool info
        self._update_tool_info()

    def _on_tool_changed(self, event):
        """Handle tool selection change."""
        _ = event  # Unused parameter
        self._update_tool_info()

    def _update_tool_info(self):
        """Update tool information display."""
        if not self.tool_select.value:
            return

        tool = self.available_tools[self.tool_select.value]

        # Extract tool metadata
        info = {
            "name": tool.metadata.name,
            "description": tool.metadata.description,
            "parameters": {},
        }

        # Get function signature info
        if hasattr(tool.metadata, "fn_schema") and tool.metadata.fn_schema:
            schema = tool.metadata.fn_schema
            # Handle case where fn_schema might be a dict or a pydantic model
            if isinstance(schema, dict) and "properties" in schema:
                for param_name, param_info in schema["properties"].items():
                    info["parameters"][param_name] = {
                        "type": param_info.get("type", "unknown"),
                        "description": param_info.get("description", "No description"),
                    }
            elif hasattr(schema, "model_json_schema") and callable(
                schema.model_json_schema
            ):
                # Handle pydantic model case (Pydantic v2)
                try:
                    schema_dict = schema.model_json_schema()
                    if "properties" in schema_dict:
                        for param_name, param_info in schema_dict["properties"].items():
                            info["parameters"][param_name] = {
                                "type": param_info.get("type", "unknown"),
                                "description": param_info.get(
                                    "description", "No description"
                                ),
                            }
                except Exception:
                    # If schema extraction fails, just skip it
                    pass
            elif hasattr(schema, "schema") and callable(schema.schema):
                # Handle pydantic model case (Pydantic v1 - deprecated but still supported)
                try:
                    schema_dict = schema.schema()
                    if "properties" in schema_dict:
                        for param_name, param_info in schema_dict["properties"].items():
                            info["parameters"][param_name] = {
                                "type": param_info.get("type", "unknown"),
                                "description": param_info.get(
                                    "description", "No description"
                                ),
                            }
                except Exception:
                    # If schema extraction fails, just skip it
                    pass

        self.tool_info.object = info

    def _on_execute_clicked(self, event):
        """Handle execute button click."""
        _ = event  # Unused parameter
        if not self.tool_select.value:
            self._update_status("Error: Please select a tool", "error")
            return

        if not self.llm_select.value or self.llm_select.value == "No LLMs available":
            self._update_status(
                "Error: No LLM models available. Please set API keys for OpenAI, Anthropic, or Google.",
                "error",
            )
            return

        if not self.user_message.value.strip():
            self._update_status("Error: Please enter a user message", "error")
            return

        # Disable button during execution
        self.execute_btn.disabled = True

        try:
            # Run execution in async context
            self._run_async(self._execute_tool())
        except Exception as e:
            self._update_status(f"Error: {str(e)}", "error")
            self.execute_btn.disabled = False

    def _run_async(self, coro):
        """Helper to run async code."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in a Jupyter notebook or similar
                import nest_asyncio

                nest_asyncio.apply()
                # Schedule the coroutine to run
                future = asyncio.ensure_future(coro)
                return future
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(coro)

    async def _execute_tool(self):
        """Execute the selected tool with LLM."""
        try:
            self._update_status("Executing...", "info")

            # Get selected tool
            tool_name = self.tool_select.value

            # Create LLM for the tool if it's knowledge_base
            if tool_name == "knowledge_base":
                llm = self.agent_manager.create_llm(self.llm_select.value)
                tool = get_rsk_kb_tool(llm=llm)
            else:
                tool = self.available_tools[tool_name]

            # Prepare system prompt
            system_prompt = (
                self.system_prompt.value.strip()
                if self.system_prompt.value.strip()
                else ""
            )
            user_msg = self.user_message.value.strip()

            # Execute the agent using centralized creation
            response = await self.agent_manager.run_function_agent(
                query=user_msg,
                tools=[tool],
                model_name=self.llm_select.value,
                system_prompt=system_prompt,
                verbose=True,
            )

            # Display results
            result = {"response": str(response), "tool_calls": [], "sources": []}

            # Note: FunctionAgent doesn't expose chat_history like ReActAgent
            # For now, we'll create a simple tool call entry

            # Extract source nodes if available
            if hasattr(response, "source_nodes") and response.source_nodes:
                for node in response.source_nodes:
                    if hasattr(node, "metadata"):
                        result["sources"].append(node.metadata)

            # Create a manual entry based on the tool used
            if self.tool_select.value:
                result["tool_calls"].append(
                    {
                        "tool_name": self.tool_select.value,
                        "arguments": "{}",  # No specific arguments captured
                        "call_id": "function_agent_call",
                        "note": "Tool executed via FunctionAgent",
                    }
                )

            self.results_display.object = result
            self._update_status("Execution completed successfully", "success")

        except Exception as e:
            import traceback

            error_result = {
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
            self.results_display.object = error_result
            self._update_status(f"Error: {str(e)}", "error")

        finally:
            # Always re-enable the button
            self.execute_btn.disabled = False

    def _update_status(self, message: str, status_type: str = "info"):
        """Update status display."""
        colors = {
            "info": "blue",
            "success": "green",
            "error": "red",
            "warning": "orange",
        }
        color = colors.get(status_type, "blue")
        self.status.object = f"<div style='color: {color};'>{message}</div>"

    def _create_layout(self):
        """Create the UI layout."""
        return pn.Column(
            pn.pane.HTML("<h2>AI Tools Testing Interface</h2>"),
            # Tool and model selection
            pn.Row(
                self.tool_select,
                self.llm_select,
            ),
            # Tool information
            self.tool_info,
            # Input areas
            self.system_prompt,
            self.user_message,
            # Execute button and status
            pn.Row(
                self.execute_btn,
                self.status,
            ),
            # Results display
            self.results_display,
            width=800,
            margin=(10, 10),
        )

    def show(self):
        """Display the UI."""
        return self.layout


def show_ai_tools_ui():
    """Show the AI tools testing UI."""
    ui = AIToolsUI()
    return ui.show()
