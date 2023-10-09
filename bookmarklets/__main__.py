"""Main entrypoint."""

import pathlib
import re
import urllib.parse
import webbrowser
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)

Folder = Annotated[Path, typer.Argument(help="Folder to save the bookmarklets")]


@dataclass
class Metadata:
    """Metadata from the comment block at the top of the bookmarklet."""

    name: str | None
    author: str | None
    url: str | None


@dataclass
class Bookmarklet:
    """Bookmarklet data extracted from code."""

    code: str
    metadata: Metadata

    @property
    def bookmarklet(self) -> str:
        """Return the bookmarklet generated from code."""
        return f"javascript:(() => {{{urllib.parse.quote(self.code)}}})()"


def _parse_metadata(f: TextIOWrapper) -> Metadata:
    metadata: dict[str, str] = {}
    for line in f.readlines():
        if not line.startswith("//"):
            break
        # each metadata like will be of the form:
        # "// @key value"
        # parse this with regex:
        m = re.match(r"// @(\w+) (\S.*)", line)
        if m:
            metadata[m.group(1)] = m.group(2)

    return Metadata(
        name=metadata.get("name"), author=metadata.get("author"), url=metadata.get("url")
    )


def _get_code(folder: Path) -> dict[str, Bookmarklet]:
    code = {}
    code_files = sorted(file for file in folder.iterdir() if file.suffix == ".js")
    for file in code_files:
        with open(file, encoding="utf-8") as f:
            metadata = _parse_metadata(f)
            f.seek(0)
            code[file.name[:-3]] = Bookmarklet(code=f.read(), metadata=metadata)

    return code


@cli.command(help="Start the bookmarklet server with links to all the bookmarklets")
def server(
    folder: Folder = pathlib.Path.cwd(),
    open_brower: Annotated[
        bool, typer.Option("-o", "--open", help="Open the web page in the browser")
    ] = False,
    port: Annotated[
        int, typer.Option("-p", "--port", help="Port to run the server on", min=1, max=65535)
    ] = 8000,
    public: Annotated[bool, typer.Option(help="Make the server public")] = False,
):
    """Start the bookmarklet server with links to all the bookmarklets."""
    typer.echo("Opening web page with all bookmarklets")
    typer.echo("Drag the bookmarklets to your bookmarks bar to install them")
    typer.echo("Press CTRL+C to stop the server")

    app = FastAPI(folder=folder)

    @app.get("/", response_class=HTMLResponse)
    def root():
        links = []
        for name, bookmarklet in _get_code(folder).items():
            author = ""
            if bookmarklet.metadata.author:
                if bookmarklet.metadata.url:
                    author = f' by <a href="{bookmarklet.metadata.url}">{bookmarklet.metadata.author}</a>'  # noqa: E501
                else:
                    author = f" by {bookmarklet.metadata.author}"
            links.append(
                f'<p><a class="bookmarklet" href="{bookmarklet.bookmarklet}">{bookmarklet.metadata.name or name}</a>{author}</p>'  # noqa: E501
            )

        joined_links = "\n".join(links)
        html_response = f"""<html>
    <head>
        <title>Bookmarklets</title>
        <style>
            html,body,div {{
                margin: 0;
                padding: 0;
                font: normal 16px/24px Helvetica Neue, Helvetica, sans-serif;
                color: #333;
            }}
            #main {{
                max-width: 630px;
                margin: 3em auto;
            }}
            .bookmarklet {{
                display: inline-block;
                padding: .5em 1em;
                color: #fff;
                background: #33e;
                border-radius: 4px;
                text-decoration: none;
            }}
            a {{
                color: #33e;
            }}
        </style>
    </head>
    <body>
        <div id="main">
            <h1>Bookmarklets</h1>
            {joined_links}
        </div>
    </body>
</html>"""
        return html_response

    if open_brower:
        webbrowser.open_new_tab(f"http://localhost:{port}")

    host = "0.0.0.0" if public else "127.0.0.1"  # nosec: B104
    uvicorn.run(app, host=host, port=port)


@cli.command(help="Generate bookmarks.html to import into browsers")
def html(
    folder: Folder = pathlib.Path.cwd(),
    output: Annotated[
        str, typer.Option("-o", "--output", help="Output file name")
    ] = "bookmarks.html",
):
    """Generate bookmarks.html to import into browsers."""
    typer.echo(f"Writing {output}")
    with open(output, "w", encoding="utf-8") as f:
        links = "\n        ".join(
            f'<DT><A HREF="{bookmarklet.bookmarklet}">{bookmarklet.metadata.name or name}</A>'
            for name, bookmarklet in _get_code(folder).items()
        )
        # write a bookmarks.html file for importing into browsers
        # https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85)
        html_str = f"""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL>
    <DT><H3>Bookmarklets</H3></DT>
    <DL>
        {links}
    </DL>
</DL>"""
        f.write(html_str)


if __name__ == "__main__":
    cli()
