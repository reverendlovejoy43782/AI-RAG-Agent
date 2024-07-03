from app.agents.agent import agent_executor

def invoke_agent(input_data):
    return agent_executor.invoke({"input": input_data["input"]})