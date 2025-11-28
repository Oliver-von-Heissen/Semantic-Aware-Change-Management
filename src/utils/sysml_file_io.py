"""
# SysML File Interface

This file declares an Importer and Exporter class to read and write SysML 2.0
Files to and from the server. The interface capability aims to be aligned to
the current tool capabilities and does not cover the full specification.
"""

import os
from typing import List

from src.sysml2.sysml_client import SysMLClient


def read_sysml_file(file_path: str) -> List[str]:
    """Reads a .sysml file and returns its lines as a list.

    Args:
        filepath (str): Path to the .sysml file.

    Returns:
        list[str]: Lines from the file.

    Raises:
        ValueError: If file extension is not .sysml.
        IOError: If file can't be read or is unable to retrieve the file contents.
    """
    if not file_path.endswith(".sysml"):
        raise ValueError(f"Invalid file type: '{file_path}'. Expected a .sysml file.")

    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    if len(lines) == 0:
        raise IOError(f"Failed to read the file '{file_path}': No content was found.")
    return lines


class FileImporter:
    """
    Parses .sysml files and stages model elements as changes via a SysMLClient.

    Attributes:
        file_content (List[str]): Raw content of the imported file, line by line.
        changes (List[dict]): Staged changes parsed from the file (not committed).
    """

    def __init__(self):
        self.file_content: List[str] = []
        self.changes: List[dict] = []

    def interpret(self, client: SysMLClient, file_path: str) -> None:
        """
        Reads a .sysml file and stages model element creation commands.

        The method identifies 'part' and 'part def' declarations line by line,
        extracts the element names, and instructs the provided SysMLClient
        to stage creation actions accordingly. Trailing opening braces (' {')
        are stripped before processing.

        Note:
            This method does not check for existing elements on the server.
            All changes are added to the project handler's local change list,
            but are not committed or uploaded.

        Args:
            client (SysMLClient): Handler used to stage model changes.
            file_path (str): Path to the .sysml file to interpret.
        """
        # Save file content for later review
        self.file_content = read_sysml_file(file_path=file_path)
        commits_initial = client.change.copy()
        for line in [l.strip().rstrip(";") for l in self.file_content]:
            if line.startswith("part def"):
                content = line[len("part def") :].rstrip("{").strip()
                client.create_element("PartDefinition", content)
            elif line.startswith("part"):
                content = line[len("part") :].rstrip("{").strip()
                client.create_element("PartUsage", content)

        # Create a deep copy of the new changes for review
        self.commits = [
            c.copy() for c in client.change if c not in commits_initial
        ]


class FileExporter:
    """
    Converts model elements into SysML-compliant text and manages file export.

    Attributes:
        file_contents (List[str]): Lines of generated SysML content, ready to be written to a file.
    """

    def __init__(self):
        self.file_contents: List[str] = []

    def generate_sysml_text(self, elements: List[dict]) -> None:
        """
        Generates formatted SysML text from a list of model elements.

        Elements are grouped by type and organized into nested 'package' blocks.
        Specifically:
        - `partDefinition` elements are written under a Definitions → PartDefinitions package.
        - `ownedPart` elements are written under a Configuration package.

        The generated text is stored in the `file_contents` attribute for later export.

        Args:
            elements (List[dict]): A list of model elements, where each element must
                include a '@type' key (either 'partDefinition' or 'ownedPart') and a 'name'.

        Raises:
            KeyError: If any element is missing the required 'name' or '@type' keys.
            TypeError: If the input is not a list of dictionaries.
        """

        file_contents = []
        indent_level = 0

        class SectionWriter:
            def __init__(self, section_type: str, section_name: str):
                self.section_type = section_type
                self.section_name = section_name

            def __enter__(self):
                nonlocal indent_level
                file_contents.append(
                    indent_level * 4 * " "
                    + f"{self.section_type} {self.section_name} {{\n"
                )
                indent_level += 1
                return self  # return self if needed for nested packages

            def __exit__(self, exc_type, exc_val, exc_tb):
                nonlocal indent_level
                indent_level -= 1
                file_contents.append(indent_level * 4 * " " + "}\n")

        def write_line(text: str) -> None:
            file_contents.append(indent_level * 4 * " " + text + ";\n")

        # Build File Section by Section, following the structure of the sample SysML file.
        part_definitions = [e for e in elements if e["@type"] == "PartDefinition"]
        parts = [e for e in elements if e["@type"] == "PartUsage"]

        with SectionWriter("package", "Model"):

            sum_definitions = len(part_definitions)
            if sum_definitions > 0:
                with SectionWriter("package", "Definitions"):
                    if len(part_definitions) > 0:
                        with SectionWriter("package", "PartDefinitions"):
                            for p in part_definitions:
                                write_line(f"part def {p['name']}")

            with SectionWriter("package", "Configuration"):
                for p in parts:
                    write_line(f"part {p['name']}")

        print(file_contents)
        self.file_contents = file_contents

    def export_to_file(self, file_path: str) -> None:
        """
        Writes the file_contents to a .sysml file at the specified path.

        - Ensures the target directory exists; creates it if necessary.
        - Appends '.sysml' if missing; raises an error for other extensions.
        - Prompts before overwriting an existing file.

        Args:
            file_path (str): Target file path for export.

        Raises:
            ValueError: If the file extension is not '.sysml' or is invalid.
            OSError: If directory creation or file writing fails.
        """
        # Ensure correct file extension
        base, ext = os.path.splitext(file_path)
        if not ext:
            file_path += ".sysml"
        elif ext != ".sysml":
            raise ValueError(
                f"Invalid file extension '{ext}'. Only '.sysml' is allowed."
            )

        # Ensure directory exists
        folder = os.path.dirname(file_path)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder, exist_ok=True)
            except OSError as e:
                raise OSError(f"Failed to access or create directory '{folder}': {e}")

        # Confirm overwrite if file exists
        if os.path.exists(file_path):
            confirm = (
                input(f"File '{file_path}' already exists. Overwrite? [y/N]: ")
                .strip()
                .lower()
            )
            if confirm != "y":
                print("Export canceled.")
                return

        # Write file contents
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(self.file_contents)
