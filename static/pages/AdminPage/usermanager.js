// User data embedded in the page
let usersData = [];

// Initialize page with user data from global variable
function initializeUserManager(users) {
  usersData = users;
  setupEventListeners();
}

function setupEventListeners() {
  // Filter functionality
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const filter = this.getAttribute('data-filter');
      
      // Update button states
      document.querySelectorAll('.filter-btn').forEach(b => {
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
    searchInput.addEventListener('keyup', function() {
      const searchTerm = this.value.toLowerCase();
      const rows = document.querySelectorAll('.user-row');
      
      rows.forEach(row => {
        const name = row.getAttribute('data-name');
        const email = row.getAttribute('data-email');
        
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
    modal.addEventListener('click', function(e) {
      if (e.target === this) {
        closeModal();
      }
    });
  }
}

function filterUsers(filter) {
  const rows = document.querySelectorAll('.user-row');
  
  rows.forEach(row => {
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
  const user = usersData.find(u => u.id === userId);
  if (!user) return;

  const modal = document.getElementById('user-modal');
  const content = document.getElementById('modal-content');

  const isAdmin = user.role.toLowerCase() === 'admin';

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
          ${user.isReport ? '<span class="user-status-badge status-reported">🚩 Reported</span>' : '<span class="user-status-badge status-active">✓ Active</span>'}
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
      
      ${isAdmin ? '<div class="text-sm text-slate-500 bg-blue-50 p-3 rounded">Admin users cannot be reported.</div>' : ''}
    </div>
  `;

  modal.classList.remove('hidden');
}

function closeModal() {
  const modal = document.getElementById('user-modal');
  modal.classList.add('hidden');
}

function reportUser(userId) {
  const user = usersData.find(u => u.id === userId);
  if (!user) return;

  // Prevent reporting admins
  if (user.role.toLowerCase() === 'admin') {
    alert('Admin users cannot be reported.');
    return;
  }

  if (confirm('Are you sure you want to report this user?')) {
    // This would typically call an API endpoint to update the user status
    alert('User reported successfully. This would be implemented with a backend API call.');
  }
}

function unreportUser(userId) {
  if (confirm('Are you sure you want to unreport this user?')) {
    // This would typically call an API endpoint to update the user status
    alert('User unreported successfully. This would be implemented with a backend API call.');
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  setupEventListeners();
  // Initialize the user manager if usersData is available
  if (typeof usersData !== 'undefined' && usersData.length > 0) {
    initializeUserManager(usersData);
  }
});
