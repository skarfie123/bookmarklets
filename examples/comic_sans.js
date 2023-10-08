// ==Bookmarklet==
// @name Comic Sans
// @author Seth Falco
// @url https://www.freecodecamp.org/news/what-are-bookmarklets/
// ==/Bookmarklet==

const allElements = document.querySelectorAll("*");

for (let element of allElements) {
  element.style.fontFamily = "Comic Sans MS";
}
