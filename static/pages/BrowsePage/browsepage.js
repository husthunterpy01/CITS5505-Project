document.addEventListener("DOMContentLoaded", function () {
  const root = document.getElementById("browse-root");
  const grid = document.getElementById("browse-product-grid");
  const feedback = document.getElementById("browse-search-feedback");
  const emptyState = document.getElementById("browse-empty-state");
  const searchInput = document.getElementById("browse-search-input");
  const searchSubmit = document.getElementById("browse-search-submit");
  const locationInput = document.getElementById("browse-location-input");
  const locationSuggestions = document.getElementById("browse-location-suggestions");
  const searchSuggestions = document.getElementById("browse-search-suggestions");
  const useLocationBtn = document.getElementById("browse-use-location");
  const distanceSelect = document.getElementById("browse-distance-filter");
  const categorySelect = document.getElementById("browse-category-filter");
  const applyFiltersBtn = document.getElementById("browse-apply-filters");
  const clearFiltersBtn = document.getElementById("browse-clear-filters");
  const sortSelect = document.getElementById("browse-sort-select");
  const favoriteToggleUrl = root ? root.dataset.favoriteToggleUrl : "";
  const csrfToken =
    document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") || "";
  const productCards = Array.from(
    grid ? grid.querySelectorAll("article.browse-product-card[data-product-id]") : [],
  );
  const defaultVisibleIds = new Set(
    productCards.map((card) => String(card.dataset.productId)),
  );
  let geoCoords = null;
  let locationSuggestionsTimer = null;
  let searchSuggestionsTimer = null;

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

  function hideLocationSuggestions() {
    if (locationSuggestions) {
      locationSuggestions.classList.add("hidden");
      locationSuggestions.innerHTML = "";
    }
  }

  function hideSearchSuggestions() {
    if (searchSuggestions) {
      searchSuggestions.classList.add("hidden");
      searchSuggestions.innerHTML = "";
    }
  }

  async function fetchLocationSuggestions(query) {
    if (!query || query.length < 3) {
      hideLocationSuggestions();
      return;
    }

    try {
      const response = await fetch(`/api/locations/suggest?q=${encodeURIComponent(query)}`);
      const data = await response.json();

      if (!data.ok || !data.locations) {
        hideLocationSuggestions();
        return;
      }

      if (locationSuggestions) {
        locationSuggestions.innerHTML = data.locations
          .map(
            (loc) => `
          <button type="button" class="block w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100" data-location="${loc.name}">
            ${loc.label}
          </button>
        `,
          )
          .join("");
        locationSuggestions.classList.remove("hidden");
      }
    } catch (error) {
      hideLocationSuggestions();
    }
  }

  function getProductNames() {
    return Array.from(productCards)
      .map((card) => card.dataset.productName)
      .filter((name) => name && name.trim());
  }

  function fetchSearchSuggestions(query) {
    if (!query || query.length < 2) {
      hideSearchSuggestions();
      return;
    }

    const allProducts = getProductNames();
    const normalized = query.toLowerCase();
    const matching = allProducts
      .filter((name) => name.toLowerCase().includes(normalized))
      .filter((name, idx, arr) => arr.indexOf(name) === idx)
      .slice(0, 5);

    if (searchSuggestions) {
      if (matching.length === 0) {
        hideSearchSuggestions();
        return;
      }

      searchSuggestions.innerHTML = matching
        .map(
          (name) => `
        <button type="button" class="block w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100" data-search-product="${name}">
          ${name}
        </button>
      `,
        )
        .join("");
      searchSuggestions.classList.remove("hidden");
    }
  }

  function bindChatDelegation(container) {
    container.addEventListener("click", function (e) {
      if (e.target.closest(".favorite-toggle-btn")) {
        return;
      }
      const button = e.target.closest(".chat-seller-btn");
      if (button) {
        // Prevent this click from reaching the global document handler
        // that closes the chat popup on outside clicks.
        e.preventDefault();
        e.stopPropagation();
        const sellerName = button.dataset.sellerName;
        const productTitle = button.dataset.productTitle;
        const productId = button.dataset.productId;
        const sellerId = Number(button.dataset.sellerId || 0);
        const productImageUrl =
          button.closest("article.browse-product-card")?.querySelector("img")
            ?.src || "";
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
              productImageUrl,
              role: "standard_user",
            },
          }),
        );
        return;
      }

      const card = e.target.closest("article.browse-product-card[data-product-id]");
      if (!card || !container.contains(card)) return;
      const productUrl = card.dataset.productUrl;
      if (productUrl) {
        window.location.href = productUrl;
      }
    });

    container.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " ") return;
      const card = e.target.closest("article.browse-product-card[data-product-id]");
      if (!card || !container.contains(card)) return;
      e.preventDefault();
      const productUrl = card.dataset.productUrl;
      if (productUrl) {
        window.location.href = productUrl;
      }
    });
  }

  function setFavoriteButtonState(button, isFavorite) {
    button.dataset.isFavorite = isFavorite ? "true" : "false";
    button.title = isFavorite ? "Remove from favorites" : "Add to favorites";
    button.classList.remove(
      "border-rose-200",
      "bg-rose-50",
      "text-rose-600",
      "hover:bg-rose-100",
      "border-slate-200",
      "bg-white",
      "text-slate-400",
      "hover:bg-slate-50",
    );
    if (isFavorite) {
      button.classList.add("border-rose-200", "bg-rose-50", "text-rose-600", "hover:bg-rose-100");
    } else {
      button.classList.add("border-slate-200", "bg-white", "text-slate-400", "hover:bg-slate-50");
    }
  }

  function bindFavoriteDelegation(container) {
    if (!favoriteToggleUrl) return;
    container.addEventListener("click", async function (e) {
      const button = e.target.closest(".favorite-toggle-btn");
      if (!button) return;
      e.preventDefault();
      e.stopPropagation();

      const productId = Number(button.dataset.productId || 0);
      if (!productId) return;

      button.disabled = true;
      try {
        const response = await fetch(favoriteToggleUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            "X-CSRFToken": csrfToken,
          },
          body: JSON.stringify({ product_id: productId }),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok || !data.ok) {
          throw new Error(data.message || "Unable to update favorites.");
        }
        setFavoriteButtonState(button, !!data.is_favorite);
      } catch (error) {
        alert(error.message || "Unable to update favorites.");
      } finally {
        button.disabled = false;
      }
    });
  }

  if (grid || root) {
    bindChatDelegation(grid || root);
    bindFavoriteDelegation(grid || root);
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
      clearTimeout(searchSuggestionsTimer);
      const query = searchInput.value.trim();
      searchSuggestionsTimer = setTimeout(() => {
        fetchSearchSuggestions(query);
      }, 300);
      if (!hasActiveFilters()) {
        setFeedback("", false);
        applyVisibleProducts(defaultVisibleIds);
      }
    });

    searchInput.addEventListener("keydown", async (e) => {
      if (e.key !== "Enter") return;
      e.preventDefault();
      hideSearchSuggestions();
      await applyBrowseFilters();
    });

    if (searchSuggestions) {
      searchSuggestions.addEventListener("click", async (e) => {
        const button = e.target.closest("button");
        if (button && button.dataset.searchProduct) {
          searchInput.value = button.dataset.searchProduct;
          hideSearchSuggestions();
          await applyBrowseFilters();
        }
      });
    }
  }

  if (locationInput) {
    locationInput.addEventListener("input", () => {
      geoCoords = null;
      clearTimeout(locationSuggestionsTimer);
      const query = locationInput.value.trim();
      locationSuggestionsTimer = setTimeout(() => {
        fetchLocationSuggestions(query);
      }, 400);
      if (!hasActiveFilters()) {
        setFeedback("", false);
        applyVisibleProducts(defaultVisibleIds);
      }
    });

    if (locationSuggestions) {
      locationSuggestions.addEventListener("click", async (e) => {
        const button = e.target.closest("button");
        if (button && button.dataset.location) {
          locationInput.value = button.dataset.location;
          hideLocationSuggestions();
          geoCoords = null;
          await applyBrowseFilters();
        }
      });
    }
  }

  if (distanceSelect) {
    distanceSelect.addEventListener("change", async () => {
      await applyBrowseFilters();
    });
  }

  if (categorySelect) {
    categorySelect.addEventListener("change", async () => {
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

  // Hide suggestions when clicking outside
  document.addEventListener("click", (e) => {
    if (locationInput && !locationInput.contains(e.target) && locationSuggestions && !locationSuggestions.contains(e.target)) {
      hideLocationSuggestions();
    }
    if (searchInput && !searchInput.contains(e.target) && searchSuggestions && !searchSuggestions.contains(e.target)) {
      hideSearchSuggestions();
    }
  });
});
