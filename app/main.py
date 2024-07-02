from fastapi import FastAPI, Request
from app.agent import agent_executor

app = FastAPI()

@app.post("/write")
async def write_book(request: Request):
    data = await request.json()
    user_input = data.get("input")

    if not user_input:
        return {"error": "No input provided"}

    # Run the agent with the user input using AgentExecutor
    result = agent_executor.invoke({"input": user_input})

    return {
        "response": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)