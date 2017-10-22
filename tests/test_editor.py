import pytest
from fabrix.editor import edit_text, edit_ini_section, edit_local_file, edit_remote_file
from fabrix.editor import _apply_editors, append_line, prepend_line, strip_line
from fabrix.editor import substitute_line, replace_line, delete_line, insert_line


def test_empty_list_of_editors():
    with pytest.raises(SystemExit, message="editors can\'t be empty"):
        _apply_editors("text")


def test_non_idempotend_editors():
    def editor(text):
        return text + "x"
    with pytest.raises(SystemExit, message="editors is not idempotent"):
        _apply_editors("text", editor)


def test_append_line():
    assert edit_text("", append_line("append")) == "append\n"
    assert edit_text("\n", append_line("append")) == "\nappend\n"
    assert edit_text("line", append_line("append")) == "line\nappend\n"
    assert edit_text("line\n", append_line("append")) == "line\nappend\n"

    assert edit_text("append", append_line("append")) == "append"
    assert edit_text("append\n", append_line("append")) == "append\n"

    assert edit_text("", append_line("append", True)) == "\nappend\n"
    assert edit_text("\n", append_line("append", True)) == "\n\nappend\n"
    assert edit_text("line", append_line("append", True)) == "line\n\nappend\n"
    assert edit_text("line\n", append_line("append", True)) == "line\n\nappend\n"


def test_prepend_line():
    assert edit_text("", prepend_line("prepend")) == "prepend\n"
    assert edit_text("\n", prepend_line("prepend")) == "prepend\n\n"
    assert edit_text("line", prepend_line("prepend")) == "prepend\nline"
    assert edit_text("line\n", prepend_line("prepend")) == "prepend\nline\n"

    assert edit_text("prepend", prepend_line("prepend")) == "prepend"
    assert edit_text("prepend\n", prepend_line("prepend")) == "prepend\n"

    assert edit_text("", prepend_line("prepend", True)) == "prepend\n\n"
    assert edit_text("\n", prepend_line("prepend", True)) == "prepend\n\n\n"
    assert edit_text("line", prepend_line("prepend", True)) == "prepend\n\nline"
    assert edit_text("line\n", prepend_line("prepend", True)) == "prepend\n\nline\n"


def test_strip_line():
    assert edit_text("line", strip_line()) == "line"
    assert edit_text("line ", strip_line()) == "line"
    assert edit_text(" line", strip_line()) == "line"
    assert edit_text(" line ", strip_line()) == "line"

    assert edit_text(" line \n line 2 ", strip_line()) == "line\nline 2"
    assert edit_text("xxxlinexxx\nxxxlinexxx2xxx", strip_line("x")) == "line\nlinexxx2"
    assert edit_text("xxxlinexxx\nxxxlinexxx2xxx", strip_line("")) == "xxxlinexxx\nxxxlinexxx2xxx"


def test_substitute_line():
    import re
    assert edit_text("php php php", substitute_line("php", "PHP")) == "PHP PHP PHP"
    assert edit_text("PHP PhP php", substitute_line("PHP", "Python", re.IGNORECASE)) == "Python Python Python"
    assert edit_text("PHP PhP php", substitute_line("PHP", "Python")) == "Python PhP php"
    assert edit_text("some php text", substitute_line("php", "PHP")) == "some PHP text"
    assert edit_text("somephptext", substitute_line("php", "PHP")) == "somePHPtext"
    assert edit_text("text", substitute_line("php", "PHP")) == "text"


def test_replace_line():
    import re
    assert edit_text("php php php", replace_line("php", "PHP")) == "php php php"
    assert edit_text("SOME TEXT", replace_line("some text", "xxx", re.IGNORECASE)) == "xxx"
    assert edit_text("text some", replace_line("^text.*", "xxx")) == "xxx"
    assert edit_text("some text", replace_line(".*text$", "xxx")) == "xxx"
    assert edit_text("some text", replace_line("^some text$", "xxx")) == "xxx"
    assert edit_text("some text", replace_line("so(.*) (.*)xt", r'\1zzz\2')) == "mezzzte"


def test_delete_line():
    assert edit_text("text", delete_line("line")) == "text"
    assert edit_text("text\nxxx", delete_line("xxx")) == "text"
    assert edit_text("text\nxxx\n", delete_line("xxx")) == "text\n"


