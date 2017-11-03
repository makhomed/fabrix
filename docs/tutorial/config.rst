.. meta::
    :description: Fabrix configuration tutorial

Configuration
-------------

Hosts
~~~~~

For example, consider simple ``fabfile.py``:

.. code-block:: python

    from fabric.api import env

    env.hosts = ['example.com', 'example.net', 'example.org']

    conf_name = 'World'

    def hello():
        print "Hello, %s!" % conf_name
        print

After running command ``fab hello`` we will se such output:

.. code-block:: none

    $ fab hello
    [example.com] Executing task 'hello'
    Hello, World!

    [example.net] Executing task 'hello'
    Hello, World!

    [example.org] Executing task 'hello'
    Hello, World!

But this approach with mixing code and configuration in one file
has many disadvantages for configuration management.

For example, it is impossible to share code of tasks
without necessity to edit fabfile and replace
hardcoded production configuration with example values.

Fabrix provides ability to easy separate code and configuration.

For example, configuration file ``fabfile.yaml``, without any code:

.. code-block:: yaml

    hosts:
      - example.com
      - example.net
      - example.org

    defaults:
      name: World

``hosts`` list from yaml configuration will be used
to set internal Fabric variable ``env.hosts``
before running any tasks.

Block ``defaults`` define default variables,
it will have same values for all hosts.
If specific hosts need different variable value
- it can be easy overriden in configuration file.

And updated ``fabfile.py`` with only code, without any configuration:

.. code-block:: python

    from fabrix.api import conf

    def hello():
        print "Hello, %s!" % conf.name
        print

After runnig ``fab hello`` we will see the same output as above.

During startup Fabrix library look for yaml configuration file
with same name as fabile, but with extension ``'.yaml'``.
If such configuration file exists it will be automatically
loaded, parsed and this configuration will be used for running tasks.

:obj:`~fabrix.config.conf` is special dict-like object,
which hold all configuration for current host during execution of task.

To illustrate how :obj:`~fabrix.config.conf` work lets change
configuration file ``fabfile.yaml``:

.. code-block:: yaml

    hosts:
      - example.com
      - example.net
      - example.org

    host_vars:
      - host: example.com
        vars:
          name: Foo

    defaults:
      name: World

Code in ``fabfile.py`` not changed, and remain the same as for previous example:

.. code-block:: python

    from fabrix.api import conf

    def hello():
        print "Hello, %s!" % conf.name
        print

After running ``fab hello`` we can see such result:

.. code-block:: none

    $ fab hello
    [example.com] Executing task 'hello'
    Hello, Foo!

    [example.net] Executing task 'hello'
    Hello, World!

    [example.org] Executing task 'hello'
    Hello, World!

For host ``example.com`` configuration variable ``name`` changed
from default value to ``Foo``, but for two rest hosts
variable ``name`` remain the same as default value.

We can see how configuration inheritance work
and how work ability to override variables for specific hosts.


Roles
~~~~~

Lets consider `roles example from Fabric documentation <http://docs.fabfile.org/en/1.14/usage/execution.html#intelligently-executing-tasks-with-execute>`_:

.. code-block:: python

    from fabric.api import env, run, roles, execute

    env.roledefs = {
        'db': ['db1', 'db2'],
        'web': ['web1', 'web2', 'web3'],
    }

    @roles('db')
    def migrate():
        # Database stuff here.
        pass

    @roles('web')
    def update():
        # Code updates here.
        pass

    def deploy():
        execute(migrate)
        execute(update)

We can separate code from configuration in this case too.

Code, ``fabfile.py``:

.. code-block:: python

    from fabric.api import env, run, roles, execute
    from fabrix.api import conf

    @roles('db')
    def migrate():
        print "Hello, %s!" % conf.name
        pass

    @roles('web')
    def update():
        print "Hello, %s!" % conf.name
        pass

    def deploy():
        execute(migrate)
        execute(update)

Configuration, ``fabrile.yaml``:

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

We can see what hosts from role ``db`` use default value
of variable ``name``, host ``web1`` use host-specific value
and all other hosts use values from ``role_vars`` definition for role ``web``.

Use different configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How to use same fabfile with different configuration files?
It is easy. We can use function :func:`~fabrix.config.read_config`:

.. code-block:: python

    from fabric.api import env, run, roles, execute
    from fabrix.api import conf, read_config

    @roles('db')
    def migrate():
        print "Hello, %s!" % conf.name
        pass

    @roles('web')
    def update():
        print "Hello, %s!" % conf.name
        pass

    def stage():
        read_config('stage.yaml')

    def prod():
        read_config('prod.yaml')

    def deploy():
        execute(migrate)
        execute(update)

If we execute command ``fab stage deploy`` task ``deploy``
will be runned with configuration from ``stage.yaml``.

If we execute command ``fab prod deploy`` task ``deploy``
will be runned with configuration from ``prod.yaml``.

Configuration file ``stage.yaml``:

.. code-block:: yaml

    roles:
      - role: db
        hosts:
          - stage-db
      - role: web
        hosts:
          - stage-web

    defaults:
      name: stage

Result of execution ``fab stage deploy``:

.. code-block:: none

    $ fab stage deploy
    [stage-db] Executing task 'migrate'
    Hello, stage!
    [stage-web] Executing task 'update'
    Hello, stage!

Configuration file ``prod.yaml``:

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

    defaults:
      name: prod

Result of execution ``fab prod deploy``:

.. code-block:: none

    $ fab prod deploy
    [db1] Executing task 'migrate'
    Hello, prod!
    [db2] Executing task 'migrate'
    Hello, prod!
    [web1] Executing task 'update'
    Hello, prod!
    [web2] Executing task 'update'
    Hello, prod!
    [web3] Executing task 'update'
    Hello, prod!

