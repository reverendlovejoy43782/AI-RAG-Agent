import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
from .tools import tools
import logging
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
import json


# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load environment variables
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize the model and memory
model = ChatOpenAI(temperature=0, model="gpt-4o")
memory = MemorySaver()


    

def inspect_memory(memory, config):

    print(f"MEMORY: {memory}")

     # Print attributes and methods of the memory object
    print("Attributes and Methods of MemorySaver:")
    print(dir(memory))
    
    # Print the __dict__ attribute if it exists
    #if hasattr(memory, '__dict__'):
        #print("MemorySaver __dict__ attribute:")
        #print(vars(memory))
    
    # Print the storage attribute
    #print("MemorySaver storage attribute:")
    #print(memory.storage)

    storage = memory.storage
    thread_id = config['configurable']['thread_id']
    thread_storage = storage.get(thread_id, {})

    for key, value in thread_storage.items():
        try:
            for data_pair in value:
                print(f"DATA PAIR: {data_pair}")
                deserialized_value = json.loads(data_pair.decode('utf-8'))
                print(f"DESERIALIZED VALUE: {deserialized_value}")
                # LOOP TO PRINT CONTENT OF TOOL MESSAGE HERE
                if 'channel_values' in deserialized_value and 'messages' in deserialized_value['channel_values']:
                    for msg in deserialized_value['channel_values']['messages']:
                        if isinstance(msg, dict) and msg.get("type") == "constructor" and 'ToolMessage' in msg.get('id', []):
                            print(f"Tool Message Content: {msg.get('kwargs', {}).get('content')}")
        except Exception as e:
            logging.error(f"Error processing memory entry {key}: {e}")



###


def remove_memory(memory, config):
    storage = memory.storage
    thread_id = config['configurable']['thread_id']
    thread_storage = storage.get(thread_id, {})

    # Collect all tool call ids
    tool_call_entries = []
    for key, value in thread_storage.items():
        try:
            for data_pair in value:
                deserialized_value = json.loads(data_pair.decode('utf-8'))
                if 'channel_values' in deserialized_value and 'messages' in deserialized_value['channel_values']:
                    for msg in deserialized_value['channel_values']['messages']:
                        if isinstance(msg, dict) and msg.get("type") == "constructor" and 'ToolMessage' in msg.get('id', []):
                            tool_call_id = msg.get('kwargs', {}).get('tool_call_id')
                            if tool_call_id:
                                tool_call_entries.append((tool_call_id, msg.get('id')))
        except Exception as e:
            logging.error(f"Error processing memory entry {key}: {e}")

    if not tool_call_entries:
        return

    # Find the latest tool call entry based on tool call id
    latest_tool_call_entry = max(tool_call_entries, key=lambda entry: entry[1])
    print(f"LATEST TOOL CALL ENTRY: {latest_tool_call_entry}")

    # Remove tool message content from past iterations
    for key, value in thread_storage.items():
        try:
            for data_pair in value:
                deserialized_value = json.loads(data_pair.decode('utf-8'))
                if 'channel_values' in deserialized_value and 'messages' in deserialized_value['channel_values']:
                    for msg in deserialized_value['channel_values']['messages']:
                        if isinstance(msg, dict) and msg.get("type") == "constructor" and 'ToolMessage' in msg.get('id', []):
                            tool_call_id = msg.get('kwargs', {}).get('tool_call_id')
                            print(f"TOOL CALL ID: {tool_call_id}")
                            if tool_call_id and tool_call_id != latest_tool_call_entry[0]:
                                msg['kwargs']['content'] = ''
                data_pair = (json.dumps(deserialized_value).encode('utf-8'), data_pair[1])
        except Exception as e:
            logging.error(f"Error processing memory entry {key}: {e}")

    print(f"THREAD STORAGE: {thread_storage}")
    memory.storage[thread_id] = thread_storage

# Create the agent
app = create_react_agent(model, tools=tools, checkpointer=memory)

def invoke_agent(input_data):
    # Configuration for memory session
    config = {"configurable": {"thread_id": "test-thread"}}

    # Inspect memory before invoking agent
    inspect_memory(memory, config)

    # Remove past iteration tool messages
    remove_memory(memory, config)

    # Define the system message
    system_message = (
        "system", 
        "You are an AI assistant. If you get a question regarding up-to-date information and current events, use the tool search_tavily. "
        "If a question is about knowledge, history, and past information, use the tool search_wikipedia. "
        "If the question is about both, use both tools. "
        "Ask follow-up questions if it is not clear to you what tool to use."
    )

    # Prepare the input for the agent
    agent_input = {
        "messages": [system_message, ("user", input_data["input"])]
    }

    # Invoke the agent with the input and memory using stream method
    return app.stream(agent_input, config=config, stream_mode="values")
