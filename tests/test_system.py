import time
import fabrix.system
from conftest import mock_run_factory, abort
from fabric.api import env
from fabrix.system import is_reboot_required, reboot_and_wait, disable_selinux
from fabrix.system import systemctl_start, systemctl_stop, systemctl_reload, systemctl_restart
from fabrix.system import systemctl_enable, systemctl_disable, systemctl_mask, systemctl_unmask
from fabrix.system import systemctl_edit, systemctl_get_default, systemctl_set_default
from fabrix.system import localectl_set_locale, timedatectl_set_timezone
from fabrix.system import get_virtualization_type


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
    with abort('systemctl_edit: override must be string in file .* line .*'):
        systemctl_edit("mysqld", ['some', 'text'])
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


def test_systemctl_get_default(monkeypatch):
    run_state = {
        r'systemctl daemon-reload ; systemctl get-default ; systemctl daemon-reload': {'stdout': 'multi-user.target', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_get_default() == 'multi-user.target'


def test_systemctl_set_default(monkeypatch):
    run_state = {
        r'systemctl daemon-reload ; systemctl set-default multi-user.target ; systemctl daemon-reload': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert systemctl_set_default('multi-user.target') == ''


def test_localectl_set_locale(monkeypatch):
    run_state = {
        r'localectl set-locale LANG=en_US.UTF-8': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert localectl_set_locale('LANG=en_US.UTF-8') == ''


def test_timedatectl_set_timezone(monkeypatch):
    run_state = {
        r'timedatectl set-timezone Europe/Kiev': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert timedatectl_set_timezone('Europe/Kiev') == ''


def test_get_virtualization_type(monkeypatch):
    run_state = {
        r'hostnamectl status': {'stdout': """
           Static hostname: test-centos
                 Icon name: computer-container
                   Chassis: container
                Machine ID: f8889d6132eb43658e8f6ea6f30c394e
                   Boot ID: 20e212fab38942e4b499f100f75f575c
            Virtualization: openvz
          Operating System: CentOS Linux 7 (Core)
               CPE OS Name: cpe:/o:centos:centos:7
                    Kernel: Linux 2.6.32-042stab124.2
              Architecture: x86-64
            """, 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert get_virtualization_type() == 'openvz'
    run_state = {
        r'hostnamectl status': {'stdout': """
           Static hostname: example.com
                 Icon name: computer-server
                   Chassis: server
                Machine ID: 4c500bbc51bb45539b5206bcbc523a42
                   Boot ID: 9c6aa7f2c066445e92f74f14d38bdc13
          Operating System: CentOS Linux 7 (Core)
               CPE OS Name: cpe:/o:centos:centos:7
                    Kernel: Linux 3.10.0-693.2.2.el7.x86_64
              Architecture: x86-64
            """, 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.system, 'run', mock_run)
    assert get_virtualization_type() is None
