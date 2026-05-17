const csrfToken =
	document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

function updatePostButtonState(activeBtn) {
	document.querySelectorAll('.post-filter-btn').forEach(function (btn) {
		btn.classList.remove('bg-blue-700', 'border-blue-700', 'text-white');
		btn.classList.add('border-slate-300', 'bg-white', 'text-slate-700');
	});

	activeBtn.classList.remove('border-slate-300', 'bg-white', 'text-slate-700');
	activeBtn.classList.add('bg-blue-700', 'border-blue-700', 'text-white');
}

function applyPostFilters() {
	const activeFilterBtn = document.querySelector('.post-filter-btn.bg-blue-700');
	const filter = activeFilterBtn ? activeFilterBtn.getAttribute('data-filter') : 'all';
	const searchValue = (document.getElementById('post-search-input').value || '').toLowerCase();

	document.querySelectorAll('.post-row').forEach(function (row) {
		const isLegit = row.getAttribute('data-legit') === 'true';
		const title = row.getAttribute('data-title') || '';
		const seller = row.getAttribute('data-seller') || '';

		let passFilter = true;
		if (filter === 'suspicious') {
			passFilter = !isLegit;
		} else if (filter === 'legit') {
			passFilter = isLegit;
		}

		const passSearch = title.includes(searchValue) || seller.includes(searchValue);
		row.style.display = (passFilter && passSearch) ? '' : 'none';
	});
}

function moderatePost(productId, action) {
	if (action === 'flag') {
		// flagging now uses a modal to collect reason
		openPostReportModal(productId);
		return;
	}

	const actionLabel = action === 'approve' ? 'mark this post as legit' : 'perform this action';
	if (!confirm('Are you sure you want to ' + actionLabel + '?')) {
		return;
	}

	const xhr = new XMLHttpRequest();
	xhr.open('POST', '/admin/reports', true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	if (csrfToken) {
		xhr.setRequestHeader('X-CSRFToken', csrfToken);
	}

	xhr.onload = function () {
		try {
			const data = JSON.parse(xhr.responseText);
			if (!data.ok) {
				alert(data.message || 'Unable to update post.');
				return;
			}
			window.location.reload();
		} catch (e) {
			alert('Unexpected response from server.');
		}
	};

	xhr.onerror = function () {
		alert('Unable to update post. Please try again.');
	};

	xhr.send(JSON.stringify({
		action: action,
		product_id: productId
	}));
}

function openPostReportModal(productId) {
	const input = document.getElementById('report-reason-input');
	const hidden = document.getElementById('report-product-id');
	if (input && hidden) {
		input.value = '';
		hidden.value = productId;
		document.getElementById('post-report-modal').classList.remove('hidden');
	}
}

function closePostReportModal() {
	document.getElementById('post-report-modal').classList.add('hidden');
}

function submitPostReport() {
	const reasonEl = document.getElementById('report-reason-input');
	const hidden = document.getElementById('report-product-id');
	const reason = reasonEl ? (reasonEl.value || '').trim() : '';
	const productId = hidden ? hidden.value : null;

	if (!productId) {
		alert('Missing product id.');
		return;
	}
	if (!reason) {
		alert('Please provide a reason for flagging this post.');
		return;
	}

	const xhr = new XMLHttpRequest();
	xhr.open('POST', '/admin/reports', true);
	xhr.setRequestHeader('Content-Type', 'application/json');
	if (csrfToken) {
		xhr.setRequestHeader('X-CSRFToken', csrfToken);
	}

	xhr.onload = function () {
		try {
			const data = JSON.parse(xhr.responseText);
			if (!data.ok) {
				alert(data.message || 'Unable to update post.');
				return;
			}
			window.location.reload();
		} catch (e) {
			alert('Unexpected response from server.');
		}
	};

	xhr.onerror = function () {
		alert('Unable to update post. Please try again.');
	};

	xhr.send(JSON.stringify({
		action: 'flag',
		product_id: Number(productId),
		reason: reason
	}));
}

function viewPostDetails(productId) {
	const row = document.querySelector('.post-row[data-post-id="' + productId + '"]');
	if (!row) {
		return;
	}

	const content = document.getElementById('post-modal-content');
	const imageUrl = row.getAttribute('data-image-url') || '';
	const imageBlock = imageUrl
		? `<div>
			<p class="text-sm font-medium text-slate-600">Image</p>
			<img src="${imageUrl}" alt="${row.getAttribute('data-name')}" class="mt-2 w-full max-h-72 rounded-lg border border-slate-200 object-cover" />
		</div>`
		: '';
	content.innerHTML = `
		<div class="space-y-4">
			${imageBlock}
			<div>
				<p class="text-sm font-medium text-slate-600">Title</p>
				<p class="text-slate-900 mt-1 font-semibold">${row.getAttribute('data-name')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Seller</p>
				<p class="text-slate-900 mt-1">${row.getAttribute('data-seller-name')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Category</p>
				<p class="text-slate-900 mt-1">${row.getAttribute('data-category')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Price</p>
				<p class="text-slate-900 mt-1">$${row.getAttribute('data-price')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Location</p>
				<p class="text-slate-900 mt-1">${row.getAttribute('data-location')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Status</p>
				<p class="text-slate-900 mt-1">${row.getAttribute('data-status')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Posted On</p>
				<p class="text-slate-900 mt-1">${row.getAttribute('data-created')}</p>
			</div>
			<div>
				<p class="text-sm font-medium text-slate-600">Description</p>
				<p class="text-slate-900 mt-1 text-sm bg-slate-50 p-3 rounded">${row.getAttribute('data-description')}</p>
			</div>
		</div>
	`;

	document.getElementById('post-modal').classList.remove('hidden');
}

function closePostModal() {
	document.getElementById('post-modal').classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', function () {
	document.querySelectorAll('.post-filter-btn').forEach(function (btn) {
		btn.addEventListener('click', function () {
			updatePostButtonState(btn);
			applyPostFilters();
		});
	});

	const searchInput = document.getElementById('post-search-input');
	if (searchInput) {
		searchInput.addEventListener('keyup', applyPostFilters);
	}

	const modal = document.getElementById('post-modal');
	if (modal) {
		modal.addEventListener('click', function (e) {
			if (e.target === modal) {
				closePostModal();
			}
		});
	}
});