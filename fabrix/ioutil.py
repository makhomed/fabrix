import sys
import os
import os.path
import re
import uuid
import StringIO
import pprint
import inspect
import numbers
import fabric.state
from fabric.api import env, abort, local, run, get, put, quiet, settings, hide
from fabric.network import key_filenames, normalize


def debug(*args):
    """Debug print all arguments.

    If debug mode is enabled via``fab --show=debug`` or something else - print each argument to sys.stdout, else do nothing.

    Args:
        *args: list of arguments for debug print.

    Returns: None
    """
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


def hide_run(command):
    """Run command with settings hide('everything').

    Args:
        command: which command run.

    Returns:
        Result of :func:`fabric.operations.run` execution.

    """
    with settings(hide('everything')):
        return run(command)


def read_local_file(local_filename, abort_on_error=True):
    """Read local file.

    Args:
        local_filename: Local file name, must be absolute.
        abort_on_error: :func:`fabric.utils.abort` if some errors encountered during reading file, for example, if file not exists.

    Returns:
        content of file or ``None`` if errors encountered and abort_on_error is False.
    """
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
    """Read remote file.

    Args:
        remote_filename: Remote file name, must be absolute.
        abort_on_error: :func:`fabric.utils.abort` if some errors encountered during reading file, for example, if file not exists.

    Returns:
        content of file or ``None`` if errors encountered and abort_on_error is False.
    """
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


def write_local_file(local_filename, content):
    """Write local file.

    Args:
        local_filename: Local file name, must be absolute.
        content: text which should be written in file, must be string.

    Returns:
        True if content differs from old file content and file changed,
        False if old contend == new content and file not changed at all.
    """
    old_content = read_local_file(local_filename, abort_on_error=False)
    if content == old_content:
        return False
    else:
        _atomic_write_local_file(local_filename, content)
        return True


def write_file(remote_filename, content):
    """Write remote file.

    Args:
        remote_filename: Remote file name, must be absolute.
        content: text which should be written in file, must be string.

    Returns:
        True if content differs from old file content and file changed,
        False if old contend == new content and file not changed at all.
    """
    old_content = read_file(remote_filename, abort_on_error=False)
    if content == old_content:
        return False
    else:
        _atomic_write_file(remote_filename, content)
        return True


def remove_file(remote_filename):
    """Remove remote file.

    Args:
        remote_filename: Remote file name, must be absolute.

    Returns:
        True if file removed, False if file not exists.
    """
    with settings(hide('everything')):
        if not os.path.isabs(remote_filename):
            abort('remote filename must be absolute, "%s" given' % remote_filename)
        changed = run('if [ -f ' + remote_filename + ' ] ; then rm -f -- ' + remote_filename + ' ; echo removed ; fi') == 'removed'
        return changed


def remove_directory(remote_dirname):
    """Remove remote directory.

    .. warning::
        Remote directory must be empty. Recursive deletion of non-empty directories is not supported.

    Args:
        remote_dirname: Remote directory name, must be absolute.

    Returns:
        True if directory removed, False if directory already not exists.
    """
    with settings(hide('everything')):
        if not os.path.isabs(remote_dirname):
            abort('remote directory name must be absolute, "%s" given' % remote_dirname)
        changed = run('if [ -d ' + remote_dirname + ' ] ; then rmdir -- ' + remote_dirname + ' ; echo removed ; fi') == 'removed'
        return changed


def create_directory(remote_dirname):
    """Create remote directory.

    .. warning::
        Directory created only if no file exists with name ``remote_dirname``. Existing file will not be deleted.

    Args:
        remote_dirname: Remote directory name, must be absolute.

    Returns:
        True if directory created, False if directory already exists.
    """
    with settings(hide('everything')):
        if not os.path.isabs(remote_dirname):
            abort('remote directory name must be absolute, "%s" given' % remote_dirname)
        changed = run('if [ ! -d ' + remote_dirname + ' ] ; then mkdir -- ' + remote_dirname + ' ; echo created ; fi') == 'created'
        return changed


def _atomic_write_local_file(local_filename, content):
    old_filename = local_filename
    with settings(hide('everything')):
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
    with settings(hide('everything')):
        with settings(warn_only=True):
            if os.path.exists('/usr/bin/getfacl') and os.path.exists('/usr/bin/setfacl'):
                local('getfacl --absolute-names -- ' + old_filename + ' | setfacl --set-file=- -- ' + new_filename)


def _copy_local_file_xattr(old_filename, new_filename):
    with settings(hide('everything')):
        with settings(warn_only=True):
            local('cp --attributes-only --preserve=xattr -- ' + old_filename + ' ' + new_filename)


def _copy_local_file_selinux_context(old_filename, new_filename):
    with settings(hide('everything')):
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
    with settings(hide('everything')):
        with settings(warn_only=True):
            run('chown --reference=' + old_filename + ' -- ' + new_filename)
            run('chmod --reference=' + old_filename + ' -- ' + new_filename)


def _copy_file_acl(old_filename, new_filename):
    with settings(hide('everything')):
        with settings(warn_only=True):
            if run('if [ -e /usr/bin/getfacl ] && [ -e /usr/bin/setfacl ] ; then echo exists ; fi') == 'exists':
                run('getfacl --absolute-names -- ' + old_filename + ' | setfacl --set-file=- -- ' + new_filename)


