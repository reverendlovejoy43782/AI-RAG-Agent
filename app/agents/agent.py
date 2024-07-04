import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
from .tools import tools
import logging
from langchain_core.messages import AIMessage, HumanMessage

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# LOAD ENVIRONMENT VARIABLES START
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')
# LOAD ENVIRONMENT VARIABLES END

model = ChatOpenAI(temperature=0, model="gpt-4o")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        ("placeholder", "{messages}"),
    ]
)

def _modify_messages(messages):
    return prompt.invoke({"messages": messages}).to_messages()

# Define the agent with the model and tools, and add a checkpointer for memory
memory = MemorySaver()
app = create_react_agent(model, tools, messages_modifier=_modify_messages, checkpointer=memory)

# Create a wrapper to use the agent with memory and iteration
def invoke_agent(input_data):

    ###

    # Retrieve the chat history

    # Configuration for memory session
    config = {"configurable": {"thread_id": "test-thread"}}
    


    # Retrieve the chat history
    chat_history_data = memory.get(config)
    if chat_history_data is None:
        chat_history_data = {"channel_values": {"messages": []}}
    elif "channel_values" not in chat_history_data:
        chat_history_data["channel_values"] = {"messages": []}
    logging.debug(f"Initial chat history: {chat_history_data}")

    # Extract the messages list
    chat_history = chat_history_data["channel_values"]["messages"]

    # Add the current user input to the chat history
    chat_history.append(HumanMessage(content=input_data["input"]))


    logging.debug(f"Apended chat history: {chat_history}")
    ###

    # Log input data
    logging.debug(f"Input data: {input_data}")

    # Prepare the input for the agent
    agent_input = {
        "messages": [("human", input_data["input"])]
    }
    logging.debug(f"Agent input: {agent_input}")

    # Configuration for memory session
    config = {"configurable": {"thread_id": "test-thread"}}

    # Invoke the agent with the input and memory using stream method
    responses = []
    for step in app.stream(agent_input, config=config, stream_mode="updates"):
        logging.debug(f"Agent step: {step}")
        responses.append(step)

    # Extract the final response and chat history from responses
    final_response = []

    for response in responses:
        messages = response.get("agent", {}).get("messages", [])
        for message in messages:
            if message.content:  # Exclude empty messages
                final_response.append(message)
                chat_history.append(message)


    logging.debug(f"Final response: {final_response}")
    logging.debug(f"Updated chat history: {chat_history}")

    return {
        "messages": final_response,
        "chat_history": chat_history
    }