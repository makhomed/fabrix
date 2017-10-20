from fabrix.editor import edit_text, append_line


def test_append_line():
    assert edit_text("", append_line("append")) == "append\n"
    assert edit_text("\n", append_line("append")) == "\nappend\n"
    assert edit_text("line", append_line("append")) == "line\nappend\n"
    assert edit_text("line\n", append_line("append")) == "line\nappend\n"

    assert edit_text("", append_line("append", True)) == "\nappend\n"
    assert edit_text("\n", append_line("append", True)) == "\n\nappend\n"
    assert edit_text("line", append_line("append", True)) == "line\n\nappend\n"
    assert edit_text("line\n", append_line("append", True)) == "line\n\nappend\n"
