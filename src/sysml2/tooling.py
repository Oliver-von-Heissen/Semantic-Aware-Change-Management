import logging
from langchain_core.tools import StructuredTool
from src.sysml2.sysml_client import SysMLClient
from src.sysml2.handler.base_handler import TYPE_HANDLERS, BaseHandler
from src.sysml2.handler.generic_handler import GenericHandler
logger = logging.getLogger(__name__)


def _choose_handler(sysml_type: str) -> BaseHandler:
    return TYPE_HANDLERS.get(sysml_type, GenericHandler())

def make_tools(client: SysMLClient):
    def create(**attrs):
        """Create a new element with a given set of attributes for the model.
        
        Args:
            **attrs: dictionary of element attributes
        """
        attrs = attrs["attrs"]
        type = attrs.get("@type")
        handler = _choose_handler(type)
        return handler.create(client, **attrs)
    
    def update(element_id, **attrs):
        """Update the attributes of an existing element.

        Args:
            element_id: id of the existing element.
            **attrs: dictionary of updated element attributes, always including @type
        """
        attrs = attrs["attrs"]
        type = attrs.get("@type")
        handler = _choose_handler(type)
        return handler.update(client, element_id, **attrs)
    
    def delete(element_id, type):
        """Remove an existing element from the model.

        Args:
            element_id: ID of the element to be removed.
            type: the @type attribute of the element to be deleted.
        
        """
        handler = _choose_handler(type)
        return handler.delete(client, element_id)
    
    return [
        StructuredTool.from_function(func=create),
        StructuredTool.from_function(func=update),
        StructuredTool.from_function(func=delete)
    ]

def execute_tool(tools_by_name, tool_call):
    tool_name = tool_call.get("name")
    tool_args = tool_call.get("args", {})
    logger.info(f"Function Call for {tool_name} - {tool_args}")

    # check tool
    selected_tool = tools_by_name[tool_name]
    if not selected_tool:
        logger.error(f"Unknown tool: {tool_name}")
        return f"Error: Tool {tool_name} not found."

    # Preprocess tool args
    if tool_name == "create" and "attrs" not in tool_args:
        tool_args = {"attrs": tool_args}
    elif tool_name == "update":
        if "attrs" not in tool_args:
            tool_args = {"attrs": tool_args}
        if "element_id" in tool_args["attrs"]:
            tool_args["element_id"] = tool_args["attrs"].pop("element_id")

    try:
        selected_tool.invoke(tool_args)
        return f"{tool_name} - {tool_args}"
    except Exception as e:
        logger.error(f"Error invoking tool {tool_name}: {e}")
        return f"Error: Toolcall malfunction for {tool_name} - {tool_args}"
