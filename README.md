# ReAct Agent Langchain Langgraph

This template sets up a basic ReAct Agent with Langchain and Langgraph. The agent uses Wikipedia and web search as tools.

## Frameworks and Libraries

- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **LangChain**: A framework for developing applications powered by language models.
- **LangSmith**: A framework for fine-tuning and deploying language models.

## Code Structure

- **app/config.py**: Loads environment variables and configurations.
- **app/schemas/input_schemas.py**: Defines the input schemas using Pydantic.
- **app/schemas/tool_schemas.py**: Defines the tool-specific input schemas using Pydantic.
- **app/agents/tools.py**: Defines the tools (search functions) and their decorators.
- **app/agents/agent.py**: Defines the agent and agent executor.
- **app/services/agent_service.py**: Contains the service to handle agent logic.
- **app/main.py**: Defines the FastAPI app and endpoints.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

   