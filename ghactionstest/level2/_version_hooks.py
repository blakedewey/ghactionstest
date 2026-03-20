from importlib import import_module
from pathlib import Path

from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


def _version_module(dist):
    packages = dist.packages or []
    # Prefer the shortest declared package path
    candidates = sorted(packages, key=lambda p: (p.count("."), p))
    for pkg in candidates:
        mod_name = f"{pkg}._version"
        try:
            return import_module(mod_name)
        except ModuleNotFoundError as e:
            continue
    raise RuntimeError("_version not found in any available package.")


def _write_static_version(dist) -> None:
    mod = _version_module(dist)
    version = mod.get_version()
    path = Path(mod.__file__).resolve().parent / "_static_version.py"
    path.write_text(
        "# This file is auto-generated at build time.\n"
        f'version = "{version}"\n',
        encoding="utf-8",
    )
    

class build_py(_build_py):
    def run(self):
        _write_static_version(self.distribution)
        super().run()


class sdist(_sdist):
    def run(self):
        _write_static_version(self.distribution)
        super().run()
