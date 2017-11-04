.. meta::
    :description: Fabrix template rendering tutorial

Template rendering
------------------

We can render template from template file with function :func:`~fabrix.render.render_template`
or render template from string template with function :func:`~fabrix.render.render`.

Templates rendered via `Jinja2 <https://pypi.python.org/pypi/Jinja2>`_.

:obj:`~fabrix.config.conf` used as default context for template rendering
if ``env.host_string`` is not empty.

If ``env.host_string`` is empty then :obj:`~fabrix.config.local_conf` used as default context.

You can override these default values of template context by explicit arguments.

For example, ``fabfile.py``:

.. code-block:: python

    from fabrix.api import render

    def hello():
        print render("Hello, {{ name }}!", name="World")

After executing command :command:`fab hello` we can see:

.. code-block:: none

    $ fab hello
    Hello, World!

Second example, using template file. In directory with ``fabfile.py``
we create subdirectory ``templates`` with file ``hello.txt.j2`` inside it.
Contents of file ``templates/hello.txt.j2``:

.. code-block:: jinja

    Hello, {{ name }}!

And ``fabfile.py``:

.. code:: python

    from fabrix.api import render_template

    def hello():
        print render_template("hello.txt.j2", name="World")

After executing command :command:`fab hello` we can see:

.. code-block:: none

    $ fab hello
    Hello, World!

Functions :func:`~fabrix.render.render_template` and :func:`~fabrix.render.render`
intended for using with functions  :func:`~fabrix.ioutil.write_file` and :func:`~fabrix.ioutil.write_local_file`.

For example:

.. code-block:: python

    from fabrix.api import write_file, render_template

    def example():
        write_file("/path/to/example.conf",
            render_template("example.conf.j2", key="value")
        )

