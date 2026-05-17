(function () {
  const grid = document.getElementById("favorites-grid");
  if (!grid) return;

  const emptyState = document.getElementById("favorites-empty-state");
  const csrfToken =
    document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";

  grid.addEventListener("click", async (event) => {
    const button = event.target.closest(".favorite-remove-btn");
    if (!button) return;

    const productId = button.getAttribute("data-product-id");
    if (!productId) return;

    if (!window.confirm("Remove this listing from your favorites?")) return;

    button.disabled = true;
    try {
      const response = await fetch("/api/favorites/toggle", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ product_id: Number(productId) }),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) {
        throw new Error(data.message || "Unable to remove favorite.");
      }

      const card = button.closest(".favorite-card");
      if (card) card.remove();

      if (grid.querySelectorAll(".favorite-card").length === 0) {
        grid.classList.add("hidden");
        if (emptyState) emptyState.classList.remove("hidden");
      }
    } catch (error) {
      alert(error.message || "Unable to remove favorite.");
      button.disabled = false;
    }
  });
})();
