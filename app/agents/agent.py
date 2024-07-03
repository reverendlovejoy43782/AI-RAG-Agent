import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
from .tools import tools
import logging

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
    if responses:
        final_response = responses[-1]["agent"]["messages"]
        logging.debug(f"Final response: {final_response}")
    else:
        final_response = []

    # Extract chat history
    updated_chat_history = []
    for response in responses:
        messages = response.get("agent", {}).get("messages", [])
        updated_chat_history.extend(messages)

    logging.debug(f"Updated chat history: {updated_chat_history}")

    return {
        "messages": final_response,
        "chat_history": updated_chat_history
    }



"""
import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint import MemorySaver
from .tools import tools
import logging

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
    final_response = responses[-1]["messages"]
    updated_chat_history = memory.get_conversation("test-thread")["messages"]
    logging.debug(f"Updated chat history: {updated_chat_history}")

    return {
        "messages": final_response,
        "chat_history": updated_chat_history
    }



####


import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain.memory import ConversationBufferMemory
from .tools import tools
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# LOAD ENVIRONMENT VARIABLES START
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')
# LOAD ENVIRONMENT VARIABLES END

model = ChatOpenAI(temperature=0, model="gpt-4o")

# Define the agent with the model and tools
app = create_react_agent(model, tools=tools)

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

# Create a wrapper to use the agent with memory
def invoke_agent(input_data):
    chat_history = memory.chat_memory.messages if hasattr(memory, 'chat_memory') else []
    logging.debug(f"Input data: {input_data}")
    logging.debug(f"Chat history: {chat_history}")

    response = app.invoke({"messages": [{"type": "user", "content": input_data["input"]}], "chat_history": chat_history})
    logging.debug(f"Agent response: {response}")

    return response



####

import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.schema.agent import AgentFinish
from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from .tools import tools

# LOAD ENVIRONMENT VARIABLES START
load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')
# LOAD ENVIRONMENT VARIABLES END

functions = [format_tool_to_openai_function(f) for f in tools]
model = ChatOpenAI(temperature=0, model="gpt-4o").bind(functions=functions)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful but sassy assistant. For knowledge questions you search wikipedia. For current information you search the web."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
chain = prompt | model | OpenAIFunctionsAgentOutputParser()

# Define the agent_chain with RunnablePassthrough
agent_chain = RunnablePassthrough.assign(
    agent_scratchpad=lambda x: format_to_openai_functions(x["intermediate_steps"])
) | chain

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

# Create the AgentExecutor
agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True, memory=memory)


"""
