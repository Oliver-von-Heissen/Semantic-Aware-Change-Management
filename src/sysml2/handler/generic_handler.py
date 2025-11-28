import logging
from src.sysml2.sysml_client import SysMLClient
from src.sysml2.handler.base_handler import BaseHandler
logger = logging.getLogger(__name__)


class GenericHandler(BaseHandler):
    
    def create(self, client: SysMLClient, **attrs) -> None:
        """Generic create operation, requires @type only"""
        logger.debug(f"Call create of GenericHandler.")

        sysml_type = attrs.get("@type")
        if not sysml_type:
            raise ValueError("Missing '@type' for generic create.")

        client.create(**attrs)

    def update(self, client: SysMLClient, element_id: str, **attrs) -> None:
        """Generic update operation, requires @type"""
        logger.debug(f"Call update of GenericHandler.")

        sysml_type = attrs.get("@type")
        if not sysml_type:
            raise ValueError("Missing '@type' for generic update.")
        
        client.update(element_id, **attrs)

    def delete(self, client: SysMLClient, element_id: str) -> None:
        """Generic delete operation"""
        logger.debug(f"Call delete of GenericHandler.")
        
        client.delete(element_id)