const updateForm = document.getElementById('update-product-form');
const imagesInput = document.querySelector('input[type="file"][name="images"]');
const imageDeleteError = document.getElementById('image-delete-error');

// Location suggestion elements
const locationInput = document.getElementById('location-name');
const latitudeInput = document.getElementById('location-latitude');
const longitudeInput = document.getElementById('location-longitude');
const suggestionsBox = document.getElementById('location-suggestions');
const locationError = document.getElementById('location-client-error');

let locationTimer = null;
let latestLocations = [];

// Location helper functions
function clearSelectedLocation() {
  latitudeInput.value = '';
  longitudeInput.value = '';
}

function showLocationError(message) {
  locationError.textContent = message;
  locationError.classList.remove('hidden');
}

function hideLocationError() {
  locationError.textContent = '';
  locationError.classList.add('hidden');
}

function showLoading() {
  suggestionsBox.innerHTML = `
    <div class="p-3">
      <div class="h-1 w-full overflow-hidden rounded bg-slate-200">
        <div class="h-full w-1/2 animate-pulse rounded bg-blue-700"></div>
      </div>
      <p class="mt-2 text-xs text-slate-500">Searching locations...</p>
    </div>
  `;
  suggestionsBox.classList.remove('hidden');
}

function showError(message) {
  suggestionsBox.innerHTML = `<div class="px-3 py-2 text-sm text-red-600">${message}</div>`;
  suggestionsBox.classList.remove('hidden');
}

function hideSuggestions() {
  suggestionsBox.classList.add('hidden');
  suggestionsBox.innerHTML = '';
}

function renderSuggestions(locations) {
  latestLocations = locations;

  suggestionsBox.innerHTML = locations
    .map(
      (location) => `
    <button
      type="button"
      class="block w-full px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
      data-name="${location.name}"
      data-latitude="${location.latitude}"
      data-longitude="${location.longitude}"
    >
      ${location.label}
    </button>
  `,
    )
    .join('');

  suggestionsBox.classList.remove('hidden');
}

async function fetchLocations(query) {
  const response = await fetch(
    `/api/locations/suggest?q=${encodeURIComponent(query)}`,
  );
  const data = await response.json();

  if (!response.ok || !data.ok) {
    throw new Error(data.message || 'Location lookup failed.');
  }

  return data.locations || [];
}

// Location input event listeners
if (locationInput) {
  locationInput.addEventListener('input', function () {
    const query = locationInput.value.trim();
    clearSelectedLocation();
    hideLocationError();
    latestLocations = [];

    clearTimeout(locationTimer);

    if (query.length < 3) {
      hideSuggestions();
      return;
    }

    showLoading();

    locationTimer = setTimeout(async function () {
      try {
        const locations = await fetchLocations(query);

        if (!locations.length) {
          showError('No matching WA suburb found.');
          showLocationError('Please enter a valid WA suburb.');
          return;
        }

        renderSuggestions(locations);
      } catch (error) {
        showError(error.message);
      }
    }, 600);
  });

  locationInput.addEventListener('blur', function () {
    setTimeout(async function () {
      const typedLocation = locationInput.value.trim();

      if (!typedLocation) {
        return; // No input, nothing to do
      }

      if (latitudeInput.value && longitudeInput.value) {
        return; // Already has coordinates, valid
      }

      if (typedLocation.length < 3) {
        showLocationError('Please enter a valid WA suburb.');
        return;
      }

      // Fetch suggestions for the typed location
      try {
        const locations = await fetchLocations(typedLocation);

        // Check for case-insensitive match
        const typedLower = typedLocation.toLowerCase();
        const matchedLocation = locations.find(
          (location) => location.name.toLowerCase() === typedLower,
        );

        if (matchedLocation) {
          // Auto-correct: replace input with proper name and set coordinates
          locationInput.value = matchedLocation.name;
          latitudeInput.value = matchedLocation.latitude;
          longitudeInput.value = matchedLocation.longitude;
          hideLocationError();
        } else {
          showLocationError('Please enter a valid WA suburb.');
        }
      } catch (error) {
        showLocationError('Location lookup failed. Please try again.');
      }
    }, 200);
  });
}

// Location suggestions click handler
if (suggestionsBox) {
  suggestionsBox.addEventListener('click', function (event) {
    const button = event.target.closest('button');
    if (!button) return;

    locationInput.value = button.dataset.name;
    latitudeInput.value = button.dataset.latitude;
    longitudeInput.value = button.dataset.longitude;

    hideLocationError();
    hideSuggestions();
  });
}

// Form submit validation for location
if (updateForm) {
  updateForm.addEventListener('submit', async function (event) {
    const typedLocation = locationInput.value.trim();

    if (latitudeInput.value && longitudeInput.value) {
      // Already valid, proceed with image check
    } else {
      // Location not set, try to validate
      event.preventDefault();

      if (typedLocation.length < 3) {
        showLocationError('Please enter a valid WA suburb.');
        return;
      }

      showLoading();

      try {
        const locations = await fetchLocations(typedLocation);
        const exactMatch = locations.find(
          (location) =>
            location.name.toLowerCase() === typedLocation.toLowerCase(),
        );

        if (!exactMatch) {
          showError('Please select a valid WA suburb from the suggestions.');
          showLocationError('Please enter a valid WA suburb.');
          return;
        }

        locationInput.value = exactMatch.name;
        latitudeInput.value = exactMatch.latitude;
        longitudeInput.value = exactMatch.longitude;

        hideLocationError();
        hideSuggestions();
        // Now proceed with image check
      } catch (error) {
        showLocationError(error.message);
        showError(error.message);
        return;
      }
    }

    // Image validation (existing code)
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

// Hide suggestions when clicking outside
document.addEventListener('click', function (event) {
  if (
    suggestionsBox &&
    !suggestionsBox.contains(event.target) &&
    event.target !== locationInput
  ) {
    hideSuggestions();
  }
});
