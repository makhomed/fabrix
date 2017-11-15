import fabrix
from conftest import mock_run_factory
from fabrix.editor import strip_text
from fabrix.passwd import get_user_home_directory, add_user_ssh_authorized_keys
from fabrix.passwd import is_user_exists, is_user_not_exists, create_user, remove_user
from fabrix.passwd import is_group_exists, is_group_not_exists, create_group, remove_group
from fabrix.passwd import is_user_in_group, is_user_not_in_group, add_user_to_group, delete_user_from_group


PASSWD = strip_text("""
    root:x:0:0:root:/root:/bin/bash
    bin:x:1:1:bin:/bin:/sbin/nologin
    daemon:x:2:2:daemon:/sbin:/sbin/nologin
    adm:x:3:4:adm:/var/adm:/sbin/nologin
    lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
    sync:x:5:0:sync:/sbin:/bin/sync
    shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
    halt:x:7:0:halt:/sbin:/sbin/halt
    mail:x:8:12:mail:/var/spool/mail:/sbin/nologin
    operator:x:11:0:operator:/root:/sbin/nologin
    games:x:12:100:games:/usr/games:/sbin/nologin
    ftp:x:14:50:FTP User:/var/ftp:/sbin/nologin
    nobody:x:99:99:Nobody:/:/sbin/nologin
    systemd-bus-proxy:x:999:998:systemd Bus Proxy:/:/sbin/nologin
    systemd-network:x:998:997:systemd Network Management:/:/sbin/nologin
    dbus:x:81:81:System message bus:/:/sbin/nologin
    rpc:x:32:32:Rpcbind Daemon:/var/lib/rpcbind:/sbin/nologin
    sshd:x:74:74:Privilege-separated SSH:/var/empty/sshd:/sbin/nologin
    nginx:x:997:995:nginx user:/var/cache/nginx:/sbin/nologin
    apache:x:48:48:Apache:/usr/share/httpd:/sbin/nologin
    postfix:x:89:89::/var/spool/postfix:/sbin/nologin
""")


def test_get_user_home_directory(monkeypatch):
    run_state = {
            r'getent passwd': {'stdout': PASSWD, 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    assert get_user_home_directory("root") == "/root"
    assert get_user_home_directory("none") is None


def test_add_user_ssh_authorized_keys(monkeypatch):

    def mock_read_local_file(filename):
        return strip_text("""
        line1

        line2
        """)
    monkeypatch.setattr(fabrix.passwd, 'get_user_home_directory', lambda x: "/home/" + x)
    monkeypatch.setattr(fabrix.passwd, 'create_directory', lambda x: None)
    monkeypatch.setattr(fabrix.passwd, 'chown', lambda x, y, z: None)
    monkeypatch.setattr(fabrix.passwd, 'chmod', lambda x, y: None)
    monkeypatch.setattr(fabrix.passwd, 'create_file', lambda x: None)
    monkeypatch.setattr(fabrix.passwd, 'read_local_file', mock_read_local_file)
    monkeypatch.setattr(fabrix.passwd, 'edit_file', lambda x, y: None)
    assert add_user_ssh_authorized_keys("user", "keys") is None


def test_is_user_exists(monkeypatch):
    run_state = {
            r'getent passwd': {'stdout': PASSWD, 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    assert is_user_exists("nginx") is True
    assert is_user_exists("not-exists") is False
    assert is_user_not_exists("nginx") is False
    assert is_user_not_exists("not-exists") is True


def test_create_user(monkeypatch):
    run_state = {
            r'useradd .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    monkeypatch.setattr(fabrix.passwd, 'is_user_not_exists', lambda x: True)
    assert create_user("user") is None
    monkeypatch.setattr(fabrix.passwd, 'is_user_not_exists', lambda x: False)
    assert create_user("user") is None


def test_remove_user(monkeypatch):
    run_state = {
            r'userdel .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    monkeypatch.setattr(fabrix.passwd, 'is_user_exists', lambda x: True)
    assert remove_user("user") is None
    monkeypatch.setattr(fabrix.passwd, 'is_user_exists', lambda x: False)
    assert remove_user("user") is None


GROUP = strip_text("""
        root:x:0:
        bin:x:1:
        daemon:x:2:
        wheel:x:10:
        cdrom:x:11:
        mail:x:12:postfix
        man:x:15:
        dialout:x:18:
        sshd:x:74:
        nginx:x:995:
        apache:x:48:
        postdrop:x:90:
        postfix:x:89:
        screen:x:84:
""")


def test_is_group_exists(monkeypatch):
    run_state = {
            r'getent group': {'stdout': GROUP, 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    assert is_group_exists("wheel") is True
    assert is_group_exists("nonex") is False
    assert is_group_not_exists("daemon") is False
    assert is_group_not_exists("not-ex") is True


def test_create_group(monkeypatch):
    run_state = {
            r'groupadd .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    monkeypatch.setattr(fabrix.passwd, 'is_group_not_exists', lambda x: True)
    assert create_group("group") is None
    monkeypatch.setattr(fabrix.passwd, 'is_group_not_exists', lambda x: False)
    assert create_group("group") is None


def test_remove_group(monkeypatch):
    run_state = {
            r'groupdel .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    monkeypatch.setattr(fabrix.passwd, 'is_group_exists', lambda x: True)
    assert remove_group("group") is None
    monkeypatch.setattr(fabrix.passwd, 'is_group_exists', lambda x: False)
    assert remove_group("group") is None


def test_is_user_in_group(monkeypatch):
    run_state = {
            r'getent group': {'stdout': GROUP, 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    assert is_user_in_group("postfix", "man") is False
    assert is_user_in_group("postfix", "zzz") is False
    assert is_user_in_group("postfix", "mail") is True
    assert is_user_not_in_group("postfix", "man") is True
    assert is_user_not_in_group("postfix", "zzz") is True
    assert is_user_not_in_group("postfix", "mail") is False


def test_add_user_to_group(monkeypatch):
    run_state = {
            r'gpasswd .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    monkeypatch.setattr(fabrix.passwd, 'is_user_not_in_group', lambda x, y: True)
    assert add_user_to_group("user", "group") is None
    monkeypatch.setattr(fabrix.passwd, 'is_user_not_in_group', lambda x, y: False)
    assert add_user_to_group("user", "group") is None


def test_delete_user_from_group(monkeypatch):
    run_state = {
            r'gpasswd .*': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.passwd, 'run', mock_run)
    monkeypatch.setattr(fabrix.passwd, 'is_user_in_group', lambda x, y: True)
    assert delete_user_from_group("user", "group") is None
    monkeypatch.setattr(fabrix.passwd, 'is_user_in_group', lambda x, y: False)
    assert delete_user_from_group("user", "group") is None
