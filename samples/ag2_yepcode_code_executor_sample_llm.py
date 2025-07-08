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
    message="Write Python code to calculate the 14th Fibonacci number.",
)
print(chat_result)


chat_result = code_executor_agent.initiate_chat(
    code_writer_agent,
    message="Fetch cryptocurrency price data from a public API and analyze the top 5 cryptocurrencies by market cap. Use the requests library to get data and calculate some basic statistics.",
)
print(chat_result)
