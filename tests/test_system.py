import time
import fabrix.system
from conftest import mock_run_factory, abort
from fabric.api import env
from fabrix.system import is_reboot_required, reboot_and_wait, disable_selinux
from fabrix.system import systemctl_start, systemctl_stop, systemctl_reload, systemctl_restart
from fabrix.system import systemctl_enable, systemctl_disable, systemctl_mask, systemctl_unmask
from fabrix.system import systemctl_edit


def test_is_reboot_required(monkeypatch):
    run_state = {
        r'if \[ ! -e /usr/bin/needs-restarting \] ; then echo notexists ; fi': {'stdout': 'notexists', 'failed': False},
        r'yum -y install yum-utils': {'stdout': '', 'failed': False},
        r'/usr/bin/needs-restarting -r': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert is_reboot_required() is False
    run_state = {
        r'if \[ ! -e /usr/bin/needs-restarting \] ; then echo notexists ; fi': {'stdout': '', 'failed': False},
        r'/usr/bin/needs-restarting -r': {'stdout': 'Reboot is required to ensure that your system benefits from these updates.', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert is_reboot_required() is True


def test_reboot_and_wait(monkeypatch):
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    run_state = {
        r'reboot': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    monkeypatch.setattr(fabrix.system.connections, 'connect', lambda x: None)
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    assert reboot_and_wait() is None


def test_disable_selinux(monkeypatch):
    run_state = {
        r'if \[ -e /etc/selinux/config \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
        r'if \[ -e /usr/sbin/setenforce \] && \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': 'exists', 'failed': False},
        r'STATUS=\$\(getenforce\) ; if \[ "\$STATUS" == "Enforcing" \] ; then setenforce 0 ; echo perm ; fi': {'stdout': 'perm', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    monkeypatch.setattr(fabrix.system, 'edit_file', lambda x, y: True)
    assert disable_selinux() is True
    run_state = {
        r'if \[ -e /etc/selinux/config \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
        r'if \[ -e /usr/sbin/setenforce \] && \[ -e /usr/sbin/getenforce \] ; then echo exists ; fi': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert disable_selinux() is False


def test_systemctl_start(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl start ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_start(name) is None


def test_systemctl_stop(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl stop ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_stop(name) is None


def test_systemctl_reload(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl reload ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_reload(name) is None


def test_systemctl_restart(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl restart ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_restart(name) is None


def test_systemctl_enable(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl enable ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_enable(name) is None


def test_systemctl_disable(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl disable ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_disable(name) is None


def test_systemctl_mask(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl mask ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_mask(name) is None


def test_systemctl_unmask(monkeypatch):
    name = 'name'
    run_state = {
        r'systemctl daemon-reload ; systemctl unmask ' + name + ' ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_unmask(name) is None


def test_systemctl_edit(monkeypatch):
    with abort('systemctl_edit: invalid unit name \'.*\' in file .* line .*'):
        systemctl_edit('mysql/d', "")
    monkeypatch.setattr(fabrix.system, 'create_directory', lambda x: True)
    monkeypatch.setattr(fabrix.system, 'write_file', lambda x, y: True)
    assert systemctl_edit('mysqld', "[Service]\nLimitNOFILE = 65535") is True
    assert systemctl_edit('mysqld.service', "[Service]\nLimitNOFILE = 65535") is True
    monkeypatch.setattr(fabrix.system, 'remove_file', lambda x: True)
    monkeypatch.setattr(fabrix.system, 'remove_directory', lambda x: True)
    assert systemctl_edit('mysqld', "") is True
    monkeypatch.setattr(fabrix.system, 'remove_file', lambda x: True)
    monkeypatch.setattr(fabrix.system, 'remove_directory', lambda x: True)
    assert systemctl_edit('mysqld', None) is True
    monkeypatch.setattr(fabrix.system, 'remove_file', lambda x: False)
    monkeypatch.setattr(fabrix.system, 'remove_directory', lambda x: False)
    assert systemctl_edit('mysqld', None) is False
