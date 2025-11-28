import os
import tempfile
import pytest
from unittest.mock import Mock, patch

from src.utils.sysml_file_io import FileImporter, FileExporter


# -------------------------------
# Fixtures and helpers
# -------------------------------


@pytest.fixture
def mock_project_handler():
    handler = Mock()
    handler.change = []
    handler.create_element = Mock(
        side_effect=lambda typ, name: handler.change.append({"type": typ, "name": name})
    )
    return handler


@pytest.fixture
def sample_sysml_file(tmp_path):
    content = "package Model {\n    part def Engine {\n        part Wheel;\n    }\n}\n"
    file_path = tmp_path / "model.sysml"
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def sample_elements():
    return [
        {"@type": "PartDefinition", "name": "Engine"},
        {"@type": "PartUsage", "name": "Wheel"},
    ]


# -------------------------------
# Tests for FileImporter
# -------------------------------


def test_interpret_reads_and_stages_changes(mock_project_handler, sample_sysml_file):
    importer = FileImporter()
    importer.interpret(mock_project_handler, sample_sysml_file)

    assert len(mock_project_handler.create_element.call_args_list) == 2
    assert mock_project_handler.create_element.call_args_list[0][0] == (
        "PartDefinition",
        "Engine",
    )
    assert mock_project_handler.create_element.call_args_list[1][0] == (
        "PartUsage",
        "Wheel",
    )
    assert isinstance(importer.file_content, list)
    assert all(isinstance(line, str) for line in importer.file_content)


def test_interpret_invalid_extension_raises(tmp_path, mock_project_handler):
    file_path = tmp_path / "invalid.txt"
    file_path.write_text("part def Engine;")

    importer = FileImporter()
    with pytest.raises(ValueError, match=r".*\.sysml.*"):
        importer.interpret(mock_project_handler, str(file_path))


def test_interpret_file_not_found(mock_project_handler):
    importer = FileImporter()
    with pytest.raises(FileNotFoundError):
        importer.interpret(mock_project_handler, "nonexistent.sysml")


def test_interpret_ignores_malformed_lines(tmp_path, mock_project_handler):
    file_path = tmp_path / "bad_lines.sysml"
    file_path.write_text("par def MissingKeyword\nrandom gibberish\n")

    importer = FileImporter()
    importer.interpret(mock_project_handler, str(file_path))

    # Should not raise and should not create any elements
    assert mock_project_handler.create_element.call_count == 0


def test_interpret_handler_raises_exception(tmp_path):
    file_path = tmp_path / "test.sysml"
    file_path.write_text("part def Boom")

    handler = Mock()
    handler.change = []
    handler.create_element.side_effect = RuntimeError("Handler error")

    importer = FileImporter()
    with pytest.raises(RuntimeError, match="Handler error"):
        importer.interpret(handler, str(file_path))


# -------------------------------
# Tests for FileExporter
# -------------------------------


@pytest.fixture
def exporter_with_generated_content():
    """Creates a FileExporter instance and generates content from test elements."""
    exporter = FileExporter()
    elements = [
        {"@type": "PartDefinition", "name": "Engine"},
        {"@type": "PartUsage", "name": "engineInstance"},
    ]
    exporter.generate_sysml_text(elements)
    return exporter.file_contents


def test_generate_sysml_text_creates_expected_structure(sample_elements):
    exporter = FileExporter()
    exporter.generate_sysml_text(sample_elements)

    print(exporter.file_contents)
    assert any("part def Engine;" in line.strip() for line in exporter.file_contents)
    assert any("part Wheel;" in line.strip() for line in exporter.file_contents)


@patch("builtins.input", return_value="y")
def test_export_to_file_creates_file(mock_input, tmp_path):
    file_path = tmp_path / "output"

    exporter = FileExporter()
    exporter.file_contents = ["package Model {\n", "    part Engine;\n", "}\n"]
    exporter.export_to_file(str(file_path))

    output_path = str(file_path) + ".sysml"
    assert os.path.exists(output_path)

    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "part Engine;" in content


@patch("builtins.input", return_value="n")
def test_export_to_file_cancels_on_existing_file(mock_input, tmp_path):
    path = tmp_path / "existing.sysml"
    path.write_text("Old content")

    exporter = FileExporter()
    exporter.file_contents = ["New content\n"]
    exporter.export_to_file(str(path))

    # File should not be overwritten
    assert path.read_text() == "Old content"


def test_export_to_file_invalid_extension(tmp_path):
    path = tmp_path / "wrong.txt"
    exporter = FileExporter()
    with pytest.raises(ValueError):
        exporter.export_to_file(str(path))


def test_generate_sysml_text_empty_input():
    exporter = FileExporter()
    exporter.generate_sysml_text([])

    assert any("package Model" in line for line in exporter.file_contents)
    assert "part" not in "".join(exporter.file_contents)


def test_generate_sysml_text_missing_keys():
    exporter = FileExporter()
    bad_elements = [{"@type": "PartUsage"}, {"name": "NoType"}]

    with pytest.raises(KeyError):
        exporter.generate_sysml_text(bad_elements)


def test_generate_sysml_text_invalid_type():
    exporter = FileExporter()

    with pytest.raises(TypeError):
        exporter.generate_sysml_text("not a list")


@patch("builtins.input", return_value="y")
def test_export_to_file_nonexistent_directory(mock_input):
    with tempfile.TemporaryDirectory() as tmp:
        new_folder = os.path.join(tmp, "newdir", "nested")
        file_path = os.path.join(new_folder, "export")

        exporter = FileExporter()
        exporter.file_contents = ["package Test {\n", "    part X;\n", "}\n"]
        exporter.export_to_file(file_path)

        full_path = file_path + ".sysml"
        assert os.path.exists(full_path)


# Notation Conformance Tests
def test_balanced_brackets(exporter_with_generated_content):
    text = "".join(exporter_with_generated_content)
    for open_, close in [("(", ")"), ("{", "}"), ("[", "]")]:
        assert text.count(open_) == text.count(close), f"Unbalanced {open_}{close}"


def test_valid_line_endings(exporter_with_generated_content):
    for line in exporter_with_generated_content:
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            continue
        assert stripped.endswith(("{", "}", ";")), f"Invalid line ending: {line}"


def test_comment_format_valid(exporter_with_generated_content):
    for line in exporter_with_generated_content:
        if any(sym in line for sym in ["#", "--"]) and not line.strip().startswith(
            "//"
        ):
            pytest.fail(f"Invalid comment format: {line}")


def test_indentation_consistency(exporter_with_generated_content):
    for line in exporter_with_generated_content:
        if line.strip():
            spaces = len(line) - len(line.lstrip(" "))
            assert spaces % 4 == 0, f"Inconsistent indentation: {line}"
