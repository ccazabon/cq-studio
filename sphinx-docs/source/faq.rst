FAQ
===

Why use this instead of just using the YACV / yacv-server package?
------------------------------------------------------------------

That package is mostly designed for use in a Jupyter notebook, rendering updates
in a cell after you make changes elsewhere in the notebook.  If you are a 
programmer (or even if you're not), you might prefer working in a proper text
editor, and you just need a (preferably live) viewer for the models you are
creating.

This is similar to the way you use OpenSCAD (with its own editor, or an external
one).  YACV provides a much better interactive viewer than OpenSCAD does, but
doesn't natively support this persistent mode.

The CadQuery documentation recommends using CQ-editor as a GUI 
editor-and-viewer, but that application appears to be more-or-less abandonware,
and is not packaged in a way that makes sense for an ordinary user to install.
Using ``cq-studio`` means you get the advantages of an interactive viewer with
many features and fast response/rendering, with the ability to use any text
editor or IDE you like.

This documentation is pretty generic looking, isn't it?
-------------------------------------------------------

Yes, this is using the default `Sphinx <https://www.sphinx-doc.org/>`_ HTML theme.
That is because I am a software engineer, not a graphic designer.

Calling this "cq-studio" - that's kind of pretentious, isn't it?
----------------------------------------------------------------

Please see `computer science hard thing #2 <https://martinfowler.com/bliki/TwoHardThings.html>`_.

Help!  Or, I found a bug!  Or, I Need a Feature!
------------------------------------------------

This project is at an early stage.  I have not yet created my typical copious quantity of
documentation and support resources for it.  If ``cq-studio`` becomes popular, I might have to
do that.

In the meantime, you can open an issue on Github, or email me at the address in the
``pyproject.toml`` file or the installed package's metadata file
(``<venv>/lib/python<VERSION>/site-packages/cq_studio-<VERSION>.dist-info/METADATA``).
