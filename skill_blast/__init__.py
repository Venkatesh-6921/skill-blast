"""skill-blast: One-click installer for 50 top AI agent skills."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("skill-blast")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__author__ = "skill-blast contributors"
