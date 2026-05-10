const updateForm = document.getElementById('update-product-form');
const imagesInput = document.querySelector('input[type="file"][name="images"]');
const imageDeleteError = document.getElementById('image-delete-error');

if (updateForm && imagesInput) {
  updateForm.addEventListener('submit', function (event) {
    if (imageDeleteError) {
      imageDeleteError.textContent = '';
      imageDeleteError.classList.add('hidden');
    }

    const totalImages = Number(updateForm.dataset.imageCount || 0);
    const deleteCheckboxes = document.querySelectorAll(
      'input[name="delete_image_ids"]:checked',
    );
    const uploadedImages = imagesInput.files ? imagesInput.files.length : 0;

    if (
      totalImages > 0 &&
      deleteCheckboxes.length === totalImages &&
      uploadedImages === 0
    ) {
      event.preventDefault();

      const errorMessage =
        'You cannot delete all existing images. Upload at least one new image before deleting the last image.';

      if (imageDeleteError) {
        imageDeleteError.textContent = errorMessage;
        imageDeleteError.classList.remove('hidden');
      } else {
        alert(errorMessage);
      }
    }
  });
}
