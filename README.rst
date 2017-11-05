Fabrix
======

**Fabrix** is `Fabric <http://www.fabfile.org/>`_ extension for configuration management.

.. image:: https://travis-ci.org/makhomed/fabrix.svg?branch=master
    :target: https://travis-ci.org/makhomed/fabrix

.. image:: https://codecov.io/gh/makhomed/fabrix/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/makhomed/fabrix

.. image:: https://readthedocs.org/projects/fabrix/badge/
    :target: https://fabrix.readthedocs.io/

.. image:: https://badge.fury.io/py/Fabrix.svg
    :target: https://badge.fury.io/py/Fabrix

Installation
------------

.. code-block:: bash

    pip install -U fabrix

Links
-----

* `Fabrix Documentation <https://fabrix.readthedocs.io/>`_
* `Fabrix GitHub Home Page <https://github.com/makhomed/fabrix>`_
* `Fabrix Python Package Index <https://pypi.python.org/pypi/Fabrix>`_

Examples
--------

Using Jinja2 templates
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fabrix.api import render

    def hello():
        print render("Hello, {{ name }}!", name="World")

Editing systemd unit files
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fabrix.api import systemctl_edit, systemctl_restart

    def example():
        changed = systemctl_edit("mysqld.service", """
            [Service]
            LimitNOFILE = 262144
        """)
        if changed:
            systemctl_restart("mysqld.service")

Editing configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Installing PHP 7.0 from remi repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fabrix.api import is_file_exists, yum_install
    from fabrix.api import edit_file, edit_ini_section, replace_line

    def install_php():

        if not is_file_exists("/etc/yum.repos.d/epel.repo"):
            yum_install("https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm")

        if not is_file_exists("/etc/yum.repos.d/remi-php70.repo"):
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

Using external configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration file ``fabfile.yaml``:

.. code-block:: yaml

    roles:
      - role: db
        hosts:
          - db1
          - db2
      - role: web
        hosts:
          - web1
          - web2
          - web3

    role_vars:
      - role: web
        vars:
          name: webserver

    host_vars:
      - host: web1
        vars:
          name: nginx

    defaults:
      name: generic

Code ``fabfile.py``:

.. code-block:: python

    from fabric.api import env, run, roles, execute
    from fabrix.api import conf

    @roles("db")
    def migrate():
        print "Hello, %s!" % conf.name
        pass

    @roles("web")
    def update():
        print "Hello, %s!" % conf.name
        pass

    def deploy():
        execute(migrate)
        execute(update)

After running ``fab deploy`` we can see:

.. code-block:: none

    $ fab deploy
    [db1] Executing task 'migrate'
    Hello, generic!
    [db2] Executing task 'migrate'
    Hello, generic!
    [web1] Executing task 'update'
    Hello, nginx!
    [web2] Executing task 'update'
    Hello, webserver!
    [web3] Executing task 'update'
    Hello, webserver!

More details and examples you can see in `Fabrix Documentation <https://fabrix.readthedocs.io/>`_.

