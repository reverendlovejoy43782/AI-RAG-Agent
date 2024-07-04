import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
from .tools import tools
import logging
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize the model and memory
model = ChatOpenAI(temperature=0, model="gpt-4o")
memory = MemorySaver()

# Create the agent
app = create_react_agent(model, tools=tools, checkpointer=memory)

def invoke_agent(input_data):
    # Configuration for memory session
    config = {"configurable": {"thread_id": "test-thread"}}
    
    # Prepare the input for the agent
    agent_input = {
        "messages": [("user", input_data["input"])]
    }


    # Invoke the agent with the input and memory using stream method
    #stream = app.stream(agent_input, config=config, stream_mode="values")

    


    #return stream

    # Invoke the agent with the input and memory using stream method
    return app.stream(agent_input, config=config, stream_mode="values")
