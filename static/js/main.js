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
<<<<<<< HEAD
=======
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
        <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p class="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">Effective date: 1 January 2026</p>
          <h3 class="mt-3 text-lg font-semibold text-slate-800">1. Account Use and Eligibility</h3>
          <p>SwanFlip is a student marketplace intended for the UWA community, and by creating an account you agree to use the platform honestly, respectfully, and in good faith.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">2. Listing Accuracy and Conduct</h3>
          <p class="mt-3">You are responsible for ensuring that listings are accurate, including item condition, photos, availability, and pricing, and you must not post misleading, deceptive, or fraudulent content.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">3. Buyer and Seller Responsibilities</h3>
          <p class="mt-3">Buyers and sellers are responsible for communicating clearly, arranging safe public meetups where possible, and verifying items before completing transactions.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">4. Risk, Safety and Enforcement</h3>
          <p class="mt-3">SwanFlip does not guarantee product quality, seller reliability, or delivery outcomes, so users should apply reasonable caution when trading.</p>
          <p class="mt-3">Prohibited activity includes illegal or unsafe goods, impersonation, harassment, spam, payment scams, or conduct that violates Australian law or UWA policies.</p>
          <p class="mt-3">We may remove listings, restrict account access, or suspend users who breach rules or create safety risks. By continuing, you acknowledge marketplace interactions are user-to-user transactions and agree to moderation and safety processes that help maintain a trusted campus marketplace.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">5. Policy Updates</h3>
          <p class="mt-3">If terms are updated, the latest version will be shown at signup, and continued use of your account indicates acceptance of revisions unless additional consent is required by law.</p>
        </div>
      `,
    },
    privacy: {
      title: "Privacy Policy",
      body: `
        <div class="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p class="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">Effective date: 1 January 2026</p>
          <h3 class="mt-3 text-lg font-semibold text-slate-800">1. Information We Collect</h3>
          <p>SwanFlip collects and uses personal information only as needed to provide a safe and functional marketplace experience for the UWA community.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">2. How We Use Information</h3>
          <p class="mt-3">When you register, we collect account details such as your name, email address, and encrypted password to authenticate users, secure accounts, and support core features like listing management and user communication.</p>
          <p class="mt-3">We may also process marketplace activity data, such as listing updates and in-platform interactions, to detect abuse, reduce fraud, and improve platform safety and reliability.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">3. Data Minimization and Safety</h3>
          <p class="mt-3">We do not intentionally request unnecessary sensitive personal information for normal use of the service, and we expect users not to publish private information in listings or messages.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">4. Retention and Compliance</h3>
          <p class="mt-3">Your data is used for account operations, service quality, moderation, and security monitoring, and may be retained for a reasonable period to meet legal, operational, or dispute-handling needs.</p>
          <h3 class="mt-4 text-lg font-semibold text-slate-800">5. Your Acknowledgement</h3>
          <p class="mt-3">By creating an account, you acknowledge and consent to this data use model and understand that reasonable safeguards, moderation checks, and policy enforcement are part of maintaining a secure campus marketplace.</p>
          <p class="mt-3">You can request profile updates by editing account details, and we may retain limited records where required for legal obligations, fraud prevention, or dispute resolution.</p>
        </div>
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
>>>>>>> origin/main
});
