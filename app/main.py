from fastapi import FastAPI, Request
from app.schemas.input_schemas import UserInput
from app.services.agent_service import invoke_agent

app = FastAPI()

@app.post("/write")
async def chat(request: Request):
    data = await request.json()
    user_input = UserInput(**data)

    if not user_input.input:
        return {"error": "No input provided"}

    # Run the agent with the user input using AgentExecutor
    result = invoke_agent(user_input.dict())

    # Access the chat history directly from the result
    chat_history = result.get("chat_history", [])

    # Format the chat history into a structured JSON object
    formatted_history = []
    for message in chat_history:
        role = "AI" if message.type == "ai" else "User"
        formatted_history.append({
            "role": role,
            "content": message.content
        })

    return {
        "response": formatted_history
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)






""""
from fastapi import FastAPI, Request
from app.agents.agent import agent_executor


app = FastAPI()

@app.post("/write")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("input")

    if not user_input:
        return {"error": "No input provided"}

    # Run the agent with the user input using AgentExecutor
    result = agent_executor.invoke({"input": user_input})

    # Access the chat history directly from the result
    chat_history = result.get("chat_history", [])

    # Format the chat history
    formatted_history = []
    for message in chat_history:
        role = "AI" if message.type == "ai" else "User"
        formatted_history.append({
            "role": role,
            "content": message.content
        })

    return {
        "response": formatted_history
    }
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""