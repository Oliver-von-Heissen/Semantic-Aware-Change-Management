import json
import logging
from src.context.vector_store import VectorDB
from src.sysml2.sysml_client import SysMLClient
logger = logging.getLogger(__name__)


class ContextManager:

    def __init__(self, client: SysMLClient):
        self.client = client
        self.vector_db = VectorDB()
        self.vector_db.remove_all_elements() # for poc remove all elemnts here
        elements = client.get_all_elements()
        self.vector_db.add_elements(elements)

    def create_context(self, query):
        logger.debug(f"Context request: {query}")

        # 1) Fetch top-N elements from vector DB
        docs = self.vector_db.query(query, 5)

        # 2) Parse base elements (JSON) from page_content
        base_elements = []
        for doc in docs:
            try:
                base_elements.append(json.loads(doc.page_content))
            except Exception:
                logger.warning("Failed to parse document page_content as JSON.", exc_info=True)

        # 3) Collect related elements (children + owner) for each base element
        seen_ids = {e.get("@id") for e in base_elements if isinstance(e, dict)}
        enriched = list(base_elements)

        for elem in base_elements:
            elem_id = elem.get("@id") if isinstance(elem, dict) else None
            if not elem_id:
                continue

            try:
                related = self.vector_db.related_elements(elem_id) or []
            except Exception:
                logger.exception(f"Failed to fetch related elements for {elem_id}")
                related = []

            for r in related:
                rid = r.get("@id") if isinstance(r, dict) else None
                if rid and rid not in seen_ids:
                    enriched.append(r)
                    seen_ids.add(rid)

        # 4) Convert back to JSON strings
        context = [json.dumps(e) for e in enriched]

        logger.debug(f"Created Context: {context}")
        return context
    