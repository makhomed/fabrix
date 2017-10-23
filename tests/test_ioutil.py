import fabrix.ioutil
from conftest import abort, mock_get_factory, mock_put_factory, mock_run_factory
from fabric.api import env
from fabrix.ioutil import debug, read_local_file, write_local_file, _atomic_write_local_file
from fabrix.ioutil import read_remote_file, write_remote_file, _atomic_write_remote_file


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
    with abort('local filename must be regular file, "%s" given' % str(symlink)):
        _atomic_write_local_file(str(symlink), "text")
    directory = tmpdir.join("directory")
    directory.mkdir()
    with abort('local filename must be regular file, "%s" given' % str(directory)):
        _atomic_write_local_file(str(directory), "text")
    regular_file = tmpdir.join("regular-file")
    regular_file.write("text")
    hardlink = tmpdir.join("hardlink")
    hardlink.mklinkto(regular_file)
    with abort('file "%s" has %d hardlinks, it can\'t be atomically written' % (regular_file, 2)):
        _atomic_write_local_file(str(regular_file), "text")


def test_read_remote_file(monkeypatch):
    get_state = {
        r'/ok': {'content': "ok-text", 'failed': False},
        r'/failed': {'content': "failed-text", 'failed': True}
    }
    mock_get = mock_get_factory(get_state)
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    monkeypatch.setattr(fabrix.ioutil, 'get', mock_get)
    with abort('downloading file ' + '/failed' + ' from remote host %s failed' % '11.11.11.11'):
        read_remote_file('/failed', abort_on_error=True)
    assert read_remote_file('/failed', abort_on_error=False) is None
    assert read_remote_file('/ok', abort_on_error=True) == 'ok-text'
    assert read_remote_file('/ok', abort_on_error=False) == 'ok-text'


def test_write_remote_file(monkeypatch):
    get_state = {
        r'/ok': {'content': "ok-text", 'failed': False},
        r'/failed': {'content': "failed-text", 'failed': True}
    }
    mock_get = mock_get_factory(get_state)
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    monkeypatch.setattr(fabrix.ioutil, 'get', mock_get)
    monkeypatch.setattr(fabrix.ioutil, '_atomic_write_remote_file', lambda x, y: None)
    assert write_remote_file('/ok', 'ok-text') is False
    assert write_remote_file('/ok', 'other-text') is True
    assert write_remote_file('/failed', "text") is True
    assert write_remote_file('/failed', None) is False


def test__atomic_write_remote_file(monkeypatch):
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    put_state = {
        r'/newfile-put-ok\.tmp\.\w+\.tmp$': False,
        r'/newfile-put-failed\.tmp\.\w+\.tmp$': True
    }
    mock_put = mock_put_factory(put_state)
    monkeypatch.setattr(fabrix.ioutil, 'put', mock_put)
    run_state = {
            r'if \[ -e /isnotfile \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ ! -f /isnotfile \] ; then echo isnotfile ; fi': {'stdout': 'isnotfile', 'failed': False},

            r'if \[ -e /7hardlinks \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ ! -f /7hardlinks \] ; then echo isnotfile ; fi': {'stdout': '', 'failed': False},
            r'stat --format "%h" /7hardlinks': {'stdout': '7', 'failed': False},

            r'if \[ -e /newfile-put-ok \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
            r'mv -f /newfile-put-ok\.tmp\.\w+\.tmp /newfile-put-ok': {'stdout': '', 'failed': False},
            r'if \[ -e /newfile-put-failed \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    with abort('remote filename must be absolute, "%s" given' % 'not-absolute-path'):
        _atomic_write_remote_file('not-absolute-path', 'text')
    with abort('remote filename must be regular file, "%s" given' % '/isnotfile'):
        _atomic_write_remote_file('/isnotfile', 'text')
    with abort('file "%s" has %d hardlinks, it can\'t be atomically written' % ('/7hardlinks', 7)):
        _atomic_write_remote_file('/7hardlinks', 'text')
    assert _atomic_write_remote_file('/newfile-put-ok', 'text') is None
    with abort(r'uploading file /newfile-put-failed\.tmp\.\w+\.tmp to remote host failed'):
        _atomic_write_remote_file('/newfile-put-failed', 'text')
