document.addEventListener("DOMContentLoaded", function () {
  const mainImage = document.getElementById("product-main-image");
  const thumbButtons = Array.from(
    document.querySelectorAll(".product-thumb-btn[data-image-url]"),
  );
  const chatButton = document.getElementById("product-chat-seller-btn");
  const mapEl = document.getElementById("product-location-map");
  const mapFallback = document.getElementById("product-location-map-fallback");

  function setActiveThumb(activeBtn) {
    thumbButtons.forEach((btn) => {
      btn.classList.remove("border-blue-600", "ring-2", "ring-blue-200");
      btn.classList.add("border-slate-200");
    });
    if (!activeBtn) return;
    activeBtn.classList.remove("border-slate-200");
    activeBtn.classList.add("border-blue-600", "ring-2", "ring-blue-200");
  }

  thumbButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const nextImage = btn.dataset.imageUrl;
      if (!mainImage || !nextImage) return;
      mainImage.src = nextImage;
      setActiveThumb(btn);
    });
  });

  if (chatButton) {
    chatButton.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const sellerId = Number(chatButton.dataset.sellerId || 0);
      if (!sellerId) {
        alert("Unable to open chat for this seller.");
        return;
      }

      document.dispatchEvent(
        new CustomEvent("swanflip:chat-start", {
          detail: {
            targetUserId: sellerId,
            productId: Number(chatButton.dataset.productId || 0) || null,
            displayName:
              chatButton.dataset.sellerName ||
              chatButton.dataset.productTitle ||
              "Seller",
            productImageUrl: chatButton.dataset.productImage || "",
            role: "standard_user",
          },
        }),
      );
    });
  }

  if (mapEl) {
    try {
      const lat = Number(mapEl.dataset.lat);
      const lon = Number(mapEl.dataset.lon);
      const radiusMeters = Number(mapEl.dataset.radiusMeters || 1300);
      const hasCoords =
        Number.isFinite(lat) &&
        Number.isFinite(lon) &&
        Math.abs(lat) <= 90 &&
        Math.abs(lon) <= 180;

      if (!(hasCoords && window.L)) {
        throw new Error("Map dependencies unavailable or coordinates invalid.");
      }

      const map = L.map(mapEl, {
        zoomControl: true,
        scrollWheelZoom: false,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      const center = [lat, lon];
      const circle = L.circle(center, {
        radius: Number.isFinite(radiusMeters) ? radiusMeters : 1300,
        color: "#2563eb",
        weight: 2,
        fillColor: "#60a5fa",
        fillOpacity: 0.25,
      }).addTo(map);

      L.circleMarker(center, {
        radius: 5,
        color: "#1d4ed8",
        fillColor: "#1d4ed8",
        fillOpacity: 1,
      }).addTo(map);

      map.setView(center, 12);
      setTimeout(() => {
        map.invalidateSize();
      }, 0);
    } catch (error) {
      console.error("Product map failed to initialize:", error);
      mapEl.classList.add("hidden");
      if (mapFallback) {
        mapFallback.classList.remove("hidden");
        mapFallback.classList.add("flex");
      }
    }
  }
});
