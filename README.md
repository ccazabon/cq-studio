# `cq-studio`

`cq-studio` is a server and utilities for running a live, updating preview of
objects designed in [CadQuery](https://cadquery.readthedocs.io/), rendered in 
your web browser.  CadQuery is a package for designing 3D models 
programmatically using Python code.

The web client side uses three.js to render the user's models.  The client-side
interface and HTTP server are supplied by the 
[yacv-server package](https://github.com/yeicor-3d/yet-another-cad-viewer/).

`cq-studio` starts a server, loads objects from a specified file, and then 
re-loads them on any change to that file or other Python modules it imports, 
and pushes the new objects to the browser ("hot-reloading").

## License

`cq-studio` is Copyright © 2024 Charles Cazabon <charlesc-software-cqs@pyropus.ca>.
Licensed under the GNU General Public License v2 (only).  See the file COPYING 
for details.

## Documentation

The documentation is available in HTML and plaintext in the `docs` subdirectory,
or online at https://pyropus.ca/docs/cq-studio/ .
