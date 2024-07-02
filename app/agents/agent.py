import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI
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
model = ChatOpenAI(temperature=0).bind(functions=functions)
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

# Define the run_agent function
def run_agent(user_input):
    intermediate_steps = []
    while True:
        result = chain.invoke({
            "input": user_input,
            "agent_scratchpad": format_to_openai_functions(intermediate_steps)
        })
        if isinstance(result, AgentFinish):
            return result
        tool = {
            "search_wikipedia": search_wikipedia,
            "search_web": search_tavily
        }[result.tool]
        observation = tool.run(result.tool_input)
        intermediate_steps.append((result, observation))

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

# Create the AgentExecutor
agent_executor = AgentExecutor(agent=agent_chain, tools=tools, verbose=True, memory=memory)