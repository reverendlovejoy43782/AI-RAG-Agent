from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.agents.agent import invoke_agent
from app.schemas.input_schemas import UserInput
import logging
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

app = FastAPI()

@app.post("/write")
async def chat(request: Request):
    data = await request.json()
    user_input = UserInput(**data)
    print(f"DATA: {data}")
    print(f"USER INPUT: {user_input}")


    if not user_input.input:
        return {"error": "No input provided"}

    # Get the stream from the agent
    stream = invoke_agent(user_input.dict())

    # Aggregate the response
    formatted_response = []
    message_ids = set()  # Set to keep track of message IDs

    for step in stream:
        messages = step.get("messages", [])
        for message in messages:
            if message.id in message_ids:
                continue  # Skip already processed messages
            message_ids.add(message.id)

            if isinstance(message, AIMessage):
                if "tool_calls" in message.additional_kwargs:
                    if message.content:
                        formatted_response.append({
                            "type": "AI Reasoning",
                            "content": message.content,
                        })
                    for tool_call in message.additional_kwargs["tool_calls"]:
                        if not message.content:
                            # Deduce reasoning from tool calls
                            tool_reasoning = f"Decided to call the tool {tool_call['function']['name']} with arguments {tool_call['function']['arguments']}."
                            formatted_response.append({
                                "type": "AI Reasoning",
                                "content": tool_reasoning,
                            })
                        formatted_response.append({
                            "type": "AI Action",
                            "tool_name": tool_call["function"]["name"],
                            "tool_args": tool_call["function"]["arguments"],
                        })
                else:
                    if message.content:
                        formatted_response.append({
                            "type": "AI Reasoning",
                            "content": message.content,
                        })
            elif isinstance(message, ToolMessage):
                truncated_content = (message.content[:100] + '...') if len(message.content) > 100 else message.content
                formatted_response.append({
                    "type": "Tool Response",
                    "tool_name": message.name,
                    "tool_call_id": message.tool_call_id,
                    "content": truncated_content,
                })
            elif isinstance(message, HumanMessage):
                formatted_response.append({
                    "type": "User Message",
                    "content": message.content,
                })

    return JSONResponse(content={"response": formatted_response})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)