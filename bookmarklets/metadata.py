"""Dataclass for parsing and representing the metadata for a bookmarklet."""

import re
from dataclasses import dataclass
from io import TextIOWrapper

import typer


@dataclass
class Metadata:
    """Metadata from the comment block at the top of the bookmarklet."""

    name: str | None
    author: str | None
    url: str | None
    scripts: list[str]
    styles: list[str]

    @property
    def html_comment(self) -> str:
        """Return the HTML comment block."""
        return f"""\
        <!-- name: {self.name or "-"} -->
        <!-- author: {self.author or "-"} -->
        <!-- url: {self.url or "-"} -->
        """

    @staticmethod
    def parse_metadata(f: TextIOWrapper) -> "Metadata":
        """Parse metadata at the top of the file."""
        name = None
        author = None
        url = None
        scripts = []
        styles = []
        for line in f.readlines():
            if not line.startswith("//"):
                break
            # each metadata like will be of the form:
            # "// @key value"
            # get the key and value using regex
            m = re.match(r"// @(\w+) (\S.*)", line)
            if m:
                key, value = m.group(1), m.group(2)
                match key:
                    case "name":
                        name = value
                    case "author":
                        author = value
                    case "url":
                        url = value
                    case "script":
                        scripts.append(value)
                    case "style":
                        styles.append(value)
                    case _:
                        typer.echo(f"Ignoring unknown metadata key: {key}")

        return Metadata(name=name, author=author, url=url, scripts=scripts, styles=styles)