def _copy_file_xattr(old_filename, new_filename):
    with settings(hide('everything')):
        with settings(warn_only=True):
            run('cp --attributes-only --preserve=xattr -- ' + old_filename + ' ' + new_filename)


def _copy_file_selinux_context(old_filename, new_filename):
    with settings(hide('everything')):
        with settings(warn_only=True):
            if run('if [ -e /usr/sbin/getenforce ] ; then echo exists ; fi') == 'exists':
                if run('getenforce') != 'Disabled':
                    if run('if [ -e /usr/bin/chcon ] ; then echo exists ; fi') == 'exists':
                        run('chcon --reference=' + old_filename + ' -- ' + new_filename)


def copy_file(local_filename, remote_filename):
    """Copy file from ``local_filename`` on local host to ``remote_filename`` on remote host.

    If ``local_filename`` is relative it will be retrieved from directory ``files`` alongside with ``env.real_fabfile``.

    .. warning::
        Using absolute ``local_filename`` supported but not recommended.

    Args:
        local_filename: Local file name on local host, copy file from it. Should be relative.
        remote_filename: Remote file name on remote host, copy file to it. Must be absolute.

    Returns:
        True if remote file changed, False otherwise.
    """
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


def rsync(local_path, remote_path, extra_rsync_options=""):
    """Rsync files/directories from local path to remote_path.

    .. warning::
            Using absolute ``local_path`` supported but not recommended.

    Args:
        local_path: Local path on local host, copy files/directories from it. Should be relative.
        remote_path: Remote path on remote host, copy files/directories to it. Must be absolute.
        extra_rsync_options: Additional rsync options added after default '-aH --stats --force --timeout=600'

    Returns:
        True if some of remote files/directories are changed, False otherwise.
    """
    files_dir = os.path.join(os.path.dirname(env.real_fabfile), 'files')
    if not os.path.isdir(files_dir):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('rsync: files dir \'%s\' not exists in file %s line %s' % (files_dir, fname, nline))
    local_abs_path = os.path.join(files_dir, local_path)
    if not os.path.exists(local_abs_path):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('rsync: local path \'%s\' not exists in file %s line %s' % (local_abs_path, fname, nline))
    if not os.path.isabs(remote_path):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('rsync: remote path \'%s\' must be absolute in file %s line %s' % (remote_path, fname, nline))
    # ssh keys
    ssh_keys = ""
    keys = key_filenames()
    if keys:
        ssh_keys = " -i " + " -i ".join(keys)
    # ssh port
    user, host, port = normalize(env.host_string)
    ssh_port = "-p %s" % port
    # ssh options
    ssh_options = "-e 'ssh %s%s'" % (ssh_port, ssh_keys)
    # rsync options
    rsync_options = '-aH --stats --force --timeout=600 %s %s --' % (ssh_options, extra_rsync_options)
    # remote_prefix
    if host.count(':') > 1:
        # Square brackets are mandatory for IPv6 rsync address,
        # even if port number is not specified
        remote_prefix = "%s@[%s]" % (user, host)
    else:
        remote_prefix = "%s@%s" % (user, host)
    # execute command
    command = "rsync %s %s %s:%s" % (rsync_options, local_abs_path, remote_prefix, remote_path)
    with settings(hide('everything')):
        stdout = local(command, capture=True)
    zero_transfer_regexp = re.compile(r'^Total transferred file size: 0 bytes$')
    changed = True
    for line in stdout.split('\n'):
        line = line.strip()
        if zero_transfer_regexp.match(line):
            changed = False
            break
    return changed


def chown(remote_filename, owner, group):
    """Chown remote file.

    Args:
        remote_filename: Remote file name, must be absolute.
        owner: set user of remote file.
        group: set group of remote file.

    Returns:
        True if user or group of remote file is changed, False otherwise.
    """
    if not os.path.isabs(remote_filename):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('chown: remote path \'%s\' must be absolute in file %s line %s' % (remote_filename, fname, nline))
    with settings(hide('everything')):
        stdout = run('chown --changes ' + owner.strip() + ':' + group.strip() + ' -- ' + remote_filename)
        changed = stdout != ""
        return changed


def chmod(remote_filename, mode):
    """Chmod remote file.

    .. warning::
        If mode is number it must be octal constant, e.t. with leading zero.
        For example, 0755 and not 755, because decimal 755 == 01363.

    Args:
        remote_filename: Remote file name, must be absolute.
        mode: set mode of remote file. Can be string or number.

    Returns:
        True if mode of remote file is changed, False otherwise.
    """
    if not os.path.isabs(remote_filename):
        fname = str(inspect.stack()[1][1])
        nline = str(inspect.stack()[1][2])
        abort('chmod: remote path \'%s\' must be absolute in file %s line %s' % (remote_filename, fname, nline))
    if isinstance(mode, numbers.Number):
        mode = oct(mode)
    with settings(hide('everything')):
        stdout = run('chmod --changes ' + mode + ' -- ' + remote_filename)
        changed = stdout != ""
        return changed
