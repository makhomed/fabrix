import os.path
import fabrix.ioutil
from conftest import abort, mock_get_factory, mock_put_factory, mock_run_factory, mock_local_factory, mock_os_path_exists_factory
from fabric.api import env
from fabrix.ioutil import debug, read_local_file, write_local_file, _atomic_write_local_file
from fabrix.ioutil import read_file, write_file, _atomic_write_file
from fabrix.ioutil import _copy_local_file_acl, _copy_local_file_selinux_context
from fabrix.ioutil import _copy_file_owner_and_mode, _copy_file_acl, _copy_file_selinux_context


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


def test__copy_local_file_acl(tmpdir, monkeypatch):
    old_file = tmpdir.join("old-file")
    old_file.write("old")
    old_filename = str(old_file)
    new_file = tmpdir.join("new-file")
    new_file.write("new")
    new_filename = str(new_file)
    os_path_exists_state = {
        r'/usr/bin/getfacl': True,
        r'/usr/bin/setfacl': False,
    }
    mock_os_path_exists = mock_os_path_exists_factory(os_path_exists_state)
    monkeypatch.setattr(os.path, 'exists', mock_os_path_exists)
    assert _copy_local_file_acl(old_filename, new_filename) is None
    os_path_exists_state = {
        r'/usr/bin/getfacl': True,
        r'/usr/bin/setfacl': True,
    }
    mock_os_path_exists = mock_os_path_exists_factory(os_path_exists_state)
    monkeypatch.setattr(os.path, 'exists', mock_os_path_exists)
    local_state = {
        r'getfacl --absolute-names -- .* | setfacl --set-file=- -- .*': {'stdout': '', 'failed': False},
    }
    mock_local = mock_local_factory(local_state)
    monkeypatch.setattr(fabrix.ioutil, 'local', mock_local)
    assert _copy_local_file_acl(old_filename, new_filename) is None


def test__copy_local_file_selinux_context(tmpdir, monkeypatch):
    old_file = tmpdir.join("old-file")
    old_file.write("old")
    old_filename = str(old_file)
    new_file = tmpdir.join("new-file")
    new_file.write("new")
    new_filename = str(new_file)
    os_path_exists_state = {
        r'/usr/sbin/getenforce': False,
    }
    mock_os_path_exists = mock_os_path_exists_factory(os_path_exists_state)
    monkeypatch.setattr(os.path, 'exists', mock_os_path_exists)
    assert _copy_local_file_selinux_context(old_filename, new_filename) is None
    os_path_exists_state = {
        r'/usr/sbin/getenforce': True,
    }
    mock_os_path_exists = mock_os_path_exists_factory(os_path_exists_state)
    monkeypatch.setattr(os.path, 'exists', mock_os_path_exists)
    local_state = {
        r'getenforce': {'stdout': 'Disabled', 'failed': False},
    }
    mock_local = mock_local_factory(local_state)
    monkeypatch.setattr(fabrix.ioutil, 'local', mock_local)
    assert _copy_local_file_selinux_context(old_filename, new_filename) is None
    os_path_exists_state = {
        r'/usr/sbin/getenforce': True,
        r'/usr/bin/chcon': True
    }
    mock_os_path_exists = mock_os_path_exists_factory(os_path_exists_state)
    monkeypatch.setattr(os.path, 'exists', mock_os_path_exists)
    local_state = {
        r'getenforce': {'stdout': 'Enabled', 'failed': False},
        r'chcon --reference=.* -- .*': {'stdout': '', 'failed': False},
    }
    mock_local = mock_local_factory(local_state)
    monkeypatch.setattr(fabrix.ioutil, 'local', mock_local)
    assert _copy_local_file_selinux_context(old_filename, new_filename) is None
    os_path_exists_state = {
        r'/usr/sbin/getenforce': True,
        r'/usr/bin/chcon': False
    }
    mock_os_path_exists = mock_os_path_exists_factory(os_path_exists_state)
    monkeypatch.setattr(os.path, 'exists', mock_os_path_exists)
    local_state = {
        r'getenforce': {'stdout': 'Enabled', 'failed': False},
    }
    mock_local = mock_local_factory(local_state)
    monkeypatch.setattr(fabrix.ioutil, 'local', mock_local)
    assert _copy_local_file_selinux_context(old_filename, new_filename) is None


def test_read_file(monkeypatch):
    get_state = {
        r'/ok': {'content': "ok-text", 'failed': False},
        r'/failed': {'content': "failed-text", 'failed': True}
    }
    mock_get = mock_get_factory(get_state)
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    monkeypatch.setattr(fabrix.ioutil, 'get', mock_get)
    with abort('downloading file ' + '/failed' + ' from host %s failed' % '11.11.11.11'):
        read_file('/failed', abort_on_error=True)
    assert read_file('/failed', abort_on_error=False) is None
    assert read_file('/ok', abort_on_error=True) == 'ok-text'
    assert read_file('/ok', abort_on_error=False) == 'ok-text'


