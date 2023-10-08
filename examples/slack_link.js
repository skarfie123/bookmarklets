// ==Bookmarklet==
// @name Slack Link
// @author Rahul Pai
// ==/Bookmarklet==

const url = window.location.href;
var suffix = null;
var separator = null;
var emoji = "link";
if (url.startsWith("https://docs.google.com/document")) {
  suffix = "- Google Docs";
  emoji = "google-docs";
} else if (url.startsWith("https://docs.google.com/spreadsheets")) {
  suffix = "- Google Sheets";
  emoji = "google-sheets";
} else if (url.startsWith("https://www.google.com/maps")) {
  suffix = "- Google Maps";
  emoji = "google-maps";
} else if (url.startsWith("https://app.shortcut.com")) {
  suffix = "| Shortcut";
  emoji = "shortcut-new";
} else if (url.startsWith("https://github.com")) {
  separator = "·";
  emoji = "github";
} else if (url.startsWith("https://lucid.app/lucidchart")) {
  suffix = ": Lucidchart";
  emoji = "lucidchart";
} else if (url.startsWith("https://www.youtube.com/")) {
  suffix = "- YouTube";
  emoji = "youtube";
}

var title = document.title;
if (suffix) {
  title = title.replace(suffix, "");
}
if (separator) {
  title = title.split(separator).slice(0, -1).join(separator);
}
const text = `:${emoji}: [${title.trim()}](${url})`;
navigator.clipboard.writeText(text);
