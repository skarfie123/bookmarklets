# Bookmarklets

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