def test_write_file(monkeypatch):
    get_state = {
        r'/ok': {'content': "ok-text", 'failed': False},
        r'/failed': {'content': "failed-text", 'failed': True}
    }
    mock_get = mock_get_factory(get_state)
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    monkeypatch.setattr(fabrix.ioutil, 'get', mock_get)
    monkeypatch.setattr(fabrix.ioutil, '_atomic_write_file', lambda x, y: None)
    assert write_file('/ok', 'ok-text') is False
    assert write_file('/ok', 'other-text') is True
    assert write_file('/failed', "text") is True
    assert write_file('/failed', None) is False


def test__atomic_write_file(monkeypatch):
    put_state = {
        r'/newfile-put-ok\.tmp\.\w+\.tmp$': False,
        r'/newfile-put-failed\.tmp\.\w+\.tmp$': True,
        r'/1hardlink\.tmp\.\w+\.tmp$': False,
    }
    mock_put = mock_put_factory(put_state)
    monkeypatch.setattr(fabrix.ioutil, 'put', mock_put)
    run_state = {
            r'if \[ -e /isnotfile \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ ! -f /isnotfile \] ; then echo isnotfile ; fi': {'stdout': 'isnotfile', 'failed': False},

            r'if \[ -e /7hardlinks \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ ! -f /7hardlinks \] ; then echo isnotfile ; fi': {'stdout': '', 'failed': False},
            r'stat --format "%h" -- /7hardlinks': {'stdout': '7', 'failed': False},

            r'if \[ -e /newfile-put-ok \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
            r'mv -f -- /newfile-put-ok\.tmp\.\w+\.tmp /newfile-put-ok': {'stdout': '', 'failed': False},
            r'if \[ -e /newfile-put-failed \] ; then echo exists ; fi': {'stdout': '', 'failed': False},

            r'if \[ -e /1hardlink \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ ! -f /1hardlink \] ; then echo isnotfile ; fi': {'stdout': '', 'failed': False},
            r'stat --format "%h" -- /1hardlink': {'stdout': '1', 'failed': False},
            r'mv -f -- /1hardlink\.tmp\.\w+\.tmp /1hardlink': {'stdout': '', 'failed': False},
            r'cp --attributes-only --preserve=xattr -- .* .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    with abort('filename must be absolute, "%s" given' % 'not-absolute-path'):
        _atomic_write_file('not-absolute-path', 'text')
    with abort('filename must be regular file, "%s" given' % '/isnotfile'):
        _atomic_write_file('/isnotfile', 'text')
    with abort('file "%s" has %d hardlinks, it can\'t be atomically written' % ('/7hardlinks', 7)):
        _atomic_write_file('/7hardlinks', 'text')
    assert _atomic_write_file('/newfile-put-ok', 'text') is None
    with abort(r'uploading file /newfile-put-failed\.tmp\.\w+\.tmp to host .* failed'):
        _atomic_write_file('/newfile-put-failed', 'text')

    def mock__copy_file_owner_and_mode(old_filename, new_filename):
        pass
    monkeypatch.setattr(fabrix.ioutil, '_copy_file_owner_and_mode', mock__copy_file_owner_and_mode)

    def mock__copy_file_acl(old_filename, new_filename):
        pass
    monkeypatch.setattr(fabrix.ioutil, '_copy_file_acl', mock__copy_file_acl)

    def mock__copy_file_selinux_context(old_filename, new_filename):
        pass
    monkeypatch.setattr(fabrix.ioutil, '_copy_file_selinux_context', mock__copy_file_selinux_context)
    assert _atomic_write_file('/1hardlink', 'text') is None


def test__copy_file_owner_and_mode(monkeypatch):
    run_state = {
            r'chown --reference=.* -- .*': {'stdout': '', 'failed': False},
            r'chmod --reference=.* -- .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_owner_and_mode('/old', '/new') is None


def test__copy_file_acl(monkeypatch):
    run_state = {
            r'if \[ -e /usr/bin/getfacl \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ -e /usr/bin/setfacl \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_acl('/old', '/new') is None
    run_state = {
            r'if \[ -e /usr/bin/getfacl \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'if \[ -e /usr/bin/setfacl \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'getfacl --absolute-names -- .* | setfacl --set-file=- -- .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_acl('/old', '/new') is None


def test__copy_file_selinux_context(monkeypatch):
    run_state = {
            r'if \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_selinux_context('/old', '/new') is None
    run_state = {
            r'if \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'getenforce': {'stdout': 'Disabled', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_selinux_context('/old', '/new') is None
    run_state = {
            r'if \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'getenforce': {'stdout': 'Enabled', 'failed': False},
            r'if \[ -e /usr/bin/chcon \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_selinux_context('/old', '/new') is None
    run_state = {
            r'if \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'getenforce': {'stdout': 'Enabled', 'failed': False},
            r'if \[ -e /usr/bin/chcon \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
            r'chcon --reference=.* -- .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.ioutil, 'run', mock_run)
    assert _copy_file_selinux_context('/old', '/new') is None
