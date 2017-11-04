
.. meta::
    :description: Fabrix installation

.. _installation:

Installation
============

Fabrix
------

For using Fabrix you need to have Python 2.7 with `setuptools <https://pypi.python.org/pypi/setuptools>`_ and `pip <https://pypi.python.org/pypi/pip>`_ installed.

Installation of stable version of Fabrix is easy::

    pip install -U fabrix

If you want to use development version of Fabrix::

    pip install -U git+https://github.com/makhomed/fabrix/#egg=fabrix

If you need to uninstall Fabrix::

    pip uninstall fabrix

Python
------

* Python 2.7 is required.
* Python 3.x not supported, because `Fabric requires Python 2.5-2.7 <http://www.fabfile.org/installing.html#python>`_

Dependencies
------------

These Fabrix dependencies will be installed automatically:

* `Fabric <https://pypi.python.org/pypi/Fabric>`_
* `Jinja2 <https://pypi.python.org/pypi/Jinja2>`_
* `PyYAML <https://pypi.python.org/pypi/PyYAML>`_

Development dependencies
------------------------

For development you need additional dependencies:

* `git <https://git-scm.com/>`_
* `pytest <https://pypi.python.org/pypi/pytest>`_
* `pytest-cov <https://pypi.python.org/pypi/pytest-cov>`_
* `coverage <https://pypi.python.org/pypi/coverage>`_
* `codecov <https://pypi.python.org/pypi/codecov>`_
* `flake8 <https://pypi.python.org/pypi/flake8>`_
* `tox <https://pypi.python.org/pypi/tox>`_
* `Sphinx <https://pypi.python.org/pypi/Sphinx>`_

Downloads
---------

To obtain a tar.gz archive of the Fabrix source code, you may visit
`Fabrix PyPI page <https://pypi.python.org/pypi/Fabrix>`_,
which offers manual downloads.

Source code checkouts
---------------------

To follow Fabrix development via Git instead of downloading official releases,
you can clone the canonical repository straight from
`the Fabrix repository on GitHub <https://github.com/makhomed/fabrix>`_.

.. seealso::
    * :ref:`Overview <overview>`
    * Installation
    * :ref:`tutorial`
    * :ref:`reference`
    * :ref:`changelog`

