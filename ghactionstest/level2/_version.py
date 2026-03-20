# -*- coding: utf-8 -*-

from pathlib import Path


def get_version() -> str:
    """
    Return the best available version string.

    Resolution order:
    1. Live Git checkout
    2. Git archival metadata
    3. Generated static version file
    4. Fallback constant
    """
    package_root = Path(__file__).resolve().parent

    version = _version_from_git(package_root)
    if version is not None:
        return version

    version = _version_from_git_archive(package_root)
    if version is not None:
        return version

    version = _version_from_static(package_root)
    if version is not None:
        return version

    return "0+unknown"


def _version_from_git(package_root: Path) -> str | None:
    # The '--long' flag gets us the 'dev' version and
    # git hash, '--always' returns the git hash even if there are no tags.
    import subprocess

    try:
        p = subprocess.Popen(
            ["git", "describe", "--long", "--always", "--tags", "--dirty"],
            cwd=package_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError:
        return None

    if p.wait() != 0:
        return None

    description = (
        p.communicate()[0]
        .decode()
        .rstrip("\n")
        .rsplit("-")  # Split the latest tag, commits since tag, hash, and dirty
    )

    try:
        release, dev, git = description[:3]
    except ValueError:  # No tags, only the git hash
        git = "g{}".format(*description)
        release = "unknown"
        dev = None

    labels = []
    if dev == "0":
        dev = None
    else:
        labels.append(git)

    if description[-1] == "dirty":
        labels.append("dirty")

    return pep440_format(release, dev, labels)


def _version_from_git_archive(package_root: Path) -> str | None:
    import json
    import re

    archival_path = package_root / ".git_archival.json"
    if not archival_path.exists():
        return None

    try:
        data = json.loads(archival_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    tag = data.get("describe")
    commit = data.get("commit")

    if not tag or not commit:
        return None

    if tag.startswith("$Format:") or commit.startswith("$Format:"):
        return None

    tag_match = re.fullmatch(r"v?(\d+\.\d+\.\d+)", tag)
    if tag_match:
        return pep440_format(tag_match.group(1), None, None)

    tag_match = re.fullmatch(r"v?(\d+\.\d+\.\d+)-(\d+)-g([0-9a-f]+)", tag)
    if tag_match:
        release, dev, git = tag_match.groups()
        labels = [] if dev == "0" else [f"g{git}"]
        return pep440_format(release, None if dev == "0" else dev, labels)
    
    return pep440_format("unknown", dev=None, labels=["g{}".format(commit[:7])])


def _version_from_static(package_root: Path) -> str | None:
    import ast

    static_path = package_root / "_static_version.py"
    if not static_path.exists():
        return None

    try:
        source = static_path.read_text(encoding="utf-8")
    except OSError:
        return None

    try:
        tree = ast.parse(source, filename=str(static_path))
    except SyntaxError:
        return None

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "version":
                    try:
                        value = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError):
                        return None
                    return value if isinstance(value, str) else None

    return None


def pep440_format(release: str, dev: str | None, labels: list[str] | None) -> str:
    if release.startswith("v"):
        release = release[1:]
    version_parts = [release]
    if dev:
        if release.endswith("-dev") or release.endswith(".dev"):
            version_parts.append(dev)
        else:  # prefer PEP440 over strict adhesion to semver
            version_parts.append(".dev{}".format(dev))

    if labels:
        version_parts.append("+")
        version_parts.append(".".join(labels))

    return "".join(version_parts)


__version__ = get_version()
