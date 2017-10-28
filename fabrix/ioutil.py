import sys
import os
import os.path
import uuid
import StringIO
import pprint
import inspect
import fabric.state
from fabric.api import env, abort, local, run, get, put, quiet, settings


def debug(*args):
    if fabric.state.output.debug:
        for arg in args:
            if isinstance(arg, basestring):
                if arg[-1] == '\n':
                    sys.stdout.write(arg)
                else:
                    print arg
            else:
                pprint.PrettyPrinter(indent=4).pprint(arg)
            print '-' * 78


def read_local_file(local_filename, abort_on_error=True):
    try:
        with open(local_filename) as local_file:
            content = local_file.read()
    except IOError, ex:
        if abort_on_error:
            abort(str(ex))
        else:
            return None
    return content


def read_file(remote_filename, abort_on_error=True):
    file_like_object = StringIO.StringIO()
    with quiet():
        with settings(warn_only=True):
            if get(local_path=file_like_object, remote_path=remote_filename).failed:
                file_like_object.close()
                if abort_on_error:
                    abort('downloading file ' + remote_filename + ' from host %s failed' % env.host_string)
                else:
                    return None
            file_like_object.seek(0)
            content = file_like_object.read()
            file_like_object.close()
    return content


def write_local_file(local_filename, new_content):
    old_content = read_local_file(local_filename, abort_on_error=False)
    if new_content == old_content:
        return False
    else:
        _atomic_write_local_file(local_filename, new_content)
        return True


def write_file(remote_filename, new_content):
    old_content = read_file(remote_filename, abort_on_error=False)
    if new_content == old_content:
        return False
    else:
        _atomic_write_file(remote_filename, new_content)
        return True


def _atomic_write_local_file(local_filename, content):
    old_filename = local_filename
    with quiet():
        if not os.path.isabs(old_filename):
            abort('local filename must be absolute, "%s" given' % old_filename)
        exists = os.path.exists(old_filename)
        if exists:
            # !!!WARNING!!! os.path.isfile(path) - Return True if path is an existing regular file.
            # This follows symbolic links, so both islink() and isfile() can be true for the same path.
            if not os.path.isfile(old_filename) or os.path.islink(old_filename):
                abort('local filename must be regular file, "%s" given' % old_filename)
            nlink = os.stat(old_filename).st_nlink
            if nlink > 1:
                abort('file "%s" has %d hardlinks, it can\'t be atomically written' % (old_filename, nlink))
        new_filename = old_filename + '.tmp.' + uuid.uuid4().hex + '.tmp'
        new_file = open(new_filename, 'w')
        new_file.write(content)
        new_file.close()
        if exists:
            _copy_local_file_owner_and_mode(old_filename, new_filename)
            _copy_local_file_acl(old_filename, new_filename)
            _copy_local_file_xattr(old_filename, new_filename)
            _copy_local_file_selinux_context(old_filename, new_filename)
        os.rename(new_filename, old_filename)


def _copy_local_file_owner_and_mode(old_filename, new_filename):
    old_file_stat = os.stat(old_filename)
    os.chown(new_filename, old_file_stat.st_uid, old_file_stat.st_gid)
    os.chmod(new_filename, old_file_stat.st_mode)


def _copy_local_file_acl(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            if os.path.exists('/usr/bin/getfacl') and os.path.exists('/usr/bin/setfacl'):
                local('getfacl --absolute-names -- ' + old_filename + ' | setfacl --set-file=- -- ' + new_filename)


def _copy_local_file_xattr(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            local('cp --attributes-only --preserve=xattr -- ' + old_filename + ' ' + new_filename)


def _copy_local_file_selinux_context(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            if os.path.exists('/usr/sbin/getenforce'):
                if local('getenforce', capture=True) != 'Disabled':
                    if os.path.exists('/usr/bin/chcon'):
                        local('chcon --reference=' + old_filename + ' -- ' + new_filename)


def _atomic_write_file(remote_filename, content):
    old_filename = remote_filename
    with quiet():
        if not os.path.isabs(old_filename):
            abort('remote filename must be absolute, "%s" given' % old_filename)
        exists = run('if [ -e ' + old_filename + ' ] ; then echo exists ; fi') == 'exists'
        if exists:
            if run('if [ ! -f ' + old_filename + ' ] ; then echo isnotfile ; fi') == 'isnotfile':
                abort('remote filename must be regular file, "%s" given' % old_filename)
            nlink = int(run('stat --format "%h" -- ' + old_filename))
            if nlink > 1:
                abort('file "%s" has %d hardlinks, it can\'t be atomically written' % (old_filename, nlink))
        new_filename = old_filename + '.tmp.' + uuid.uuid4().hex + '.tmp'
        file_like_object = StringIO.StringIO()
        file_like_object.write(content)
        if put(local_path=file_like_object, remote_path=new_filename).failed:
            abort('uploading file ' + new_filename + ' to host %s failed' % env.host_string)
        file_like_object.close()
        if exists:
            _copy_file_owner_and_mode(old_filename, new_filename)
            _copy_file_acl(old_filename, new_filename)
            _copy_file_xattr(old_filename, new_filename)
            _copy_file_selinux_context(old_filename, new_filename)
        run('mv -f -- ' + new_filename + ' ' + old_filename)


def _copy_file_owner_and_mode(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            run('chown --reference=' + old_filename + ' -- ' + new_filename)
            run('chmod --reference=' + old_filename + ' -- ' + new_filename)


def _copy_file_acl(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            if (run('if [ -e /usr/bin/getfacl ] ; then echo exists ; fi') == 'exists' and
                    run('if [ -e /usr/bin/setfacl ] ; then echo exists ; fi') == 'exists'):
                run('getfacl --absolute-names -- ' + old_filename + ' | setfacl --set-file=- -- ' + new_filename)


def _copy_file_xattr(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            run('cp --attributes-only --preserve=xattr -- ' + old_filename + ' ' + new_filename)


def _copy_file_selinux_context(old_filename, new_filename):
    with quiet():
        with settings(warn_only=True):
            if run('if [ -e /usr/sbin/getenforce ] ; then echo exists ; fi') == 'exists':
                if run('getenforce') != 'Disabled':
                    if run('if [ -e /usr/bin/chcon ] ; then echo exists ; fi') == 'exists':
                        run('chcon --reference=' + old_filename + ' -- ' + new_filename)


def copy_file(local_filename, remote_filename):
    files_dir = os.path.join(os.path.dirname(env.real_fabfile), 'files')
    if not os.path.isdir(files_dir):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('copy_file: files dir \'%s\' not exists in file %s line %s' % (files_dir, fname, nline))
    local_abs_filename = os.path.join(files_dir, local_filename)
    if not os.path.isfile(local_abs_filename):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('copy_file: file \'%s\' not exists in file %s line %s' % (local_abs_filename, fname, nline))
    content = read_local_file(local_abs_filename)
    changed = write_file(remote_filename, content)
    return changed