def test_insert_line():
    with pytest.raises(SystemExit, message='insert_line: must be defined \'before\' or \'after\' argument'):
        edit_text("text", insert_line("line"))
    with pytest.raises(SystemExit, message='insert_line: unknown insert_type \'%s\'' % 'xxx'):
        edit_text("text", insert_line("line", xxx="text"))
    with pytest.raises(SystemExit, message='insert_line: already defined insert_type \'%s\', unexpected \'%s\'' % ('after', 'before')):
        edit_text("text", insert_line("line", after="text", before="text"))
    assert edit_text("text", insert_line("line", before="text")) == "line\ntext"
    assert edit_text("text\n", insert_line("line", before="text")) == "line\ntext\n"
    assert edit_text("text", insert_line("line", after="text")) == "text\nline"
    assert edit_text("text\n", insert_line("line", after="text")) == "text\nline\n"
    with pytest.raises(SystemExit, message='insert_line: anchor pattern \'%s\' not found' % "text"):
        edit_text("test", insert_line("line", after="text"))
    with pytest.raises(SystemExit, message='insert_line: anchor pattern \'%s\' found %d times, must be only one' % ("text", 2)):
        edit_text("test\ntest\n", insert_line("line", after="test"))


def test_edit_ini_section():
    with pytest.raises(SystemExit, message='edit_ini_section: section name must be in form [section_name]'):
        edit_text("text", edit_ini_section("section", append_line("append")))
    with pytest.raises(SystemExit, message='edit_ini_section: section name must be in form [section_name]'):
        edit_text("text", edit_ini_section("[section", append_line("append")))
    with pytest.raises(SystemExit, message='edit_ini_section: section name must be in form [section_name]'):
        edit_text("text", edit_ini_section("section]", append_line("append")))
    with pytest.raises(SystemExit, message='edit_ini_section: section \'[%s]\' not found' % "section"):
        edit_text("text", edit_ini_section("[section]", append_line("append")))
    with pytest.raises(SystemExit, message='edit_ini_section: bad ini file, section \'[%s]\' duplicated' % "section"):
        edit_text("# php\n[section]\nt=1\n[section]\nx=2\n", edit_ini_section("[section]", append_line("z=3")))
    with pytest.raises(SystemExit, message='edit_ini_section: bad ini file, section \'[%s]\' duplicated' % "section"):
        edit_text("# php\n[section]\nt=1\n[x]\na=b\n[section]\nx=2\n", edit_ini_section("[section]", append_line("z=3")))
    with pytest.raises(SystemExit, message='edit_ini_section: bad ini file, section \'[%s]\' duplicated' % "section"):
        edit_text("[section]\n[section]\n", edit_ini_section("[section]", append_line("append")))
    assert edit_text("[remi-php70]\nenabled=0\n", edit_ini_section("[remi-php70]", replace_line("enabled=0", "enabled=1"))) == "[remi-php70]\nenabled=1\n"
    assert edit_text("[remi]\nenabled=0\n[x]\n", edit_ini_section("[remi]", replace_line("enabled=0", "enabled=1"))) == "[remi]\nenabled=1\n[x]\n"
    assert edit_text("# php\n[remi-php70]\nenabled=0\n", edit_ini_section(None, substitute_line("php", "PHP"))) == "# PHP\n[remi-php70]\nenabled=0\n"


def test_edit_local_file(tmpdir):
    temp_file = tmpdir.join("test.txt")
    temp_file.write("some example text")
    changed = edit_local_file(str(temp_file), substitute_line("example", "sample"))
    assert changed is True
    assert temp_file.read() == "some sample text"
    changed = edit_local_file(str(temp_file), substitute_line("example", "sample"))
    assert changed is False


def test_edit_remote_file(tmpdir, monkeypatch):
    remote_file = dict(content="some example text")

    def patch_read_remote_file(remote_filename):
        assert remote_filename
        return remote_file['content']

    def patch__atomic_write_remote_file(remote_filename, new_content):
        assert remote_filename
        remote_file['content'] = new_content

    import fabrix.ioutil
    monkeypatch.setattr(fabrix.editor, 'read_remote_file', patch_read_remote_file)
    monkeypatch.setattr(fabrix.editor, '_atomic_write_remote_file', patch__atomic_write_remote_file)
    changed = edit_remote_file("/path/to/test.txt", substitute_line("example", "sample"))
    assert changed is True
    assert remote_file['content'] == "some sample text"
    changed = edit_remote_file("/path/to/test.txt", substitute_line("example", "sample"))
    assert changed is False
