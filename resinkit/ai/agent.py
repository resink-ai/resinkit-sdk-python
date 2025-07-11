from llama_index.core.agent import AgentWorkflow
from llama_index.llms.openai import OpenAI
from resinkit.ai.prompt import SQL_GENERATION_SYSTEM_PROMPT

# 1. Collect all defined tools
all_tools = []

# 2. Initialize the LLM
llm = OpenAI(model="gpt-4o")

# 3. Create the AgentWorkflow
workflow = AgentWorkflow.from_tools(
    tools=all_tools,
    llm=llm,
    verbose=True,  # Set to True to see the agent's reasoning
    system_prompt=SQL_GENERATION_SYSTEM_PROMPT,
)

# 4. Run the workflow with a user query
user_query = "What were the total sales for each product category in the last quarter?"
response = workflow.run(user_query)

print(response)
