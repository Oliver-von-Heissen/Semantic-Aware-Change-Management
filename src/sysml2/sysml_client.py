import logging
from src.external.sysml2.branch import get_project_branch, get_project_branches
from src.external.sysml2.commit import push_commit
from src.external.sysml2.element import get_project_element, get_project_elements
from src.external.sysml2.meta import get_datatypes
from src.external.sysml2.project import get_project
logger = logging.getLogger(__name__)

class SysMLClient:

    def check_project_branch(project_id, branch_id):
        project = get_project(project_id)
        if project is None:
            return "Project not found", 404
        branch = get_project_branch(project_id, branch_id)
        if branch is None:
            return "Branch not found", 404
        return "Check successfull", 200

    def initialize(self, project_id, branch_id):
        # project
        self.project_id = project_id
        project = get_project(project_id)
        self.project_name = project["name"]
        # branch
        self.branch_id = branch_id
        branch = get_project_branch(project_id, branch_id)
        self.commit_id = branch["head"]["@id"]
        # staging
        self.change = []
        # fetch available data types
        datatypes = get_datatypes()
        self.datatypes = [datatype["title"] for datatype in datatypes["$defs"].values()]

        logger.info(f"Working on project {self.project_name}({self.project_id}) on branch main({self.branch_id}) on HEAD({self.commit_id})")

    def get_all_elements(self):
        elements = get_project_elements(self.project_id, self.commit_id)
        return elements

    def create(self, **attrs):
        """Create a new element and add it to the model."""
        logger.debug(f"Creating new element with attributes {attrs}")
        create_element = {
            "@type": "DataVersion",
            "payload": {
                **attrs
            }
        }
        self.change.append(create_element)

    def update(self, element_id, **attrs):
        """Update an existing element in the model."""
        logger.debug(f"Updating element({element_id}) with attributes {attrs}")
        update_element = {
            "@type": "DataVersion",
            "payload": {
                **attrs
            },
            "identity": {
                "@id": element_id
            }
        }
        self.change.append(update_element)

    def delete(self, element_id):
        logger.debug(f"Deleting the element({element_id})")
        delete_element = {
            "@type": "DataVersion",
            "payload":None,     # no payload removes the element
            "identity": {
                "@id": element_id
            }
        }
        self.change.append(delete_element)

    def commit_and_push(self):
        commit_id = push_commit(self.project_id, self.change)
        self.commit_id = commit_id
        self.change = []

    def get_element(self, element_id):
        # Fetch the element in the given commit of the given project
        element = get_project_element(self.project_id, self.commit_id, element_id)
        return element

    # Returns directly / immediate owned elements for a given element in a given commit of a given project
    def print_owned_elements(self, element_id, indent):
        
        # Fetch the element in the given commit of the given project
        element_data = self.get_element(element_id)

        # Print single element to console
        element_name_to_print = element_data['name'] if element_data['name'] else 'N/A'
        element_type = element_data ['@type']
        print(f"{indent} - {element_name_to_print} ({element_type})")
        
        if element_data:
            owned_elements = element_data['ownedElement']
            if len(owned_elements) > 0:
                for owned_element in owned_elements:
                    self.print_owned_elements(owned_element['@id'], indent+' ')
        else:
            print(f"Unable to fetch element with id '{element_id}' in commit '{self.commit_id}' of project '{self.project_id}'")

    def print_project_structure(self):
        print("Project Structure:")
        all_project_elements = self.get_all_elements()
        if not all_project_elements:
            print("EMPTY")
        for element in all_project_elements:
            if not element.get('owner'):
                self.print_owned_elements(element['@id'], '')
