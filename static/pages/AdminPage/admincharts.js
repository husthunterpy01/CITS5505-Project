document.addEventListener('DOMContentLoaded', function () {
  if (typeof Chart === 'undefined') return;

  const chartDataScript = document.getElementById('admin-chart-data');
  let chartData = {};
  if (chartDataScript) {
    try {
      chartData = JSON.parse(chartDataScript.textContent || '{}');
    } catch (error) {
      chartData = {};
    }
  } else {
    chartData = window.adminChartData || {};
  }

  const colorPalette = ['#2563eb', '#0ea5e9', '#14b8a6', '#22c55e', '#f59e0b', '#f97316', '#ef4444'];
  const safeArray = (value) => (Array.isArray(value) ? value : []);

  function hasData(values) {
    return safeArray(values).some((value) => Number(value) > 0);
  }

  function getChartAnimationOptions() {
    return {
      animation: {
        duration: 900,
        easing: 'easeOutQuart',
      },
      transitions: {
        active: {
          animation: {
            duration: 250,
          },
        },
      },
    };
  }

  function renderTrendChart() {
    const canvas = document.getElementById('adminTrendChart');
    if (!canvas) return;

    const trend = chartData.trend || {};
    const labels = safeArray(trend.labels);
    const users = safeArray(trend.users);
    const products = safeArray(trend.products);

    if (!labels.length || (!hasData(users) && !hasData(products))) {
      canvas.parentElement.insertAdjacentHTML('beforeend', '<p class="mt-3 text-xs text-slate-500">No recent trend data available.</p>');
      return;
    }

    new Chart(canvas, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'New Users',
            data: users,
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.15)',
            tension: 0.35,
            fill: true,
          },
          {
            label: 'New Listings',
            data: products,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.15)',
            tension: 0.35,
            fill: true,
          },
        ],
      },
      options: {
        ...getChartAnimationOptions(),
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 },
          },
        },
      },
    });
  }

  function renderCategoricalChart(canvasId, labels, values, title, chartType) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (!safeArray(labels).length || !hasData(values)) {
      canvas.parentElement.insertAdjacentHTML('beforeend', `<p class="mt-3 text-xs text-slate-500">No ${title.toLowerCase()} data available.</p>`);
      return;
    }

    new Chart(canvas, {
      type: chartType,
      data: {
        labels,
        datasets: [
          {
            label: title,
            data: values,
            backgroundColor: colorPalette,
            borderColor: colorPalette,
            borderWidth: 1,
            fill: chartType === 'radar',
          },
        ],
      },
      options: {
        ...getChartAnimationOptions(),
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
        },
        scales: chartType === 'bar'
          ? {
              y: {
                beginAtZero: true,
                ticks: { precision: 0 },
              },
            }
          : chartType === 'radar'
            ? {
                r: {
                  beginAtZero: true,
                  ticks: { precision: 0 },
                },
              }
            : undefined,
      },
    });
  }

  function renderProductMap() {
    const mapElement = document.getElementById('adminSalesMap');
    if (!mapElement) return;

    if (typeof L === 'undefined') {
      mapElement.insertAdjacentHTML('beforeend', '<p class="p-3 text-xs text-slate-500">Map library not available.</p>');
      return;
    }

    const productLocations = safeArray(chartData.product_locations)
      .filter((item) => Number(item && item.latitude) && Number(item && item.longitude) && Number(item && item.count) > 0);

    if (!productLocations.length) {
      mapElement.insertAdjacentHTML('beforeend', '<p class="p-3 text-xs text-slate-500">No product location data available.</p>');
      return;
    }

    const map = L.map(mapElement, {
      scrollWheelZoom: false,
      zoomControl: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    const bounds = [];
    productLocations.forEach((location) => {
      const lat = Number(location.latitude);
      const lng = Number(location.longitude);
      const productCount = Number(location.count);

      bounds.push([lat, lng]);

      L.circleMarker([lat, lng], {
        radius: Math.min(24, 6 + productCount * 2),
        color: '#1d4ed8',
        weight: 2,
        fillColor: '#3b82f6',
        fillOpacity: 0.35,
      })
        .addTo(map)
        .bindPopup(`<strong>${location.name || 'Unknown location'}</strong><br/>Products: ${productCount}`);
    });

    if (bounds.length === 1) {
      map.setView(bounds[0], 11);
    } else {
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  }

  renderTrendChart();
  renderCategoricalChart(
    'adminProductStatusChart',
    safeArray(chartData.product_status && chartData.product_status.labels),
    safeArray(chartData.product_status && chartData.product_status.values),
    'Product Status',
    'bar'
  );
  renderCategoricalChart(
    'adminCategoryChart',
    safeArray(chartData.top_categories && chartData.top_categories.labels),
    safeArray(chartData.top_categories && chartData.top_categories.values),
    'Top Categories',
    'radar'
  );
  renderProductMap();
});
