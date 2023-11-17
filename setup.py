from pathlib import Path
from setuptools import setup, find_packages

__package_name__ = "ghactionstest"


def get_version_and_cmdclass(pkg_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(pkg_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.get_cmdclass(pkg_path)


__version__, cmdclass = get_version_and_cmdclass(__package_name__)

setup(
    name="gh-actions-test",
    version=__version__,
    description="Test package for GitHub Actions",
    long_description=(Path(__file__).parent.resolve() / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Blake Dewey",
    author_email="blake.dewey@jhu.edu",
    url="https://github.com/blakedewey/ghactionstest",
    license="Apache License, 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
    packages=find_packages(),
    keywords="testing",
    python_requires=">=3.10",
    cmdclass=cmdclass,
)
