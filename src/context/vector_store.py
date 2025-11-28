import json
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from src.utils.json_sanitize import sanitize


class VectorDB:

    def __init__(self):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

        self.vector_store = Chroma(
            collection_name="sysml_model",
            embedding_function=embeddings,
            persist_directory="./db"
        )

    def add_elements(self, elements):
        """Add the elements to the vector store, where each element is treated as a document."""
        sanitized_elements = sanitize(elements) # store important data only, remove empty fields
        if elements:
            documents = []
            for element in sanitized_elements:
                doc = Document(
                    page_content=json.dumps(element),
                    id=element["@id"],
                    metadata={"owner_id": element.get("owner", {}).get("@id")}
                )
                documents.append(doc)

            self.vector_store.add_documents(documents=documents)

    def remove_all_elements(self):
        documents = self.vector_store.get()
        if documents["ids"]:
            self.vector_store.delete(ids=documents["ids"])

    def query(self, prompt, amount_of_elements=5):
        results = self.vector_store.similarity_search(
            prompt,
            k=amount_of_elements,
        )
        return results

    def related_elements(self, element_id: str):
        """
        Returns a single list of dicts:

        - all children whose metadata.owner_id == element_id
        - the owner element of the given element (if any)

        """
        # Fetch children via metadata filter
        children_res = self.vector_store.get(where={"owner_id": element_id})
        children_docs = children_res.get("documents") or []
        children = [json.loads(d) for d in children_docs if d]

        # Fetch the given element to get its owner_id from metadata
        given_res = self.vector_store.get(ids=[element_id])
        owner_id = None
        if given_res and given_res.get("metadatas"):
            owner_id = (given_res["metadatas"][0] or {}).get("owner_id")

        # Fetch the owner element (if any)
        owner = None
        if owner_id:
            owner_res = self.vector_store.get(ids=[owner_id])
            owner_doc = (owner_res.get("documents") or [None])[0]
            if owner_doc:
                owner = json.loads(owner_doc)

        # Combine and deduplicate by @id (safety)
        combined = children[:]
        if owner:
            combined.append(owner)

        unique_by_id = {}
        for el in combined:
            eid = el.get("@id")
            unique_by_id[eid] = el

        return list(unique_by_id.values())
    