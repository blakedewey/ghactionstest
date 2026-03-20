from pathlib import Path

from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist


def _static_version_path(dist) -> Path:
    pkg_dirs = dist.package_dir or {}
    root = Path(pkg_dirs.get("", "."))
    for pkg in sorted(dist.packages or [], key=lambda p: (p.count("."), p)):
        if pkg in pkg_dirs:
            pkg_dir = Path(pkg_dirs[pkg])
        else:
            pkg_dir = root.joinpath(*pkg.split("."))
        if (pkg_dir / "_version.py").exists():
            return pkg_dir / ".static_version.json"
    raise RuntimeError("_version.py not found in any declared package")


def _write_static_version(dist) -> None:
    version = dist.get_version()
    _static_version_path(dist).write_text(
        f'{"version": "{version}"}',
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
