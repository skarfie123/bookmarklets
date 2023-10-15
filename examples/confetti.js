// ==Bookmarklet==
// @name Confetti
// @author Rahul Pai
// @script https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.0/dist/confetti.browser.min.js
// ==/Bookmarklet==

// example from here https://www.npmjs.com/package/canvas-confetti
window.confetti({
  particleCount: 100,
  startVelocity: 30,
  spread: 360,
  origin: {
    x: Math.random(),
    // since they fall down, start a bit higher than random
    y: Math.random() - 0.2,
  },
});
