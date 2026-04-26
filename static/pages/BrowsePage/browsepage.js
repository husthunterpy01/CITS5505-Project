document.addEventListener("DOMContentLoaded", function () {
  const chatButtons = document.querySelectorAll(".chat-seller-btn");

  chatButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const sellerName = this.dataset.sellerName;
      const productTitle = this.dataset.productTitle;
      const productId = this.dataset.productId;

      alert(
        `Chat feature coming soon.\n\nSeller: ${sellerName}\nProduct: ${productTitle}\nProduct ID: ${productId}`,
      );
    });
  });
});
