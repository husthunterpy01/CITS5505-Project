document.addEventListener("DOMContentLoaded", function () {
  const root = document.getElementById("browse-root");
  const grid = document.getElementById("browse-product-grid");
  const feedback = document.getElementById("browse-search-feedback");

  function escapeHtml(value) {
    if (value == null) return "";
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
  }

  function statusBadgeClass(status) {
    if (status === "available") return "bg-green-100 text-green-700";
    if (status === "sold") return "bg-red-100 text-red-700";
    return "bg-slate-100 text-slate-600";
  }

  function capitalizeStatus(status) {
    if (!status) return "";
    return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
  }

  function renderProductCard(product) {
    const isSold = product.status === "sold";
    const price = Number(product.price);
    const priceStr = Number.isFinite(price) ? price.toFixed(2) : "0.00";
    const chatBlock = isSold
      ? ""
      : `<button type="button" class="chat-seller-btn mt-5 w-full rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-800" data-product-id="${escapeHtml(product.product_id)}" data-seller-name="${escapeHtml(product.seller_name)}" data-product-title="${escapeHtml(product.title)}" data-product-status="${escapeHtml(product.status)}">Chat with Seller</button>`;

    return `
      <article class="browse-product-card flex w-full sm:w-[calc(50%-12px)] lg:w-[calc(33.333%-16px)] xl:w-[calc(25%-18px)] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md">
        <div class="aspect-[4/3] w-full overflow-hidden bg-slate-100">
          <img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" class="h-full w-full object-cover" />
        </div>
        <div class="flex flex-1 flex-col p-5">
          <h2 class="text-lg font-semibold text-slate-800">${escapeHtml(product.title)}</h2>
          <p class="mt-2 text-sm font-medium text-blue-700">$${priceStr}</p>
          <div class="mt-2 flex items-center justify-between gap-3">
            <p class="mt-2 text-sm text-slate-500">${escapeHtml(product.location)}</p>
            <span class="rounded-full px-3 py-1 text-xs font-semibold ${statusBadgeClass(product.status)}">${escapeHtml(capitalizeStatus(product.status))}</span>
          </div>
          <p class="mt-3 flex-1 text-sm leading-6 text-slate-600">${escapeHtml(product.description || "")}</p>
          ${chatBlock}
        </div>
      </article>
    `;
  }

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

  document.addEventListener("swanflip:browse-search", async function (ev) {
    const raw = ev.detail && ev.detail.query != null ? String(ev.detail.query) : "";
    const q = raw.trim();

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
      if (items.length === 0) {
        grid.innerHTML =
          '<p class="w-full py-8 text-center text-sm text-slate-600">No listings to show. Try different keywords or clear the search.</p>';
      } else {
        grid.innerHTML = items.map(renderProductCard).join("");
      }
    } catch {
      setFeedback("Something went wrong. Please try again.", true);
    } finally {
      grid.classList.remove("opacity-60", "pointer-events-none");
    }
  });
});
