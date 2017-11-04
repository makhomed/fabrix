.. meta::
    :description: Fabrix system management tutorial

.. _tutorial-system:

System management
-----------------

We can start and stop services with functions
:func:`~fabrix.system.systemctl_start`
and :func:`~fabrix.system.systemctl_stop`.

Also we can reload and restart services with functions
:func:`~fabrix.system.systemctl_reload`
and :func:`~fabrix.system.systemctl_restart`.

Services can be enabled and disabled with functions
:func:`~fabrix.system.systemctl_enable`
and :func:`~fabrix.system.systemctl_disable`.

Also services can be masked and unmasked with functions
:func:`~fabrix.system.systemctl_mask`
and :func:`~fabrix.system.systemctl_unmask`.

Service unit files can be edited with function
:func:`~fabrix.system.systemctl_edit`.

For example:

.. code-block:: python

    from fabrix.api import systemctl_edit

    def example():
        systemctl_edit("mysqld.service", """
            [Service]
            LimitNOFILE = 262144
        """)

This example creates on remote machine file
:file:`/etc/systemd/system/mysqld.service.d/override.conf`
with contents:

.. code-block:: none

    [Service]
    LimitNOFILE = 262144

If you need to remove override.conf created by
:func:`~fabrix.system.systemctl_edit` function
or by :command:`systemctl edit` command - just
call function :func:`~fabrix.system.systemctl_edit`
with second parameter ``None`` or empty string.

For example:

.. code-block:: python

    from fabrix.api import systemctl_edit

    def example():
        systemctl_edit("mysqld.service", None)

This code removes file
:file:`/etc/systemd/system/mysqld.service.d/override.conf`
and removes empty directory :file:`/etc/systemd/system/mysqld.service.d`.


With functions :func:`~fabrix.system.systemctl_get_default`
and :func:`~fabrix.system.systemctl_set_default` we can
get and set default target.

For example:

.. code-block:: python

    from fabrix.api import systemctl_get_default, systemctl_set_default

    def example():
        systemctl_set_default("multi-user.target")
        print systemctl_get_default()


Functions :func:`~fabrix.system.localectl_set_locale`
and :func:`~fabrix.system.timedatectl_set_timezone`
we can use for setting locale and timezone.

.. code-block:: python

    from fabrix.api import localectl_set_locale, timedatectl_set_timezone

    def example():
        localectl_set_locale("LANG=en_US.UTF-8")
        timedatectl_set_timezone("Europe/Kiev")


Function :func:`~fabrix.system.disable_selinux`
can be used for disablong SELinux on remote machine.

Function :func:`~fabrix.system.get_virtualization_type`
returns None if no virtualization detected, or virtualization type
as string, for example, "openvz", "kvm" or something else.

Function :func:`~fabrix.system.is_reboot_required` returns True
if remote system requires reboot after yum update.

Function :func:`~fabrix.system.reboot_and_wait` reboots remove system.

.. seealso::
    :ref:`System management Reference <reference-system>`

