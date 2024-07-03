from app.agents.agent import invoke_agent

def invoke_agent_service(input_data):
    return invoke_agent(input_data)


"""
from app.agents.agent import agent_executor

def invoke_agent(input_data):
    return agent_executor.invoke({"input": input_data["input"]})
"""