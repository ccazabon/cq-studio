"""
cq-studio is Copyright © 2024 Charles Cazabon <charlesc-software-cqs@pyropus.ca>.
Licensed under the GNU General Public License v2 (only).  See the file COPYING for details.
"""

import datetime
import functools
import importlib
import os
import pathlib
import sys
import time
import traceback
import types
from typing import Any

# Otherwise YACV starts a server process when the module is imported
os.environ["YACV_DISABLE_SERVER"] = "1"

# flake8: noqa: E402
import build123d
import cadquery as cq
import click
from yacv_server import YACV

from cq_studio.constants import LogLevel
from cq_studio.defaults import defaults
from cq_studio.reloader import Reloader


class Server:
    def __init__(
        self,
        model_file: pathlib.Path,
        poll_interval: float,
        excluded_dirs: list[pathlib.Path],
        log_level: LogLevel,
    ):
        assert log_level, log_level

        if not model_file.exists():
            raise ValueError(f"Model file {model_file} does not exist")
        elif not model_file.is_file():
            raise ValueError(
                f"Model path {model_file} exists but is not a regular file"
            )

        self.model_file = model_file.resolve()
        self.poll_interval = poll_interval
        self.log_level = log_level

        # Ensure the current working directory is in the module search path, in case the
        # user is serving a script using a module in a subdirectory/package.
        self.cwd = pathlib.Path.cwd().resolve()
        if self.cwd not in sys.path:
            sys.path.insert(0, str(self.cwd))

        # Exclude the Python stdlib.  Some modules get loaded from the system-wide copy
        # even when running in a venv, so do both if applicable.
        for prefix in {sys.prefix, sys.base_prefix}:
            platlibdir = (
                pathlib.Path(prefix)
                / sys.platlibdir
                / f"python{sys.version_info.major}.{sys.version_info.minor}"
            )
            assert platlibdir.is_dir(), platlibdir
            excluded_dirs.append(platlibdir)

        self.excluded_dirs = [p.resolve() for p in excluded_dirs]
        self.reloader = Reloader(self, self.excluded_dirs)

        self.last_files: set[pathlib.Path] | None = None
        self.last_updated: datetime.datetime | None = None
        self.last_import_error: list[str] | None = None

    def _output(self, log_level: LogLevel, *args: Any, **kwargs: Any) -> None:
        assert isinstance(log_level, LogLevel), f"{log_level=} {type(log_level)=}"
        assert isinstance(
            self.log_level, LogLevel
        ), f"{self.log_level=} {type(self.log_level)=}"

        if log_level.value < self.log_level.value:
            return
        kwargs.pop("file", None)
        print(
            *args,
            file=sys.stderr if log_level.value >= LogLevel.ERROR.value else sys.stdout,
            **kwargs,
        )

    def trace(self, *args: Any, **kwargs: Any) -> None:
        self._output(LogLevel.TRACE, *args, **kwargs)

    def debug(self, *args: Any, **kwargs: Any) -> None:
        self._output(LogLevel.DEBUG, *args, **kwargs)

    def info(self, *args: Any, **kwargs: Any) -> None:
        self._output(LogLevel.INFO, *args, **kwargs)

    def error(self, *args: Any, **kwargs: Any) -> None:
        self._output(LogLevel.ERROR, *args, **kwargs)

    def import_model_module(self):
        """Import the user's model file, and handle exceptions raised during the process."""
        self.trace(f"trying to load {self.model_file}")
        import_name = self.model_file.stem
        dir = self.model_file.parent
        while (dir / "__init__.py").is_file() and dir.parent != dir:
            import_name = f"{dir.name}.{import_name}"
            dir = dir.parent
        dir_str = str(dir)
        if dir_str not in sys.path:
            sys.path.insert(0, dir_str)
        self.trace(f"Generated import name '{import_name}', from dir '{dir}'")

        # If the user has added a new module since last time, there might be a cached
        # "no such module" entry, so invalidate the cache to start fresh.
        importlib.invalidate_caches()
        try:
            model_module = importlib.import_module(import_name)
            self.trace(f"Successfully imported {model_module}")
            self.last_files = self.reloader.find_files()
            self.last_updated = self.reloader.most_recent(self.last_files)
            self.last_import_error = None
            self.trace(f"loaded {model_module} {self.last_files=} {self.last_updated=}")
            return model_module
        except Exception as e:
            # force reload when any change after error
            self.last_files = None
            self.last_updated = None
            self.error(
                f"Error importing module {import_name} from {self.model_file}: {e}",
            )
            error = traceback.format_exception(e)
            if error == self.last_import_error:
                # stack trace hasn't changed, so don't clutter the user's console by logging it
                pass
            else:
                self.last_import_error = error
                for line in self.last_import_error:
                    self.error(f"  {line}", end="")
        self.trace(f"  ... failed to import {import_name}")
        return None

    def load_objects(self, model_module):
        """Load the exported CadQuery model objects from the user's model file."""
        if model_module is None:
            return None
        try:
            objects = model_module.main()
            if not objects:
                self.info("No objects loaded")
                return
            if isinstance(objects, dict):
                # already supplied with names by user
                pass
            elif isinstance(objects, list):
                # generate sequential names
                objects = dict(
                    [
                        (f"model-{partnum + 1}", model)
                        for (partnum, model) in enumerate(objects)
                    ]
                )
            else:
                # assume they returned a single CadQuery object/solid/compound
                objects = {
                    "model": objects,
                }
            self.trace(f"  ... loaded {len(objects)} objects: {sorted(objects)}")
            return objects
        except Exception as e:
            # :TODO: clear last_files/last_modtime ?
            self.error(
                f"Error loading objects from {model_module.__name__}: {e}",
            )
            trace = traceback.format_exception(e)
            for line in trace:
                self.error(f"  {line}", end="")
        return None

    def check_updated(self) -> bool:
        self.trace(f"Checking updated...")
        if not self.last_files or not self.last_updated:
            self.trace(f"  defaulting to true {self.last_files=} {self.last_updated=}")
            return True
        modtime = self.reloader.most_recent(self.last_files)
        self.trace(f"  {modtime != self.last_updated=} {modtime=} {self.last_updated=}")
        return modtime != self.last_updated

    def reload(self) -> types.ModuleType:
        self.reloader.unload()
        module = self.import_model_module()
        return module

    @functools.cached_property
    def axes_origin(self):
        # An object to show where the origin is in the viewport, as well as indicate the
        # orientation of the three axes.  A short 1x1x12 bar is placed on the positive side
        # of the origin on each of the axes, with a short stub of the bar pointing back in
        # the negative direction.
        wp = cq.Workplane()
        axes = (
            wp.box(12, 1, 1, centered=False).translate((-2, 0, 0))
            + wp.box(1, 12, 1, centered=False).translate((0, -2, 0))
            + wp.box(1, 1, 12, centered=False).translate((0, 0, -2))
        )
        axes.colour = defaults["axes-colour"]
        axes.export_stl = False
        return axes

    def wrap_cq_object(self, obj):
        """Wrap a CadQuery object in a b3d (build123d) one, which YACV server expects."""
        cq_part = obj.findSolid()
        try:
            d = cq_part.largestDimension()
            size = (d, d, d)
        except AttributeError:
            # Compound and various other objects don't have .largestDimension() method
            size = defaults["model-size"]
        b3d_part = build123d.Solid.make_box(*size)
        b3d_part.wrapped = cq_part

        # See if a colour was set on the part, or any of its ancestors, and apply it to the
        # b3d part so YACV uses it.
        colour = None
        obj_ = obj
        while obj_:
            if (colour := getattr(obj_, "colour", None)) or (
                colour := getattr(obj_, "color", None)
            ):
                break
            obj_ = obj_.parent
        b3d_part.color = colour

        return b3d_part

    def serve(self, axes_origin: bool, export_models: bool):
        """Begin serving models to the browser, and watching for changes to files to trigger
        reloading.
        """
        view_server = YACV()
        view_server.start()

        model_module_name = self.model_file.stem
        model_module = None

        while True:
            self.debug(".", end="", flush=True)

            if self.last_files is None:
                self.trace("No files to watch")
            else:
                self.trace(f"Watching {len(self.last_files)} files:")
                for file in self.last_files:
                    self.trace(f"  {file}")
                self.trace(f"  last mod time {self.last_updated}")

            try:
                updated = self.check_updated()
                if not model_module:
                    self.debug(f"loading from {self.model_file}")
                    model_module = self.import_model_module()
                elif updated:
                    self.info(f"reloading objects from {self.model_file}")
                    model_module = self.reload()
                else:
                    self.trace("not first load and not updated, sleeping...")
                    time.sleep(self.poll_interval)
                    continue
                if not model_module:
                    self.debug(f"failed to import from {self.model_file}, sleeping")
                    print(f"failed importing {self.model_file}, sleeping")
                    time.sleep(self.poll_interval)
                    continue

                objects = self.load_objects(model_module)
                if not objects:
                    self.debug("No objects loaded, sleeping")
                    time.sleep(self.poll_interval)
                    continue

                try:
                    num_objects = len(objects)
                except TypeError:
                    num_objects = 1
                self.trace(f"Loaded {num_objects} objects")

                if axes_origin:
                    # Add indicators for the three axes to help the user with orientation
                    # and centering
                    objects["origin"] = self.axes_origin

                if updated:
                    b3d_parts = {}
                    for name, obj in objects.items():
                        b3d_parts[name] = self.wrap_cq_object(obj)

                    # Show it in the frontend with hot-reloading
                    view_server.clear()
                    # view_server.show(*models, names=names)
                    view_server.show(*b3d_parts.values(), names=list(b3d_parts.keys()))

                    if export_models:
                        for name, obj in objects.items():
                            if not getattr(obj, "export_stl", True):
                                continue
                            model_ofile = (
                                pathlib.Path.cwd() / f"{model_module_name}-{name}.stl"
                            )
                            cq.exporters.export(obj, str(model_ofile), tolerance=0.0001)
                            self.info(f"Wrote {model_ofile}")

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                self.info("exiting")
                sys.exit(0)


