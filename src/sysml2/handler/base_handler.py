from typing import Callable
from src.sysml2.sysml_client import SysMLClient


class BaseHandler:

    def create(self, client: SysMLClient, **attrs) -> None:
        raise NotImplementedError
    
    def update(self, client: SysMLClient, element_id: str, **attrs) -> None:
        raise NotImplementedError
    
    def delete(self, client: SysMLClient, element_id: str) -> None:
        raise NotImplementedError
    
TYPE_HANDLERS: dict[str, BaseHandler] = {}

def register_handler(sysml_type: str) -> Callable[[type], type]:
    """
    Decorator to register a handler class for a given SysML type.
    """
    def _decorator(cls: type) -> type:
        inst: BaseHandler = cls()  # stateless, safe to single-instance
        inst.sysml_type = sysml_type
        TYPE_HANDLERS[sysml_type] = inst
        return cls
    return _decorator
