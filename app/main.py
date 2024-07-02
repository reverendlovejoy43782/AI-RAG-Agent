from fastapi import FastAPI, Request
from app.agent import run_agent

app = FastAPI()

@app.post("/write")
async def write_book(request: Request):
    data = await request.json()
    user_input = data.get("input")

    if not user_input:
        return {"error": "No input provided"}

    # Run the agent with the user input
    result = run_agent(user_input)

    return {
        "response": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



"""
from fastapi import FastAPI, Request
from app.agent import chain, search_wikipedia
from langchain.agents.format_scratchpad import format_to_openai_functions

app = FastAPI()

@app.post("/write")
async def write_book(request: Request):
    data = await request.json()
    user_input = data.get("input")
    agent_scratchpad = data.get("agent_scratchpad", [])

    if not user_input:
        return {"error": "No input provided"}

    # Invoke the chain with the user input and agent scratchpad
    result = chain.invoke({
        "input": user_input,
        "agent_scratchpad": agent_scratchpad
    })

    # Execute the search_wikipedia function with the tool_input
    observation = search_wikipedia(result.tool_input)

    # Format the scratchpad for the next invocation
    formatted_scratchpad = format_to_openai_functions([(result, observation)])

    # Re-invoke the chain with the formatted scratchpad and original input
    result1 = chain.invoke({
        "input": user_input,
        "agent_scratchpad": formatted_scratchpad
    })

    return {
        "response": result1
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""