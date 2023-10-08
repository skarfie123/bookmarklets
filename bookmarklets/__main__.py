import pathlib
import re
import urllib.parse
import webbrowser
from io import TextIOWrapper
from pathlib import Path
from typing import Annotated

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

cli = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)

Folder = Annotated[Path, typer.Argument(help="Folder to save the bookmarklets")]


def _parse_metadata(f: TextIOWrapper) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in f.readlines():
        if not line.startswith("//"):
            return metadata
        # each metadata like will be of the form:
        # "// @key value"
        # parse this with regex:
        m = re.match(r"// @(\w+) (\S.*)", line)
        if m:
            metadata[m.group(1)] = m.group(2)

    return metadata


def _get_code(folder: Path) -> dict[str, tuple[str, dict[str, str]]]:
    code = {}
    code_files = sorted(file for file in folder.iterdir() if file.suffix == ".js")
    for file in code_files:
        with open(file, encoding="utf-8") as f:
            metadata = {}
            if f.readline().startswith("//"):
                metadata = _parse_metadata(f)
            f.seek(0)
            code[file.name[:-3]] = (f.read(), metadata)

    return code


def _get_bookmarklets(folder: Path):
    all_code = _get_code(folder)
    return {
        name: (f"javascript:(() => {{{urllib.parse.quote(code[0])}}})()", code[1])
        for name, code in all_code.items()
    }


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
    typer.echo("Opening web page with all bookmarklets")
    typer.echo("Drag the bookmarklets to your bookmarks bar to install them")
    typer.echo("Press CTRL+C to stop the server")

    app = FastAPI(folder=folder)

    @app.get("/", response_class=HTMLResponse)
    def root():
        links = []
        for name, bookmarklet in _get_bookmarklets(folder).items():
            code, metadata = bookmarklet
            author = ""
            if "author" in metadata:
                if "url" in metadata:
                    author = f' by <a href="{metadata["url"]}">{metadata["author"]}</a>'
                else:
                    author = f' by {metadata["author"]}'
            link = f'<p><a class="bookmarklet" href="{code}">{metadata.get("name") or name}</a>{author}</p>'
            links.append(link)

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
    typer.echo(f"Writing {output}")
    with open(output, "w", encoding="utf-8") as f:
        links = "\n        ".join(
            f'<DT><A HREF="{bookmarklet[0]}">{bookmarklet[1].get("name") or name}</A>'
            for name, bookmarklet in _get_bookmarklets(folder).items()
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
