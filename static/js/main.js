document.addEventListener("DOMContentLoaded", () => {
  const flashContainer = document.getElementById("flash-container");

  if (!flashContainer) {
    return;
  }

  window.setTimeout(() => {
    flashContainer.classList.add("opacity-0");

    window.setTimeout(() => {
      flashContainer.remove();
    }, 500);
  }, 5000);
});

document.addEventListener("DOMContentLoaded", () => {
  // Browse search wiring now lives in static/pages/BrowsePage/browsepage.js
});
