const tabButtons = document.querySelectorAll('.profile-tab-button');
const tabPanels = document.querySelectorAll('.profile-tab-panel');

// Define active tab in profile page
const activateTab = (targetId) => {
    tabPanels.forEach((panel) => {
        panel.classList.toggle('hidden', panel.id !== targetId);
    });

    tabButtons.forEach((button) => {
        const isActive = button.dataset.tabTarget === targetId;
        button.setAttribute('aria-selected', isActive ? 'true' : 'false');
        button.classList.toggle('border-blue-700', isActive);
        button.classList.toggle('text-blue-700', isActive);
        button.classList.toggle('border-transparent', !isActive);
        button.classList.toggle('text-slate-500', !isActive);
        button.classList.toggle('hover:text-slate-700', !isActive);
    });
};

tabButtons.forEach((button) => {
    button.addEventListener('click', () => activateTab(button.dataset.tabTarget));
});

const setupPasswordVisibilityToggles = () => {
    const toggleButtons = document.querySelectorAll('[data-toggle-password]');

    toggleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const targetInputId = button.getAttribute('data-target-input');
            const targetInput = document.getElementById(targetInputId);

            if (!targetInput) {
                return;
            }

            const shouldShow = targetInput.type === 'password';
            targetInput.type = shouldShow ? 'text' : 'password';
            button.textContent = shouldShow ? 'Hide' : 'Show';
            button.setAttribute('aria-label', shouldShow ? 'Hide password' : 'Show password');
        });
    });
};

const ajaxGetJson = (url, errorMessage) => {
    return new Promise((resolve, reject) => {
        const request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.responseType = 'json';

        request.onload = () => {
            if (request.status >= 200 && request.status < 300) {
                resolve(request.response);
                return;
            }
            reject(new Error(errorMessage));
        };

        request.onerror = () => {
            reject(new Error(errorMessage));
        };

        request.send();
    });
};

// Define data sources for profile page (mock file or API)
const DataSources = {
    async fromMockFile() {
        return await ajaxGetJson('/static/mock_userdata.json', 'Failed to load mock user data');
    },

    async fromApi() {
        return await ajaxGetJson('/api/profile', 'Failed to load API profile data');
    },
};

// Sanitize input data
const normalizeProfile = (raw) => {
    const user = raw?.user || {};
    const stats = user.stats || {};
    const charts = raw?.charts || {};

    return {
        user: {
            username: user.username || 'Master User',
            firstName: user.first_name || '',
            lastName: user.last_name || '',
            email: user.email || '',
            memberSince: user.member_since || '-',
            lastLogin: user.last_login || '-',
            stats: {
                totalTransactions: stats.total_transactions ?? 0,
                successfulTransactions: stats.successful_transactions ?? 0,
                posts: stats.posts ?? 0,
                comments: stats.comments ?? 0,
            },
        },
        charts: {
            totalBuyingByMonth: {
                labels: charts.totalBuyingByMonth?.labels || [],
                values: charts.totalBuyingByMonth?.values || [],
            },
            postsComments: {
                posts: charts.postsComments?.posts ?? stats.posts ?? 0,
                comments: charts.postsComments?.comments ?? stats.comments ?? 0,
            },
        },
    };
};

// Define common to replace values
const setText = (id, value) => {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
};

const setValue = (id, value) => {
    const element = document.getElementById(id);
    if (element) {
        element.value = value;
    }
};

// Define placeholder for charts for new users with no data
const toggleChartPlaceholder = (canvasId, placeholderId, showPlaceholder) => {
    const canvas = document.getElementById(canvasId);
    const placeholder = document.getElementById(placeholderId);

    if (canvas) {
        canvas.classList.toggle('hidden', showPlaceholder);
    }

    if (placeholder) {
        placeholder.classList.toggle('hidden', !showPlaceholder);
        placeholder.classList.toggle('flex', showPlaceholder);
    }
};

// Pour data into profile page and render charts
const renderProfile = (profile) => {
    setText('profile-username', profile.user.username);

    setValue('first-name', profile.user.firstName);
    setValue('last-name', profile.user.lastName);
    setValue('email', profile.user.email);

    setText('stat-total-transactions', profile.user.stats.totalTransactions);
    setText('stat-successful-transactions', profile.user.stats.successfulTransactions);
    setText('stat-failed-transactions', Math.max(profile.user.stats.totalTransactions - profile.user.stats.successfulTransactions, 0));
    setText('stat-posts', profile.user.stats.posts);
    setText('stat-comments', profile.user.stats.comments);
    setText('stat-last-login', profile.user.lastLogin);
    setText('stat-member-since', profile.user.memberSince);
};

const renderCharts = (profile) => {
    if (typeof Chart === 'undefined') {
        return;
    }

    const postsCommentsCanvas = document.getElementById('postsCommentsBarChart');
    const postsCount = profile.charts.postsComments.posts;
    const commentsCount = profile.charts.postsComments.comments;
    const hasPostsCommentsData = postsCount > 0 || commentsCount > 0;
    toggleChartPlaceholder('postsCommentsBarChart', 'placeholder-posts-comments', !hasPostsCommentsData);

    if (postsCommentsCanvas && hasPostsCommentsData) {
        new Chart(postsCommentsCanvas, {
            type: 'bar',
            data: {
                labels: ['Posts', 'Comments'],
                datasets: [
                    {
                        label: 'Count',
                        data: [postsCount, commentsCount],
                        backgroundColor: ['#2563eb', '#06b6d4'],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Activity Type',
                        },
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count',
                        },
                    },
                },
            },
        });
    }

    const totalBuyingCanvas = document.getElementById('totalBuyingLineChart');
    const totalBuyingLabels = profile.charts.totalBuyingByMonth.labels;
    const totalBuyingValues = profile.charts.totalBuyingByMonth.values;
    const hasTotalBuyingData = totalBuyingLabels.length > 0 && totalBuyingValues.some((value) => value > 0);
    toggleChartPlaceholder('totalBuyingLineChart', 'placeholder-total-buying', !hasTotalBuyingData);

    if (totalBuyingCanvas && hasTotalBuyingData) {
        new Chart(totalBuyingCanvas, {
            type: 'line',
            data: {
                labels: totalBuyingLabels,
                datasets: [
                    {
                        label: 'Total Buying',
                        data: totalBuyingValues,
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.12)',
                        fill: true,
                        tension: 0.35,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Month',
                        },
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Total Buying',
                        },
                    },
                },
            },
        });
    }

    const outcomeCanvas = document.getElementById('transactionOutcomePieChart');
    const successful = profile.user.stats.successfulTransactions;
    const failed = Math.max(profile.user.stats.totalTransactions - successful, 0);
    const hasOutcomeData = successful + failed > 0;
    toggleChartPlaceholder('transactionOutcomePieChart', 'placeholder-outcome', !hasOutcomeData);

    if (outcomeCanvas && hasOutcomeData) {
        new Chart(outcomeCanvas, {
            type: 'pie',
            data: {
                labels: ['Successful', 'Failed'],
                datasets: [
                    {
                        data: [successful, failed],
                        backgroundColor: ['#16a34a', '#ef4444'],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }
};

const initProfilePage = async ({ source = 'mock' } = {}) => {
    try {
        const rawData = source === 'api'
            ? await DataSources.fromApi()
            : await DataSources.fromMockFile();

        const profile = normalizeProfile(rawData);
        renderProfile(profile);
        renderCharts(profile);
    } catch (error) {
        console.error('Profile page init failed:', error);
    }
};

initProfilePage({ source: 'mock' });
setupPasswordVisibilityToggles();