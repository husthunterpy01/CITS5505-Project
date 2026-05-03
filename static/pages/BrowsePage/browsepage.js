document.addEventListener("DOMContentLoaded", function () {
  const root = document.getElementById("browse-root");
  const grid = document.getElementById("browse-product-grid");
  const feedback = document.getElementById("browse-search-feedback");
  const emptyState = document.getElementById("browse-empty-state");
  const searchInput = document.getElementById("browse-search-input");
  const searchSubmit = document.getElementById("browse-search-submit");
  const productCards = Array.from(grid ? grid.querySelectorAll("[data-product-id]") : []);
  const defaultVisibleIds = new Set(
    productCards.map((card) => String(card.dataset.productId)),
  );

  function setFeedback(message, show) {
    if (!feedback) return;
    if (!show || !message) {
      feedback.textContent = "";
      feedback.classList.add("hidden");
      return;
    }
    feedback.textContent = message;
    feedback.classList.remove("hidden");
  }

  function setEmptyState(show) {
    if (!emptyState) return;
    if (show) {
      emptyState.classList.remove("hidden");
    } else {
      emptyState.classList.add("hidden");
    }
  }

  function bindChatDelegation(container) {
    container.addEventListener("click", function (e) {
      const button = e.target.closest(".chat-seller-btn");
      if (!button) return;
      const sellerName = button.dataset.sellerName;
      const productTitle = button.dataset.productTitle;
      const productId = button.dataset.productId;
      alert(
        `Chat feature coming soon.\n\nSeller: ${sellerName}\nProduct: ${productTitle}\nProduct ID: ${productId}`,
      );
    });
  }

  if (grid) {
    bindChatDelegation(grid);
  }

  if (!root || !grid) {
    return;
  }

  const apiUrl = root.dataset.searchUrl;
  if (!apiUrl) {
    return;
  }

  async function runSearch(query) {
    const params = new URLSearchParams();
    params.set("q", query);
    const res = await fetch(`${apiUrl}?${params.toString()}`, {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) {
      throw new Error("Search request failed");
    }
    return res.json();
  }

  function applyVisibleProducts(visibleProductIds) {
    let visibleCount = 0;
    productCards.forEach((card) => {
      const id = card.dataset.productId;
      const visible = visibleProductIds.has(id);
      card.classList.toggle("hidden", !visible);
      if (visible) visibleCount += 1;
    });
    setEmptyState(visibleCount === 0);
  }

  async function performSearch(q) {
    if (!q) {
      setFeedback("", false);
      applyVisibleProducts(defaultVisibleIds);
      return;
    }

    setFeedback("", false);
    grid.classList.add("opacity-60", "pointer-events-none");

    try {
      const data = await runSearch(q);
      if (!data.success || !Array.isArray(data.products)) {
        throw new Error("Invalid response");
      }
      const items = data.products;
      if (data.message) {
        setFeedback(data.message, true);
      } else {
        setFeedback("", false);
      }
      const visibleIds = new Set(items.map((item) => String(item.product_id)));
      applyVisibleProducts(visibleIds);
    } catch {
      setFeedback("Something went wrong. Please try again.", true);
      setEmptyState(false);
    } finally {
      grid.classList.remove("opacity-60", "pointer-events-none");
    }
  }

  document.addEventListener("swanflip:browse-search", async function (ev) {
    const raw = ev.detail && ev.detail.query != null ? String(ev.detail.query) : "";
    await performSearch(raw.trim());
  });

  if (searchInput && searchSubmit) {
    searchInput.addEventListener("input", () => {
      if (!searchInput.value.trim()) {
        setFeedback("", false);
        applyVisibleProducts(defaultVisibleIds);
      }
    });

    searchInput.addEventListener("keydown", async (e) => {
      if (e.key !== "Enter") return;
      e.preventDefault();
      await performSearch(searchInput.value.trim());
    });

    searchSubmit.addEventListener("click", async () => {
      await performSearch(searchInput.value.trim());
      searchInput.focus();
    });
  }
});
