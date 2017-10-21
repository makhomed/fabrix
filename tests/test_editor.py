import pytest
from fabrix.editor import edit_text, append_line, _apply_editors


def test_append_line():
    assert edit_text("", append_line("append")) == "append\n"
    assert edit_text("\n", append_line("append")) == "\nappend\n"
    assert edit_text("line", append_line("append")) == "line\nappend\n"
    assert edit_text("line\n", append_line("append")) == "line\nappend\n"

    assert edit_text("", append_line("append", True)) == "\nappend\n"
    assert edit_text("\n", append_line("append", True)) == "\n\nappend\n"
    assert edit_text("line", append_line("append", True)) == "line\n\nappend\n"
    assert edit_text("line\n", append_line("append", True)) == "line\n\nappend\n"


def test_non_idempotend_editors():
    def editor(text):
        return text + "x"
    with pytest.raises(SystemExit, message="editors is not idempotent"):
        _apply_editors("text", editor)


def test_empty_list_of_editors():
    with pytest.raises(SystemExit, message="editors can\'t be empty"):
        _apply_editors("text")
