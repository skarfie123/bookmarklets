"""Main entrypoint."""

import pathlib
import re
import urllib.parse
import webbrowser
from dataclasses import dataclass
from functools import cached_property
from hashlib import md5
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


@dataclass
class Bookmarklet:
    """Bookmarklet data extracted from code."""

    file_name: str
    code: str
    metadata: Metadata

    def _hash(self, value: str) -> str:
        return md5(value.encode(), usedforsecurity=False).hexdigest()

    def _load_script(self, code: str, script: str) -> str:
        id_ = f"bookmarklet__script_{self._hash(script)}"
        return f"""
function callback(){{
    {code}
}}

if (!document.getElementById("{id_}")) {{
    var s = document.createElement("script");
    if (s.addEventListener) {{
    s.addEventListener("load", callback, false)
    }} else if (s.readyState) {{
    s.onreadystatechange = callback
    }}
    s.id = "{id_}";
    s.src = "{script}";
    document.body.appendChild(s);
}} else {{
    callback();
}}
    """

    def _load_style(self, code: str, style: str) -> str:
        id_ = f"bookmarklet__style_{self._hash(style)}"
        return f"""{code}
if (!document.getElementById("{id_}")) {{
    var link = document.createElement("link");
    link.id = "{id_}";
    link.rel="stylesheet";
    link.href = "{style}";
    document.body.appendChild(link);
}}
    """

    @cached_property
    def bookmarklet(self) -> str:
        """Return the bookmarklet generated from code."""
        code = self.code
        for script in reversed(self.metadata.scripts):
            code = self._load_script(code, script)
        for style in reversed(self.metadata.styles):
            code = self._load_style(code, style)
        return f"javascript:(() => {{{urllib.parse.quote(code)}}})()"

    @property
    def name(self) -> str:
        """
        Return the name of the bookmarklet.

        If the name is not specified in the metadata, the name of the source file is used.
        """
        return self.metadata.name or self.file_name[:-3]

    @property
    def html_comment(self) -> str:
        """Return the HTML comment block."""
        return f"<!-- {self.name}.js -->\n" + self.metadata.html_comment


def _parse_metadata(f: TextIOWrapper) -> Metadata:
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


def _get_code(folder: Path) -> list[Bookmarklet]:
    code = []
    code_files = sorted(file for file in folder.iterdir() if file.suffix == ".js")
    for file in code_files:
        with open(file, encoding="utf-8") as f:
            metadata = _parse_metadata(f)
            f.seek(0)
            code.append(Bookmarklet(file_name=file.name, code=f.read(), metadata=metadata))

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
        for bookmarklet in _get_code(folder):
            author = ""
            if bookmarklet.metadata.author:
                if bookmarklet.metadata.url:
                    author = f' by <a href="{bookmarklet.metadata.url}">{bookmarklet.metadata.author}</a>'  # noqa: E501
                else:
                    author = f" by {bookmarklet.metadata.author}"
            links.append(
                f'<p><a class="bookmarklet" href="{bookmarklet.bookmarklet}">{bookmarklet.name}</a>{author}</p>'  # noqa: E501
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
    # 0.0.0.0 binds on all IPs whereas 127.0.0.1 binds only on localhost
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
            f"<!-- {bookmarklet.file_name} -->\n"
            + bookmarklet.metadata.html_comment
            + f'<DT><A HREF="{bookmarklet.bookmarklet}">{bookmarklet.name}</A>'
            for bookmarklet in _get_code(folder)
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
