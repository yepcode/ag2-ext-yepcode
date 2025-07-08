from autogen import ConversableAgent, LLMConfig
from ag2_ext_yepcode import YepCodeCodeExecutor
from dotenv import load_dotenv
import os

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize YepCode executor
yepcode_executor = YepCodeCodeExecutor(
    timeout=120,
    remove_on_done=False,
    sync_execution=True,
)

# Create an agent with code executor configuration.
code_executor_agent = ConversableAgent(
    "code_executor_agent",
    llm_config=False,  # Turn off LLM for this agent.
    code_execution_config={
        "executor": yepcode_executor
    },  # Use the local command line code executor.
    human_input_mode="ALWAYS",  # Always take human input for this agent for safety.
)

task = """Run this code:
```python
message = "Hello, world!"
print(message)
return message
```

and return the output.
"""

# Generate a reply for the given code.
reply = code_executor_agent.generate_reply(messages=[{"role": "user", "content": task}])
print(reply)
