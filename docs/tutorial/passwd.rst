.. meta::
    :description: Fabrix package management tutorial

.. _tutorial-passwd:

User/Group management
---------------------

Functions :func:`~fabrix.passwd.is_user_exists` and :func:`~fabrix.passwd.is_user_not_exists`
can be used to check exists or not exists user.

Functions :func:`~fabrix.passwd.is_group_exists` and :func:`~fabrix.passwd.is_group_not_exists`
can be used to check exists or not exists group.

Functions :func:`~fabrix.passwd.create_user` and :func:`~fabrix.passwd.remove_user`
can be used for creating and removing users.

Functions :func:`~fabrix.passwd.create_group` and :func:`~fabrix.passwd.remove_group`
can be used for creating and removing groups.

Functions :func:`~fabrix.passwd.is_user_in_group` and :func:`~fabrix.passwd.is_user_not_in_group`
can be used to check is user in additional group or is user not in additional group.

Functions :func:`~fabrix.passwd.add_user_to_group` and :func:`~fabrix.passwd.delete_user_from_group`
can be used for adding user to group and for deleting user from group.

Function :func:`~fabrix.passwd.get_user_home_directory` return user home directory
from /etc/passwd file or return None if such user not exists.

Function :func:`~fabrix.passwd.add_user_ssh_authorized_keys` can be used for adding
authorized public keys to user authorized_keys file located in .ssh directory in home directory.

.. seealso::
    :ref:`User/Group management Reference <reference-passwd>`

