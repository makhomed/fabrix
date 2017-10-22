from conftest import abort
from fabrix.ioutil import debug, read_local_file, write_local_file, _atomic_write_local_file


def test_debug(monkeypatch, capsys):
    delimiter = '-' * 78 + '\n'
    import fabric.state
    monkeypatch.setitem(fabric.state.output, 'debug', False)
    debug("test")
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    monkeypatch.setitem(fabric.state.output, 'debug', True)
    debug("test")
    out, err = capsys.readouterr()
    assert out == "test\n" + delimiter
    assert err == ""
    monkeypatch.setitem(fabric.state.output, 'debug', True)
    debug("test\n")
    out, err = capsys.readouterr()
    assert out == "test\n" + delimiter
    assert err == ""
    monkeypatch.setitem(fabric.state.output, 'debug', True)
    debug(["foo", "bar"])
    out, err = capsys.readouterr()
    assert out == "['foo', 'bar']\n" + delimiter
    assert err == ""


def test_read_local_file(tmpdir):
    temp_file = tmpdir.join("file.txt")
    temp_file.write("text")
    assert read_local_file(str(temp_file)) == "text"
    non_existent_file = tmpdir.join("non_existent_file")
    with abort(r'\[Errno 2\] No such file or directory:.*'):
        read_local_file(str(non_existent_file))
    assert read_local_file(str(non_existent_file), False) is None


def test_write_local_file(tmpdir):
    temp_file = tmpdir.join("file.txt")
    assert write_local_file(str(temp_file), "text") is True
    assert write_local_file(str(temp_file), "text") is False


def test__atomic_write_local_file(tmpdir):
    with abort('local filename must be absolute, "%s" given' % "file.txt"):
        _atomic_write_local_file("file.txt", "text")
    regular_file = tmpdir.join("regular-file")
    regular_file.write("text")
    symlink = tmpdir.join("symlink")
    symlink.mksymlinkto(regular_file)
    with abort('local filename must be regular file, symlink "%s" given' % str(symlink)):
        _atomic_write_local_file(str(symlink), "text")
    directory = tmpdir.join("directory")
    directory.mkdir()
    with abort('local filename must be regular file, directory "%s" given' % str(directory)):
        _atomic_write_local_file(str(directory), "text")
    regular_file = tmpdir.join("regular-file")
    regular_file.write("text")
    hardlink = tmpdir.join("hardlink")
    hardlink.mklinkto(regular_file)
    with abort('file "%s" has %d hardlinks, it can\'t be atomically written' % (regular_file, 2)):
        _atomic_write_local_file(str(regular_file), "text")
