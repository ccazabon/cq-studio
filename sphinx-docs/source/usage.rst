Use
===

Short version
-------------

#. Create a Python file with a ``main()`` method that takes no arguments, and which
   returns your CadQuery model(s).  The return type can be a single object, a
   list of objects, or a dictionary of names and objects.  A dictionary is
   preferred so that you get meaningful names displayed in the viewer for your models.
#. Run ``cq-studio /path/to/your/model-file.py``.
#. Point your browser at http://127.0.0.1:32323/ and
   view your model(s).  You can select which objects to show, whether to show
   faces, edges, vertices, or any combination for each object, adjust 
   transparency and other properties.  You can experiment with a `demo of the
   viewer (which comes from the YACV package) here <https://yeicor-3d.github.io/yet-another-cad-viewer/?autoplay=false&preload=logo.glb&preload=logo_hl.glb&preload=fox.glb&preload=img.jpg.glb&preload=location.glb>`_.
#. Edit your Python file to modify your CadQuery model(s) and save it; the
   changes will be pushed to the viewer in your browser.
#. If errors are encountered (bad Python code, or CadQuery cannot handle what
   you're asking it to do), they will be printed to the console where you
   started ``cq-studio``, and it will then wait for the files to change again
   and reload them.

Use ctrl-c in the terminal you're running ``cq-studio`` in to stop the server.

Details
-------

The ``cq-studio`` server takes some options, which you can see using the ``--help``
option or by running it with no arguments::

    Usage: cq-studio [OPTIONS] MODEL_FILE

      Copyright © 2024 Charles Cazabon <charlesc-software@pyropus.ca>.

      Licensed under the GNU General Public License v2 (only).  See the file
      COPYING for details.

    Options:
      -a, --address IP-ADDRESS        listen on ADDRESS  [default: 127.0.0.1]
      -p, --port PORT                 listen on PORT  [default: 32323;
                                      1<=x<=65535]
      -i, --poll-interval INTERVAL    poll for changed files every INTERVAL
                                      seconds  [default: 1.0; 0.1<=x<=2.0]
      -o, --axes-origin / -O, --no-axes-origin
                                      show axes and orientation at origin
                                      [default: axes-origin]
      -e, --export-models / -E, --no-export-models
                                      generate STL model files from loaded objects
                                      [default: export-models]
      -x, --exclude-dir DIR           exclude directories from watching for
                                      changes (use multiple times)  [default:
                                      .venv, .git]
      -v, --verbose                   operate more verbosely (use multiple times)
      -q, --quiet                     operate less verbosely
      --help                          Show this message and exit.


*Note: the ``--address`` and ``--port`` options are provisional and can't be used
at present.  While they do actually affect the address and port the server binds
to, the front-end JavaScript code has the default values hardcoded, and so will
only try to contact http://127.0.0.1:32323/ to obtain the models for rendering.*
                                                        
By default, ``cq-studio`` adds a small 3-bar object, named ``origin``, at the
(0, 0, 0) origin of the workspace to indicate the position and direction (positive)
of the axes.  You can suppress this be running with the ``--no-axes-origin`` option.

By default, ``cq-studio`` will export the models returned by your code to STL
files in the current working directory whenever the models change.  You can 
suppress this with the ``--no-export-models`` option.  If you generally want
to create model files, but not for specific model objects, you can set
``<object>.export_stl`` to ``False``.

By default, ``cq-studio`` will print a few types of messages to the console when
running, indicating when it has detected changes in the code files or modules
imported by those files.  You can suppress this with the ``--quiet`` option,
which will result in only errors being reported on the console.  Higher 
verbosity is generally only useful for debugging ``cq-studio`` itself.

``cq-studio`` will ignore files (when watching for updates) under a given
directory with the ``--exclude-dir`` option.  This can be given multiple times to
ignore more than one directory.  By default, ``.git`` and ``.venv`` directories are
ignored; specifying this option will override that default.

Viewer Interface
----------------

By default, all faces/edges/vertices of the objects are shown:

.. image:: images/view-1.png
    :alt: The YACV (Yet Another Cad Viewer) browser interface, showing a view of the
        parts of a 3D printer system, with the top plate removed.

Clicking the arrow at the bottom-left of the viewer expands a control panel:

.. image:: images/view-2.png
    :alt: The same view as above, but with the left control panel of the YACV viewer expanded,
        showing the list of objects being rendered, along with controls for setting the visibility
        of various elements.

Clicking on the name of an object will expand controls allowing you to set transparency and
other settings for that object.

For example, you can disable rendering of the faces of an object, showing only its edges and
vertices, so that it is transparent:

.. image:: images/view-3.png
    :alt: The same view as previously, but two of the objects have had face rendering deselected,
        so that they are shown with only their edges rendered as lines, ghost-like, allowing
        what is behind them to be seen.

Another view, with the main body of the printer transparent by disabling rendering of faces
on that object:

.. image:: images/view-4.png
    :alt: Another view with additional objects set to not render faces.

Example Project
===============

There is an example project located in the ``example_project`` subdirectory.
Run ``cq-server example_project/project.py`` and point your browser at http://127.0.0.1:32323/ .

The example project included with ``cq-studio`` looks like this:

.. image:: images/example-project.png
    :alt: An example CadQuery project being displayed in ``cq-studio``.  It consists of a colourful
        block with four screwholes at the corners, a large hole in the center with a floating sphere
        in the middle, and a long rod running through the sphere at an angle.  There are screws or
        pins floating exploded-diagram-style above the holes they fit in.

Expanding the left control panel and clicking on the ``block`` item expands the controls for that
object.  In addition to the face, edge, and vertex visibility toggles, there are sliders for the
transparency/opacity of the object, the prominence or rendering size of its edges and vertices,
and the ability to set a clipping plane anywhere on the ``X``, ``Y``, or ``Z`` axes.

Here you can see the block's opacity reduced so that the sphere and rod can be seen through it:

.. image:: images/example-project-object-transparency.png
    :alt: The same model scene as above, with the colourful block object having a roughly 50%
        transparency value applied.