@click.command(
    "run-server",
    help="""
Copyright © 2024 Charles Cazabon <charlesc-software@pyropus.ca>.

Licensed under the GNU General Public License v2 (only).  See the file COPYING for details.
""",
    no_args_is_help=True,
)
@click.argument(
    "model_file",
    type=click.Path(
        exists=True, dir_okay=False, file_okay=True, path_type=pathlib.Path
    ),
)
@click.option(
    "--address",
    "-a",
    type=str,
    # The frontend JS in YACV has this address hardcoded (and also the port), even though the
    # YACV server can be made to listen on an alternate port.
    default="127.0.0.1",
    show_default=True,
    metavar="IP-ADDRESS",
    help="listen on ADDRESS",
)
@click.option(
    "--port",
    "-p",
    type=click.IntRange(1, 65535),
    # The frontend JS in YACV has this port hardcoded (and also the address), even though the
    # YACV server can be made to listen on an alternate port.
    # default=8180,
    default=32323,
    show_default=True,
    metavar="PORT",
    help="listen on PORT",
)
@click.option(
    "--poll-interval",
    "-i",
    type=click.FloatRange(0.1, 2.0),
    default=1.0,
    show_default=True,
    metavar="INTERVAL",
    help="poll for changed files every INTERVAL seconds",
)
@click.option(
    "--axes-origin/--no-axes-origin",
    "-o/-O",
    default=True,
    show_default=True,
    help="show axes and orientation at origin",
)
@click.option(
    "--export-models/--no-export-models",
    "-e/-E",
    default=True,
    show_default=True,
    help="generate STL model files from loaded objects",
)
@click.option(
    "excluded_dirs",
    "--exclude-dir",
    "-x",
    type=click.Path(dir_okay=True, file_okay=False, path_type=pathlib.Path),
    multiple=True,
    default=[".venv", ".git"],
    show_default=True,
    metavar="DIR",
    help="exclude directories from watching for changes (use multiple times)",
)
@click.option(
    "--verbose",
    "-v",
    count=True,
    default=False,
    help="operate more verbosely (use multiple times)",
)
@click.option(
    "--quiet",
    "-q",
    count=True,
    default=False,
    help="operate less verbosely",
)
@click.pass_context
def run(
    ctx: click.Context,
    model_file: pathlib.Path,
    address: str,
    port: int,
    poll_interval: float,
    excluded_dirs: list[pathlib.Path],
    axes_origin: bool,
    export_models: bool,
    verbose: int,
    quiet: int,
):
    if (
        ctx.get_parameter_source("address") is not click.core.ParameterSource.DEFAULT
        or ctx.get_parameter_source("port") is not click.core.ParameterSource.DEFAULT
    ):
        ctx.fail(
            "--address/--port are currently unsupported due to YACV front-end JS code "
            "hard-coding http://127.0.0.1:32323/\n\n"
            "This limitation may be removed in a later release."
        )

    verbosity = min(max(verbose - quiet, -1), 2)
    match verbosity:
        case -1:
            log_level = LogLevel.ERROR
        case 0:
            # default
            log_level = LogLevel.INFO
        case 1:
            log_level = LogLevel.DEBUG
        case 2:
            log_level = LogLevel.TRACE
        case _:
            # can't happen
            raise ValueError(f"unhandled log level {verbosity}")

    os.environ["YACV_HOST"] = address
    os.environ["YACV_PORT"] = str(port)
    print(f"Starting server on http://{address}:{port}")
    server = Server(
        model_file,
        poll_interval=poll_interval,
        excluded_dirs=list(excluded_dirs),
        log_level=log_level,
    )
    server.serve(axes_origin=axes_origin, export_models=export_models)


if __name__ == "__main__":
    """If you don't want to use a Python entrypoint to get at run() above, you can just invoke
    this file as a script.
    """
    run()
