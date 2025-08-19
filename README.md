![YepCode Run SDK Preview](https://yepcode.io/images/cover/yepcode-ultimate-dev-tool-ai-solutions.png)

<div align="center">

[![PyPI Version](https://img.shields.io/pypi/v/ag2-ext-yepcode)](https://pypi.org/project/ag2-ext-yepcode/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/ag2-ext-yepcode)](https://pypi.org/project/ag2-ext-yepcode/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/yepcode/ag2-ext-yepcode-py/ci.yml)](https://github.com/yepcode/ag2-ext-yepcode-py/actions)

</div>

# AG2 Extension for YepCode

An [AG2](https://ag2.ai/) (formerly AutoGen) extension that enables secure code execution using [YepCode's](https://yepcode.io/) serverless runtime environment. Execute Python and JavaScript code in production-grade, isolated sandboxes with built-in security and scalability.

> **Note**: AG2 was evolved from AutoGen. If you are looking for the extension for AutoGen, please check the [autogen-ext-yepcode](https://github.com/yepcode/autogen-ext-yepcode) repository.

## Features

- **Secure Execution**: Code runs in isolated, production-grade sandboxes
- **Multi-language Support**: Python and JavaScript execution
- **Automatic Package Installation**: YepCode automatically detects and installs dependencies in the sandbox
- **Logging and Monitoring**: Access to YepCode's execution logs, results and errors
- **AG2 Integration**: Seamless integration with AG2 agents and tools

## Installation

Install the package using pip:

```bash
pip install ag2_ext_yepcode
```

## Setup

1. **Create a YepCode Account**: Sign up at [yepcode.io](https://yepcode.io/)
2. **Get Your API Token**: Navigate to `Settings` > `API credentials` in your YepCode workspace
3. **Set Environment Variable**:

   ```bash
   export YEPCODE_API_TOKEN="your-api-token-here"
   ```

Alternatively, you can pass the API token directly to the executor constructor.

## Quick Start

### Basic Integration with AG2

The YepCode executor is designed to work with AG2 agents as a `CodeExecutor`. Here's a example of just the code executor agent:

```python
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
\```python
message = "Hello, world!"
print(message)
return message
\```

and return the output.
"""

# Generate a reply for the given code.
reply = code_executor_agent.generate_reply(messages=[{"role": "user", "content": task}])
print(reply)
```

### With LLMs and code execution tools

The extension also works with more advanced patterns, like using LLMs and code execution tools:

```python
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
    human_input_mode="ALWAYS",
)

# The code writer agent's system message is to instruct the LLM on how to use
# the code executor in the code executor agent.
code_writer_system_message = """You are a helpful AI assistant.
Solve tasks using your coding and language skills.
In the following cases, suggest python code (in a python coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply 'TERMINATE' in the end when everything is done.
"""

code_writer_agent = ConversableAgent(
    "code_writer_agent",
    system_message=code_writer_system_message,
    llm_config=LLMConfig(
        api_type="anthropic",
        model="claude-3-haiku-20240307",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    ),
    code_execution_config=False,  # Turn off code execution for this agent.
)

chat_result = code_executor_agent.initiate_chat(
    code_writer_agent,
    message="Fetch cryptocurrency price data from a public API and analyze the top 5 cryptocurrencies by market cap. Use the requests library to get data and calculate some basic statistics.",
)
print(chat_result)
```

### Custom Configuration

You can customize the YepCode executor behavior:

```python
# Custom executor configuration
yepcode_executor = YepCodeCodeExecutor(
    api_token="your-api-token",  # Optional: pass token directly
    timeout=300,  # 5 minutes timeout
    remove_on_done=False,  # Keep execution records for debugging
    sync_execution=True,  # Wait for completion
)
```

## API Reference

### YepCodeCodeExecutor

The main executor class for running code in YepCode's serverless environment.

#### Constructor Parameters

- `api_token` (Optional[str]): YepCode API token. If not provided, will use `YEPCODE_API_TOKEN` environment variable.
- `timeout` (int): Execution timeout in seconds. Default: 60.
- `remove_on_done` (bool): Whether to remove execution records after completion. Default: True.
- `sync_execution` (bool): Whether to wait for execution completion. Default: True.

#### Methods

- `async execute_code_blocks(code_blocks, cancellation_token)`: Execute code blocks

### YepCodeCodeResult

Result object returned from code execution.

#### Properties

- `exit_code` (int): Execution exit code (0 for success)
- `output` (str): Execution output and logs
- `execution_id` (Optional[str]): YepCode execution ID for tracking

## Supported Languages

| Language   | Language Code | Aliases |
| ---------- | ------------- | ------- |
| Python     | `python`      | `py`    |
| JavaScript | `javascript`  | `js`    |

## Development

### Setup Development Environment

```bash
git clone https://github.com/yepcode/ag2_ext_yepcode.git
cd ag2_ext_yepcode
poetry install
```

### Run Tests

```bash
pytest tests/ -v
```

## 📚 Documentation

- **[YepCode Documentation](https://yepcode.io/docs)**: Complete YepCode platform documentation
- **[AG2 Documentation](https://docs.ag2.ai/)**: AG2 framework documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
