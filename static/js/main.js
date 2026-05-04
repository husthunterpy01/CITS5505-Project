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
  const termsCheckbox = document.getElementById("terms-accepted-checkbox");
  const signupButton = document.getElementById("signup-submit-btn");
  const legalOverlay = document.getElementById("legal-modal-overlay");
  const legalTitle = document.getElementById("legal-modal-title");
  const legalContent = document.getElementById("legal-modal-content");
  const legalClose = document.getElementById("legal-modal-close");
  const legalTriggers = document.querySelectorAll("[data-legal-trigger]");

  if (!termsCheckbox || !signupButton) return;

  const LEGAL_COPY = {
    terms: {
      title: "Terms of Service",
      body: `
        <p>SwanFlip is for UWA community members only. By creating an account, you agree to use the marketplace honestly and respectfully.</p>
        <p>You must provide accurate listing details, including real item condition, clear pricing, and truthful descriptions.</p>
        <p>Transactions should be arranged safely in public places. Users are responsible for verifying items before payment.</p>
        <p>Illegal products, prohibited goods, scams, and abusive behavior are not allowed and may result in account suspension.</p>
      `,
    },
    privacy: {
      title: "Privacy Policy",
      body: `
        <p>We collect basic profile information (name, email) to create and secure your account.</p>
        <p>Your data is used to provide login/session functionality, listing management, and user-to-user communication features.</p>
        <p>We do not request unnecessary personal data for marketplace use.</p>
        <p>By continuing, you acknowledge that your account activity may be used to maintain platform safety and service quality.</p>
      `,
    },
  };

  const updateSignupButtonState = () => {
    const enabled = termsCheckbox.checked;
    signupButton.disabled = !enabled;
    signupButton.classList.toggle("opacity-50", !enabled);
    signupButton.classList.toggle("cursor-not-allowed", !enabled);
    signupButton.classList.toggle("hover:scale-105", enabled);
    signupButton.classList.toggle("hover:bg-blue-900", enabled);
  };

  const closeLegalModal = () => {
    if (!legalOverlay) return;
    legalOverlay.classList.add("hidden");
    legalOverlay.classList.remove("flex");
  };

  const openLegalModal = (kind) => {
    if (!legalOverlay || !legalTitle || !legalContent) return;
    const selected = LEGAL_COPY[kind] || LEGAL_COPY.terms;
    legalTitle.textContent = selected.title;
    legalContent.innerHTML = selected.body;
    legalOverlay.classList.remove("hidden");
    legalOverlay.classList.add("flex");
  };

  termsCheckbox.addEventListener("change", updateSignupButtonState);
  updateSignupButtonState();

  legalTriggers.forEach((btn) => {
    btn.addEventListener("click", () => {
      openLegalModal(btn.dataset.legalTrigger);
    });
  });

  if (legalClose) {
    legalClose.addEventListener("click", closeLegalModal);
  }

  if (legalOverlay) {
    legalOverlay.addEventListener("click", (event) => {
      if (event.target === legalOverlay) closeLegalModal();
    });
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeLegalModal();
  });
});
