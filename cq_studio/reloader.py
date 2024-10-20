import datetime
import gc
import pathlib
import sys
import types
from typing import Any


class Reloader:
    def __init__(self, logger: Any, ignore_dirs: list[pathlib.Path] | None = None):
        # Any modules loaded before the reloader is created and initialized are considered
        # system stuff that won't change, and are ignored by the watch-for-changes logic.
        self.initial_modules = sys.modules.copy()
        self.logger = logger
        self.logger.trace("Initial modules at startup:")
        for module in self.initial_modules:
            self.logger.trace(f"  {module}")

        self.ignore_paths = [
            pathlib.Path(path).resolve()
            for path in ignore_dirs or []
            if path.exists() and path.is_dir()
        ]
        for path in self.ignore_paths:
            assert path.is_absolute() and path.is_dir(), path

    def _filter_modules(
        self,
        modules: dict[str, types.ModuleType],
    ) -> dict[str, types.ModuleType]:
        filtered = {}

        for name, module in modules.items():
            if name in self.initial_modules:
                continue
            file = getattr(module, "__file__", None)
            if not file:
                # builtins and some others don't have a __file__ attribute.
                # cadquery has some modules where the attribute is present, but None.  WTF?
                # Either way, ignore it.
                continue
            mod_file = pathlib.Path(file).resolve()
            if any(
                [exclude_dir in mod_file.parents for exclude_dir in self.ignore_paths]
            ):
                self.logger.trace(f"Skipping {module.__file__} from excluded directory")
                continue
            filtered[name] = module
        return filtered

    def find_modules(self) -> dict[str, types.ModuleType]:
        """Generate a list of loaded modules, minus those present before loading model file."""
        modules = self._filter_modules(sys.modules)

        self.logger.trace(
            f"Found {len(modules)} user modules loaded after initialization"
        )
        for name, module in sorted(modules.items()):
            file = getattr(module, "__file__", None)
            self.logger.trace(f"  {name}: {file}")

        return modules

    def find_files(self) -> set[pathlib.Path]:
        """Generate a list of files to watch, associated with modules loaded by model file."""
        modules = self.find_modules()
        files = {
            pathlib.Path(mod.__file__) for mod in modules.values()  # type: ignore[arg-type]
        }
        self.logger.trace(f"Found {len(files)} from post-initialization modules")
        for file in sorted(files):
            self.logger.trace(f"  {file}")
        return files

    def most_recent(self, files: set[pathlib.Path]) -> datetime.datetime:
        """Find the most recent timestamp from a set of files."""
        timestamp_by_file = {
            file: datetime.datetime.fromtimestamp(file.stat().st_mtime)
            for file in files
        }
        self.logger.trace(f"Most recent timestamps for {len(timestamp_by_file)} files:")
        for file, timestamp in sorted(timestamp_by_file.items()):
            self.logger.trace(f"  {file}: {timestamp.isoformat()}")
        val = max(timestamp_by_file.values())
        return val

    def unload(self) -> None:
        """Force-unload the modules loaded (directly or indirectly) by the user's model file."""
        to_unload = self.find_modules()
        self.logger.trace(f"Unloading {len(to_unload)} modules")
        for name in sorted(to_unload):
            module = sys.modules.pop(name)
            self.logger.trace(f"  {name}: {getattr(module, '__file__', 'None')}")
            del module

        gc.collect()
