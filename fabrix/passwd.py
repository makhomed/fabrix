import os.path
from fabrix.ioutil import run, chmod, chown, create_directory, create_file, read_local_file
from fabrix.editor import edit_file, append_line


def get_user_home_directory(name):
    """get user home directory

    Args:
        name: user name

    Returns:
        Home directory if user exists or None if user not exists.
    """
    passwd = run("getent passwd")
    for line in passwd.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.split(":")[0] == name:
            return line.split(":")[5]
    return None


def add_user_ssh_authorized_keys(username, ssh_authorized_keys_filename):
    """add records to user ~/.ssh/authorized_keys file

    Args:
        username: user name
        ssh_authorized_keys_filename: name of local file with ssh authorized keys to add
    """
    home_directory = get_user_home_directory(username)
    ssh_directory = os.path.join(home_directory, ".ssh")
    create_directory(ssh_directory)
    chown(ssh_directory, username, username)
    chmod(ssh_directory, 0700)
    authorized_keys = os.path.join(ssh_directory, "authorized_keys")
    create_file(authorized_keys)
    chown(authorized_keys, username, username)
    chmod(authorized_keys, 0600)
    keys = read_local_file(ssh_authorized_keys_filename)
    for key in keys.split("\n"):
        key = key.strip()
        if not key:
            continue
        edit_file(authorized_keys, append_line(key, insert_empty_line_before=True))


def is_user_exists(name):
    """is user exists?

    Args:
        name: user name

    Returns:
        True if user exists, False if user not exists.
    """
    passwd = run("getent passwd")
    for line in passwd.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.split(":")[0] == name:
            return True
    return False


def is_user_not_exists(name):
    """is user not exists?

    Args:
        name: user name

    Returns:
        True if user not exists, False if user exists.
    """
    return not is_user_exists(name)


def create_user(name):
    """create user if it not exists
    """
    if is_user_not_exists(name):
        run("useradd %s --comment %s" % (name, name))


def remove_user(name):
    """remove user if it exists
    """
    if is_user_exists(name):
        run("userdel %s" % name)


def is_group_exists(name):
    """is group exists?

    Args:
        name: group name

    Returns:
        True if group exists, False if group not exists.
    """
    group = run("getent group")
    for line in group.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.split(":")[0] == name:
            return True
    return False


def is_group_not_exists(name):
    """is group not exists?

    Args:
        name: group name

    Returns:
        True if group not exists, False if group exists.
    """
    return not is_group_exists(name)


def create_group(name):
    """create group if it not exists
    """
    if is_group_not_exists(name):
        run("groupadd %s" % name)


def remove_group(name):
    """remove group if it exists
    """
    if is_group_exists(name):
        run("groupdel %s" % name)


def is_user_in_group(username, groupname):
    """is user in group?
    """
    group = run("getent group")
    for line in group.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.split(":")[0] == groupname:
            members = line.split(":")[3].split(",")
            return username in members
    return False


def is_user_not_in_group(username, groupname):
    """is user not in group?
    """
    return not is_user_in_group(username, groupname)


def add_user_to_group(username, groupname):
    """add user to group
    """
    if is_user_not_in_group(username, groupname):
        run("gpasswd --add %s %s" % (username, groupname))


def delete_user_from_group(username, groupname):
    """delete user_from group
    """
    if is_user_in_group(username, groupname):
        run("gpasswd --delete %s %s" % (username, groupname))
