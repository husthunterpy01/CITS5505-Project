document.addEventListener("DOMContentLoaded", function () {
  const root = document.getElementById("browse-root");
  const grid = document.getElementById("browse-product-grid");
  const feedback = document.getElementById("browse-search-feedback");
  const emptyState = document.getElementById("browse-empty-state");
  const searchInput = document.getElementById("browse-search-input");
  const searchSubmit = document.getElementById("browse-search-submit");
  const locationInput = document.getElementById("browse-location-input");
  const useLocationBtn = document.getElementById("browse-use-location");
  const distanceSelect = document.getElementById("browse-distance-filter");
  const categorySelect = document.getElementById("browse-category-filter");
  const applyFiltersBtn = document.getElementById("browse-apply-filters");
  const clearFiltersBtn = document.getElementById("browse-clear-filters");
  const sortSelect = document.getElementById("browse-sort-select");
  const productCards = Array.from(
    grid ? grid.querySelectorAll("article.browse-product-card[data-product-id]") : [],
  );
  const defaultVisibleIds = new Set(
    productCards.map((card) => String(card.dataset.productId)),
  );
  let geoCoords = null;

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
    emptyState.classList.toggle("hidden", !show);
  }

  function bindChatDelegation(container) {
    container.addEventListener("click", function (e) {
      const button = e.target.closest(".chat-seller-btn");
      if (!button) return;
      const sellerName = button.dataset.sellerName;
      const productTitle = button.dataset.productTitle;
      const productId = button.dataset.productId;
      const sellerId = Number(button.dataset.sellerId || 0);
      if (!sellerId) {
        alert("Unable to open chat for this seller.");
        return;
      }

      document.dispatchEvent(
        new CustomEvent("swanflip:chat-start", {
          detail: {
            targetUserId: sellerId,
            productId: Number(productId || 0) || null,
            displayName: sellerName || productTitle || "Seller",
            role: "standard_user",
          },
        }),
      );
    });
  }

  if (grid || root) {
    bindChatDelegation(grid || root);
  }

  if (!root || !grid) {
    return;
  }

  const apiUrl = root.dataset.searchUrl;
  if (!apiUrl) {
    return;
  }

  function hasActiveFilters() {
    const q = searchInput && searchInput.value.trim();
    const location = locationInput && locationInput.value.trim();
    const distance = distanceSelect && distanceSelect.value;
    const cat = categorySelect && categorySelect.value;
    return !!(q || location || distance || cat);
  }

  function buildSearchParams() {
    const params = new URLSearchParams();
    const q = searchInput ? searchInput.value.trim() : "";
    if (q) params.set("q", q);
    const location = locationInput ? locationInput.value.trim() : "";
    if (location) params.set("user_location", location);
    if (geoCoords && Number.isFinite(geoCoords.latitude) && Number.isFinite(geoCoords.longitude)) {
      params.set("user_lat", String(geoCoords.latitude));
      params.set("user_lon", String(geoCoords.longitude));
    }
    if (distanceSelect && distanceSelect.value) {
      params.set("distance_km", distanceSelect.value);
    }
    if (categorySelect && categorySelect.value) {
      params.set("category_id", categorySelect.value);
    }
    return params;
  }

  async function fetchFilteredProducts() {
    const params = buildSearchParams();
    const qs = params.toString();
    const url = qs ? `${apiUrl}?${qs}` : apiUrl;
    const res = await fetch(url, {
      headers: { Accept: "application/json" },
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg =
        data && data.message ? data.message : "Filter request failed.";
      throw new Error(msg);
    }
    return data;
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
    applySort();
  }

  function applySort() {
    if (!grid) return;
    const mode = sortSelect ? sortSelect.value : "newest";
    const cards = Array.from(
      grid.querySelectorAll("article.browse-product-card[data-product-id]"),
    );
    cards.sort((a, b) => {
      if (mode === "price-low") {
        return Number(a.dataset.price || 0) - Number(b.dataset.price || 0);
      }
      if (mode === "price-high") {
        return Number(b.dataset.price || 0) - Number(a.dataset.price || 0);
      }
      return Number(a.dataset.rank || 0) - Number(b.dataset.rank || 0);
    });
    cards.forEach((card) => grid.appendChild(card));
  }

  async function applyBrowseFilters() {
    if (!hasActiveFilters()) {
      setFeedback("", false);
      applyVisibleProducts(defaultVisibleIds);
      return;
    }

    setFeedback("", false);
    grid.classList.add("opacity-60", "pointer-events-none");

    try {
      const data = await fetchFilteredProducts();
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
    } catch (err) {
      setFeedback(err.message || "Something went wrong. Please try again.", true);
      setEmptyState(false);
    } finally {
      grid.classList.remove("opacity-60", "pointer-events-none");
    }
  }

  function clearAllFilters() {
    geoCoords = null;
    if (searchInput) searchInput.value = "";
    if (locationInput) locationInput.value = "";
    if (distanceSelect) distanceSelect.value = "";
    if (categorySelect) categorySelect.value = "";
    setFeedback("", false);
    applyVisibleProducts(defaultVisibleIds);
  }

  document.addEventListener("swanflip:browse-search", async function (ev) {
    const raw = ev.detail && ev.detail.query != null ? String(ev.detail.query) : "";
    if (searchInput) searchInput.value = raw;
    await applyBrowseFilters();
  });

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      if (!hasActiveFilters()) {
        setFeedback("", false);
        applyVisibleProducts(defaultVisibleIds);
      }
    });

    searchInput.addEventListener("keydown", async (e) => {
      if (e.key !== "Enter") return;
      e.preventDefault();
      await applyBrowseFilters();
    });
  }

  if (locationInput) {
    locationInput.addEventListener("input", () => {
      // If user edits text manually, stop using previous geo pin.
      geoCoords = null;
      if (!hasActiveFilters()) {
        setFeedback("", false);
        applyVisibleProducts(defaultVisibleIds);
      }
    });
  }

  if (distanceSelect) {
    distanceSelect.addEventListener("change", async () => {
      await applyBrowseFilters();
    });
  }

  if (useLocationBtn) {
    useLocationBtn.addEventListener("click", () => {
      if (!navigator.geolocation) {
        setFeedback("Geolocation is not supported by your browser.", true);
        return;
      }

      useLocationBtn.disabled = true;
      useLocationBtn.textContent = "Locating...";
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          geoCoords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          if (locationInput && !locationInput.value.trim()) {
            locationInput.value = "Current location";
          }
          setFeedback("Using your current location.", true);
          await applyBrowseFilters();
          useLocationBtn.disabled = false;
          useLocationBtn.textContent = "Use my location";
        },
        (err) => {
          let message = "Unable to get your location.";
          if (err && err.code === 1) message = "Location permission denied.";
          if (err && err.code === 2) message = "Location unavailable.";
          if (err && err.code === 3) message = "Location request timed out.";
          setFeedback(message, true);
          useLocationBtn.disabled = false;
          useLocationBtn.textContent = "Use my location";
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
      );
    });
  }

  if (searchSubmit) {
    searchSubmit.addEventListener("click", async () => {
      await applyBrowseFilters();
      if (searchInput) searchInput.focus();
    });
  }

  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener("click", async () => {
      await applyBrowseFilters();
    });
  }

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", () => {
      clearAllFilters();
    });
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", () => {
      applySort();
    });
  }
});
