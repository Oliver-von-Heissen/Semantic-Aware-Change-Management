import logging
import os
from dotenv import load_dotenv
from token_count import TokenCount
from langchain.chat_models import init_chat_model
from src.change.prompt import prompt_template
from src.sysml2 import sysml_types
logger = logging.getLogger(__name__)


# Load environment variables from .env file
load_dotenv()
OPENAI_API_MODEL = os.environ.get("OPENAI_API_MODEL")

# Set up model and counter
model = init_chat_model(OPENAI_API_MODEL, model_provider="openai")
tc = TokenCount(model_name=OPENAI_API_MODEL)


def create_llm_prompt(context, user_request):
    prompt = prompt_template.format(types=sysml_types.sysml_types, context=context, user_request=user_request)
    input_token = tc.num_tokens_from_string(prompt)
    return prompt, input_token

def send_llm_request(context, user_request, tools):
    # prepare request
    model_with_tools = model.bind_tools(tools, tool_choice="any") # force the llm to use at least one tool
    prompt, input_token = create_llm_prompt(context, user_request)
    logger.debug("Sending LLM REST request")
    logger.debug(f"  Context: {context}")
    logger.debug(f"  User-Request: {user_request}")
    logger.debug(f"  Tools: {tools}")
    logger.debug(f"  Prompt: {prompt}")

    # send request
    response = model_with_tools.invoke(prompt).tool_calls

    # postprocess result
    logger.debug(f"  Response: {response}")
    output_token = tc.num_tokens_from_string(str(response)) # convert dict to str

    return response, input_token, output_token
