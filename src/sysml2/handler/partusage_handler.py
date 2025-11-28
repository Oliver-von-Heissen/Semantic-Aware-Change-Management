import logging
from src.sysml2.sysml_client import SysMLClient
from src.sysml2.handler.base_handler import register_handler
from src.sysml2.handler.generic_handler import GenericHandler
logger = logging.getLogger(__name__)

@register_handler("PartUsage")
class PartDefinitionHandler(GenericHandler):

    def create(self, client: SysMLClient, **attrs) -> None:
        """PartUsage create operation, requires @type and definition"""
        logger.debug(f"Call create of PartUsage.")
                
        sysml_type = attrs.get("@type")
        if not sysml_type:
            raise ValueError("Missing '@type' for partusage create.")

        client.create(**attrs)
