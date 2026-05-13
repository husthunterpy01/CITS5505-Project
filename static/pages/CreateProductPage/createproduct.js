const locationInput = document.getElementById('location-name');
const latitudeInput = document.getElementById('location-latitude');
const longitudeInput = document.getElementById('location-longitude');
const suggestionsBox = document.getElementById('location-suggestions');
const locationError = document.getElementById('location-client-error');

let locationTimer = null;
let latestLocations = [];

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

suggestionsBox.addEventListener('click', function (event) {
  const button = event.target.closest('button');
  if (!button) return;

  locationInput.value = button.dataset.name;
  latitudeInput.value = button.dataset.latitude;
  longitudeInput.value = button.dataset.longitude;

  hideLocationError();
  hideSuggestions();
});

document.addEventListener('click', function (event) {
  if (
    !suggestionsBox.contains(event.target) &&
    event.target !== locationInput
  ) {
    hideSuggestions();
  }
});
