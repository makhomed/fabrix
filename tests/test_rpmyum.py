import fabrix.rpmyum
from conftest import mock_run_factory, abort
from fabrix.rpmyum import yum_install, yum_remove, yum_update, _parse_packages


def test_yum_install(tmpdir, monkeypatch):
    run_state = {
        r'yum -y install a b c': {'stdout': '', 'failed': False},
        r'yum -y install A B C': {'stdout': 'Nothing to do', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.rpmyum, 'hide_run', mock_run)
    assert yum_install(["c", "b"], "a") is True
    assert yum_install(""" C B A """) is False


def test_yum_remove(tmpdir, monkeypatch):
    run_state = {
        r'yum -y remove a b c': {'stdout': '', 'failed': False},
        r'yum -y remove A B C': {'stdout': 'No Packages marked for removal', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.rpmyum, 'hide_run', mock_run)
    assert yum_remove(["c", "b"], "a") is True
    assert yum_remove(""" C B A """) is False


def test_yum_update(tmpdir, monkeypatch):
    run_state = {
        r'yum -y update a b c$': {'stdout': '', 'failed': False},
        r'yum -y update A B C$': {'stdout': 'No packages marked for update', 'failed': False},
        r'yum -y update $': {'stdout': '', 'failed': False},
    }
    mock_run = mock_run_factory(run_state)
    monkeypatch.setattr(fabrix.rpmyum, 'hide_run', mock_run)
    assert yum_update(["c", "b"], "a") is True
    assert yum_update(""" C B A """) is False
    assert yum_update() is True


def test__parse_packages():
    with abort('.*: unexpected object \'.*\' in list of packages in file .* line .*'):
        _parse_packages(0, False, None)
    with abort('.*: unexpected empty list of packages in file .* line .*'):
        _parse_packages(0, False, [[], [[], [[]]]], [])
    assert _parse_packages(0, False, """

            A

            B

            C

        """, [set("D"), list("E")]) == ['A', 'B', 'C', 'D', 'E']
