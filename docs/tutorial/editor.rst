.. meta::
    :description: Fabrix editor functions tutorial

.. _tutorial-editor:

Editor functions
----------------

For configuration management we need ability to edit configuration files.
Fabrix provide several functions for this.

We can edit local files with function :func:`~fabrix.editor.edit_local_file`
and we can edit remote files with function :func:`~fabrix.editor.edit_file`.
These functions return True if edited file changed and False otherwise.

For example, we have file :file:`/etc/default/grub` on remote host ``example.com``:

.. code-block:: bash

    GRUB_TIMEOUT=5
    GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
    GRUB_DEFAULT=saved
    GRUB_DISABLE_SUBMENU=true
    GRUB_TERMINAL_OUTPUT="console"
    GRUB_CMDLINE_LINUX="rd.lvm.lv=lv/root nomodeset rhgb quiet"
    GRUB_DISABLE_RECOVERY="true"

Configuration :file:`fabfile.yaml`:

.. code-block:: yaml

    hosts:
        - example.com

Code :file:`fabfile.py`:

.. code-block:: python

    from fabric.api import run
    from fabrix.api import edit_file, replace_line, substitute_line, strip_line

    def edit_grub():
        changed = edit_file("/etc/default/grub",
            replace_line(r"GRUB_TIMEOUT=.*", r"GRUB_TIMEOUT=1"),
            replace_line(r"(GRUB_CMDLINE_LINUX=.*)\brhgb\b(.*)", r"\1selinux=0\2"),
            replace_line(r"(GRUB_CMDLINE_LINUX=.*)\bquiet\b(.*)", r"\1panic=1\2"),
            substitute_line(r"\s+", r" "),
            strip_line(),
        )
        if changed:
            run("grub2-mkconfig -o /boot/grub2/grub.cfg")

After execution command :command:`fab edit_grub` we got file :file:`/etc/default/grub`:

.. code-block:: bash

    GRUB_TIMEOUT=1
    GRUB_DISTRIBUTOR="$(sed 's, release .*$,,g' /etc/system-release)"
    GRUB_DEFAULT=saved
    GRUB_DISABLE_SUBMENU=true
    GRUB_TERMINAL_OUTPUT="console"
    GRUB_CMDLINE_LINUX="rd.lvm.lv=lv/root nomodeset selinux=0 panic=1"
    GRUB_DISABLE_RECOVERY="true"

Second example. We need to install PHP 7.0 from remi repo on host ``example.com``.

Configuration :file:`fabfile.yaml`:

.. code-block:: yaml

    hosts:
        - example.com

Code :file:`fabfile.py`:

.. code-block:: python

    from fabrix.api import is_file_not_exists, yum_install
    from fabrix.api import edit_file, edit_ini_section, replace_line

    def install_php():

        if is_file_not_exists("/etc/yum.repos.d/epel.repo"):
            yum_install("https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm")

        if is_file_not_exists("/etc/yum.repos.d/remi-php70.repo"):
            yum_install("https://rpms.remirepo.net/enterprise/remi-release-7.rpm")

        edit_file("/etc/yum.repos.d/remi-php70.repo",
            edit_ini_section("[remi-php70]",
                replace_line("enabled=0", "enabled=1")
            )
        )

        yum_install("""
                php-cli
                php-common
                php-fpm
                php-gd
                php-mbstring
                php-mysql
                php-pdo
                php-pear
                php-pecl-imagick
                php-process
                php-xml
                php-opcache
                php-mcrypt
                php-soap
        """)

**All editor functions**:

    - :func:`~fabrix.editor.edit_local_file`
    - :func:`~fabrix.editor.edit_file`

    - :func:`~fabrix.editor.edit_ini_section`
    - :func:`~fabrix.editor.edit_text`

    - :func:`~fabrix.editor.append_line`
    - :func:`~fabrix.editor.prepend_line`

    - :func:`~fabrix.editor.delete_line`
    - :func:`~fabrix.editor.insert_line`

    - :func:`~fabrix.editor.replace_line`
    - :func:`~fabrix.editor.substitute_line`

    - :func:`~fabrix.editor.strip_line`
    - :func:`~fabrix.editor.strip_text`

.. seealso::
    :ref:`Editor functions Reference <reference-editor>`

