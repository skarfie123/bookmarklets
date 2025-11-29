"""Dataclass for representing and converting a bookmarklet."""

import urllib.parse
from dataclasses import dataclass
from functools import cached_property
from hashlib import md5

from bookmarklets.metadata import Metadata


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
