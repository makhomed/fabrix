import __builtin__


def test_yaml_import_fallback(tmpdir, monkeypatch):
    original_import = __builtin__.__import__

    def import_hook(name, *args, **kwargs):
        if name == 'CLoader':
            raise ImportError('test case module import failure')
        else:
            return original_import(name, *args, **kwargs)
    __builtin__.__import__ = import_hook
    from fabrix.config import read_config
    from fabric.api import env
    fabfile = tmpdir.join("fabfile.py")
    config_filename = tmpdir.join("stage.yaml")
    config_filename.write("""
        hosts:
            - 10.10.10.10
    """)
    monkeypatch.setitem(env, "real_fabfile", str(fabfile))
    read_config("stage.yaml")
    assert env.hosts == ['10.10.10.10']
    __builtin__.__import__ = original_import
