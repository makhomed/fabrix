import time
import fabrix.reboot
from conftest import mock_run_factory
from fabric.api import env
from fabrix.reboot import is_reboot_required, reboot_and_wait


def test_is_reboot_required(monkeypatch):
    run_state = {
        r'if \[ ! -e /usr/bin/needs-restarting \] ; then echo notexists ; fi': {'stdout': 'notexists', 'failed': False},
        r'yum -y install yum-utils': {'stdout': '', 'failed': False},
        r'/usr/bin/needs-restarting -r': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.reboot, 'run', mock_run)
    assert is_reboot_required() is False
    run_state = {
        r'if \[ ! -e /usr/bin/needs-restarting \] ; then echo notexists ; fi': {'stdout': '', 'failed': False},
        r'/usr/bin/needs-restarting -r': {'stdout': 'Reboot is required to ensure that your system benefits from these updates.', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.reboot, 'run', mock_run)
    assert is_reboot_required() is True


def test_reboot_and_wait(monkeypatch):
    monkeypatch.setitem(env, "host_string", '11.11.11.11')
    run_state = {
        r'reboot': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.reboot, 'run', mock_run)
    monkeypatch.setattr(fabrix.reboot.connections, 'connect', lambda x: None)
    monkeypatch.setattr(time, 'sleep', lambda x: None)
    assert reboot_and_wait() is None
