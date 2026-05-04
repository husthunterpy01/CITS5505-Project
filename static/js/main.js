document.addEventListener("DOMContentLoaded", () => {
  const flashContainer = document.getElementById("flash-container");

  if (flashContainer) {
    window.setTimeout(() => {
      flashContainer.classList.add("opacity-0");

      window.setTimeout(() => {
        flashContainer.remove();
      }, 500);
    }, 5000);
  }

  if (window.location.pathname === "/admin/users") {
    const script = document.createElement("script");
    script.src = "/static/pages/AdminPage/usermanager.js";
    script.defer = true;
    document.body.appendChild(script);
  }
});
