.. meta::
    :description: Fabrix package management tutorial

Package management
------------------

We can install packages with function :func:`~fabrix.rpmyum.yum_install`,
remove packages with function :func:`~fabrix.rpmyum.yum_remove`
and we can update already installed packages with function
:func:`~fabrix.rpmyum.yum_update`.

Functions :func:`~fabrix.rpmyum.yum_install` and :func:`~fabrix.rpmyum.yum_remove`
requires at least one argument, function :func:`~fabrix.rpmyum.yum_update`
can be called without arguments, in this case it update all installed packages.

Argument can be string with package names separated with whitespace characters.

Or argument can be iterable of such strings or any combinations of such strings and iretables.

For example:

.. code-block:: python

    from fabrix.api import yum_install

    def example():

        base_packages = set(("mc", "postfix", "vim", "screen", "htop"))

        php_packages = """php-cli php-common php-fpm php-gd php-mbstring
                php-mysql php-pdo php-pear php-pecl-imagick php-process
                php-xml php-opcache php-mcrypt php-soap"""

        all_packages = list(("crond", base_packages, php_packages))

        yum_install(all_packages, "net-tools mysql man")

