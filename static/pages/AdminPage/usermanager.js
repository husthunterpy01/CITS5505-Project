let usersData = [];
let pendingReportUserId = null;

function redirectToReportedView() {
  const params = new URLSearchParams(window.location.search || '');
  const currentPerPage = params.get('per_page') || '10';
  params.set('view', 'reported');
  params.set('sort', 'status');
  params.set('direction', 'desc');
  params.set('page', '1');
  params.set('per_page', currentPerPage);
  window.location.href = `/admin/users?${params.toString()}`;
}

function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatActivityTimestamp(value) {
  if (!value) return 'Unknown time';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Unknown time';
  return date.toLocaleString([], {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function loadUsersFromDom() {
  const rows = document.querySelectorAll('.user-row');
  return Array.from(rows).map((row) => ({
    id: Number(row.getAttribute('data-user-id')),
    firstName: row.getAttribute('data-first-name') || '',
    lastName: row.getAttribute('data-last-name') || '',
    email: row.getAttribute('data-email') || '',
    role: row.getAttribute('data-role') || 'standard_user',
    isReport: row.getAttribute('data-reported') === 'true',
    review: row.getAttribute('data-review') || 'No notes',
    createdAt: row.getAttribute('data-created-at') || 'N/A',
    productCount: Number(row.getAttribute('data-product-count')) || 0,
  }));
}

// Initialize page with user data from global variable
function initializeUserManager(users) {
  usersData = users;
  setupEventListeners();
}

function updateUserReportStatus(userId, action, reason) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/admin/users', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (error) {
          reject(error);
        }
      } else {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (error) {
          reject(error);
        }
      }
    };

    xhr.onerror = function () {
      reject(new Error('Network request failed'));
    };

    xhr.send(
      JSON.stringify({
        user_id: userId,
        action: action,
        reason: reason || '',
      }),
    );
  });
}

