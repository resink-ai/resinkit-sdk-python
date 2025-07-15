# AI Tools UI

Implement an panel bsed UI for quick AI tools testing. UI elements and User flow is described blow:

1. On the UI, there is a dropdown allowing user to select the tool to test. This list in the dropdown are hard coded based on the enabled tools under resinkit/ai/tools.
2. On the UI, there is also a drop down list allowing users to select corresponding LLM model to power the tool. The list shows the popular public available LLM modes from OpenAI, Anthropic or Google Gemini, and the drop only shows the models whose corresponding API key env variable is provided. For example "models/gemini-1.5-flash" is in the list, because
   - env `GOOGLE_API_KEY` exists in os.environ and is not empty.
   - "models/gemini-1.5-flash" can directly be used to create a models like
    `llm = Gemini(model="models/gemini-1.5-flash")`
3. The UI also provide a UI to view the tool meta info, like name, description and paramters schema.
4. On the UI, there are two input boxes.
   1. The first one is for adding system prompt. By default the system input will be ""
   2. The second input box is for adding user message, which starts with empty string.
5. The UI also has a button allow calling LLM with user message which can trigger the tool Call and display the returned response.


