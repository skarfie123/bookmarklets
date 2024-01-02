# Bookmarklets

![PyPI version](https://img.shields.io/pypi/v/bookmarklets)
![PyPI downloads](https://img.shields.io/pypi/dm/bookmarklets)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

A tool for developing bookmarklets.

Inspired by <https://github.com/mrcoles/bookmarklet>, but designed to support multiple bookmarklets, and to also export as html.

Develop bookmarklets based on javascript files, eg. so that you can commit the source files to git.

## Installation

It is recommended to install using `pipx`, but you can also use `pip`. See <https://pypi.org/project/pipx/>.

```sh
pipx install bookmarklet
```

To convert them to bookmarklets, either start the server or generate a bookmarks.html file.

## Server

1. run `bookmarklet server [FOLDER]`
    - specify the folder with the javascript files, otherwise the current folder is used
    - use `-o`/`--open` to automatically open the webpage
    - use `-p`/`--port` to serve the port other than the default (8000)
    - use `--public` to allow other devices on your network to access the page, otherwise only on localhost
2. on the webpage drag each bookmarklet to your bookmarks bar

## HTML

1. run `bookmarklet html [FOLDER]`
    - specify the folder with the javascript files, otherwise the current folder is used
    - use `-o`/`--output` to specify the output file, otherwise it defaults to `bookmarks.html`
2. import the `bookmarks.html` into your browser

## Metadata

You can include some metadata in a comment block at the top of the source file.

The fields that you can use are:

- name: the name of the bookmarklet (if not provided, the file name will be used)
  - in the server this will be the name of the button
  - in the html this will be the name of the bookmark, and included in a comment
- author : the author of the bookmarklet
  - in the server this will be mentioned next to the button
  - in the html this will be included in a comment
- url: link to the author
  - in the server this will be linked to the author
  - in the html this will be included in a comment
- script: script to load before running the bookmarklet
  - specify it multiple times to use multiple scripts
- style: style to load before running the bookmarklet
  - specify it multiple times to use multiple styles

See the examples in this repo.
