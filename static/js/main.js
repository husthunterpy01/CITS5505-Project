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
  const toggle = document.getElementById("nav-search-toggle");
  const panel = document.getElementById("nav-search-panel");
  const input = document.getElementById("nav-search-input");

  if (!toggle || !panel || !input) {
    return;
  }

  const setOpen = (open) => {
    if (open) {
      panel.classList.remove("hidden");
      toggle.setAttribute("aria-expanded", "true");
      window.setTimeout(() => input.focus(), 0);
    } else {
      panel.classList.add("hidden");
      toggle.setAttribute("aria-expanded", "false");
    }
  };

  toggle.addEventListener("click", (e) => {
    e.stopPropagation();
    if (panel.classList.contains("hidden")) {
      setOpen(true);
    } else {
      setOpen(false);
    }
  });

  document.addEventListener("click", (e) => {
    if (panel.classList.contains("hidden")) return;
    if (toggle.contains(e.target) || panel.contains(e.target)) return;
    setOpen(false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !panel.classList.contains("hidden")) {
      setOpen(false);
    }
  });

  input.addEventListener("keydown", (e) => {
    if (e.key !== "Enter") return;
    e.preventDefault();
    const query = input.value.trim();
    document.dispatchEvent(
      new CustomEvent("swanflip:browse-search", {
        bubbles: true,
        detail: { query },
      }),
    );
    setOpen(false);
  });
});
