Installation
============

Short version
-------------

Use ``pipx install cq-studio``

You can probably install `pipx <https://pypi.org/project/pipx/>`_ from your
system's standard software repositories, if it isn't already installed.

Details
-------

The recommended way to install ``cq-studio`` is inside a virtual environment, so
that it cannot affect any Python code from other programs you may have installed
on your system.  Using ``pipx`` above creates a virtual environment just for
``cq-studio`` that cannot interfere with your project virtual environment or
system-wide Python installations.

As an alternative, you can also install ``cq-studio`` in your project virtual
environment like any other Python dependency (with ``uv``, ``poetry``, ``pip``,
etc).

You can also download and install the package manually, but it won't give you
anything you wouldn't get from the above methods.  

``cq-studio`` requires Python version 3.10 or later.