function fetchUserActivities(userId) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/admin/users/${userId}/activity`, true);
    xhr.onload = function () {
      try {
        resolve(JSON.parse(xhr.responseText));
      } catch (error) {
        reject(error);
      }
    };
    xhr.onerror = function () {
      reject(new Error('Network request failed'));
    };
    xhr.send();
  });
}

function setupEventListeners() {
  // Filter functionality
  document.querySelectorAll('.filter-btn').forEach((btn) => {
    btn.addEventListener('click', function () {
      const filter = this.getAttribute('data-filter');

      // Update button states
      document.querySelectorAll('.filter-btn').forEach((b) => {
        b.classList.remove('bg-blue-700', 'border-blue-700', 'text-white');
        b.classList.add('border-slate-300', 'bg-white', 'text-slate-700');
      });
      this.classList.remove('border-slate-300', 'bg-white', 'text-slate-700');
      this.classList.add('bg-blue-700', 'border-blue-700', 'text-white');
      // Filter rows
      filterUsers(filter);
    });
  });

  // Search functionality
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('keyup', function () {
      const searchTerm = this.value.toLowerCase();
      const rows = document.querySelectorAll('.user-row');

      rows.forEach((row) => {
        const name = row.getAttribute('data-name');
        const email = row.getAttribute('data-email-search') || '';

        if (name.includes(searchTerm) || email.includes(searchTerm)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }

  // Close modal when clicking outside
  const modal = document.getElementById('user-modal');
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === this) {
        closeModal();
      }
    });
  }

  const reportModal = document.getElementById('report-modal');
  if (reportModal) {
    reportModal.addEventListener('click', function (e) {
      if (e.target === this) {
        closeReportReasonModal();
      }
    });
  }

  const reportCancelBtn = document.getElementById('report-cancel');
  if (reportCancelBtn) {
    reportCancelBtn.addEventListener('click', function () {
      closeReportReasonModal();
    });
  }

  const reportForm = document.getElementById('report-form');
  if (reportForm) {
    reportForm.addEventListener('submit', function (e) {
      e.preventDefault();

      if (!pendingReportUserId) {
        return;
      }

      const reasonInput = document.getElementById('report-reason');
      const errorLabel = document.getElementById('report-form-error');
      const reason = (reasonInput?.value || '').trim();

      if (!reason) {
        if (errorLabel) {
          errorLabel.textContent = 'Report reason is required.';
          errorLabel.classList.remove('hidden');
        }
        return;
      }

      if (errorLabel) {
        errorLabel.classList.add('hidden');
      }

      updateUserReportStatus(pendingReportUserId, 'report', reason)
        .then((result) => {
          if (!result.ok) {
            if (errorLabel) {
              errorLabel.textContent =
                result.message || 'Unable to update user status.';
              errorLabel.classList.remove('hidden');
            }
            return;
          }
          redirectToReportedView();
        })
        .catch(() => {
          if (errorLabel) {
            errorLabel.textContent =
              'Unable to update user status. Please try again.';
            errorLabel.classList.remove('hidden');
          }
        });
    });
  }
}

function openReportReasonModal(userId) {
  pendingReportUserId = userId;
  const reportModal = document.getElementById('report-modal');
  const reasonInput = document.getElementById('report-reason');
  const errorLabel = document.getElementById('report-form-error');

  if (reasonInput) {
    reasonInput.value = '';
    reasonInput.focus();
  }

  if (errorLabel) {
    errorLabel.classList.add('hidden');
  }

  if (reportModal) {
    reportModal.classList.remove('hidden');
  }
}

function closeReportReasonModal() {
  pendingReportUserId = null;
  const reportModal = document.getElementById('report-modal');
  if (reportModal) {
    reportModal.classList.add('hidden');
  }
}

function filterUsers(filter) {
  const rows = document.querySelectorAll('.user-row');

  rows.forEach((row) => {
    const isReported = row.getAttribute('data-reported') === 'true';
    const isAdmin = row.getAttribute('data-role') === 'admin';

    if (filter === 'all') {
      row.style.display = '';
    } else if (filter === 'reported') {
      row.style.display = isReported ? '' : 'none';
    } else if (filter === 'active') {
      row.style.display = !isReported && !isAdmin ? '' : 'none';
    } else if (filter === 'admin') {
      row.style.display = isAdmin ? '' : 'none';
    }
  });
}

function viewUserDetails(userId) {
  const user = usersData.find((u) => u.id === userId);
  if (!user) return;

  const modal = document.getElementById('user-modal');
  const content = document.getElementById('modal-content');

  content.innerHTML = `
    <div class="space-y-4">
      <div class="flex items-center justify-center gap-3 pb-4 border-b border-slate-200">
        <div class="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold text-lg">
          ${user.firstName[0].toUpperCase()}${user.lastName[0].toUpperCase()}
        </div>
        <div>
          <h3 class="font-semibold text-slate-900">${user.firstName} ${user.lastName}</h3>
          <p class="text-sm text-slate-500">${user.email}</p>
        </div>
      </div>
      
      <div>
        <p class="text-sm font-medium text-slate-600">Role</p>
        <p class="text-slate-900 mt-1"><span class="role-badge role-${user.role.toLowerCase()}">${user.role.charAt(0).toUpperCase() + user.role.slice(1)}</span></p>
      </div>
      
      <div>
        <p class="text-sm font-medium text-slate-600">Status</p>
        <p class="text-slate-900 mt-1">
          ${user.isReport ? '<span class="user-status-badge status-reported">Reported</span>' : '<span class="user-status-badge status-active">Active</span>'}
        </p>
      </div>
      
      <div>
        <p class="text-sm font-medium text-slate-600">Joined</p>
        <p class="text-slate-900 mt-1">${user.createdAt}</p>
      </div>
      
      <div>
        <p class="text-sm font-medium text-slate-600">Products Listed</p>
        <p class="text-slate-900 mt-1">${user.productCount}</p>
      </div>
      
      <div>
        <p class="text-sm font-medium text-slate-600">Notes</p>
        <p class="text-slate-900 mt-1 text-sm bg-slate-50 p-2 rounded">${user.review}</p>
      </div>

      <div>
        <p class="text-sm font-medium text-slate-600">Recent Activity</p>
        <div id="user-activity-feed" class="activity-trace mt-2">
          <p class="activity-trace-empty">Loading activity...</p>
        </div>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
  const activityFeed = document.getElementById('user-activity-feed');
  fetchUserActivities(userId)
    .then((result) => {
      if (!activityFeed) return;
      if (!result.ok) {
        activityFeed.innerHTML = `<p class="text-red-600">${escapeHtml(result.message || 'Failed to load user activity.')}</p>`;
        return;
      }
      const activities = result.activities || [];
      if (!activities.length) {
        activityFeed.innerHTML =
          '<p class="activity-trace-empty">No activities recorded yet.</p>';
        return;
      }
      const rowsHtml = activities
        .map((activity) => {
          const targetLabel = `${activity.target_type || 'unknown'}#${activity.target_id ?? '-'}`;
          return `
            <tr>
              <td>${escapeHtml(formatActivityTimestamp(activity.created_at))}</td>
              <td>${escapeHtml(activity.action)}</td>
              <td>${escapeHtml(targetLabel)}</td>
              <td>${escapeHtml(activity.actor_name)}</td>
              <td>${escapeHtml(activity.reason || '-')}</td>
            </tr>
          `;
        })
        .join('');
      activityFeed.innerHTML = `
        <div class="activity-trace-table-wrap">
          <table class="activity-trace-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Action</th>
                <th>Target</th>
                <th>Actor</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>${rowsHtml}</tbody>
          </table>
        </div>
      `;
    })
    .catch(() => {
      if (!activityFeed) return;
      activityFeed.innerHTML =
        '<p class="activity-trace-error">Unable to load user activity.</p>';
    });
}

function closeModal() {
  const modal = document.getElementById('user-modal');
  modal.classList.add('hidden');
}

function reportUser(userId) {
  const user = usersData.find((u) => u.id === userId);
  if (!user) return;

  // Prevent reporting admins
  if (user.role.toLowerCase() === 'admin') {
    alert('Admin users cannot be reported.');
    return;
  }

  openReportReasonModal(userId);
}

function unreportUser(userId) {
  if (confirm('Are you sure you want to unreport this user?')) {
    updateUserReportStatus(userId, 'unreport', '')
      .then((result) => {
        if (!result.ok) {
          alert(result.message || 'Unable to update user status.');
          return;
        }
        window.location.reload();
      })
      .catch(() => {
        alert('Unable to update user status. Please try again.');
      });
  }
}

// Initialize safely for both static and dynamically injected script loading.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function () {
    initializeUserManager(loadUsersFromDom());
  });
} else {
  initializeUserManager(loadUsersFromDom());
}
