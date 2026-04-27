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

// Hide/show password input and toggle button text on profile page
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

const DataSources = {
    async fromApi() {
        return await ajaxGetJson('/api/profile', 'Failed to load API profile data');
    },

    async fromChartMock() {
        return await ajaxGetJson('/static/mock_userdata.json', 'Failed to load mock chart data');
    },
};

// Sanitize input data
const normalizeProfile = (raw) => {
    const user = raw?.user || {};
    const stats = user.stats || {};

    return {
        user: {
            username: user.username || 'Invalid User',
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
    };
};

const normalizeChartData = (raw) => {
    const charts = raw?.charts || {};

    return {
        totalBuyingByMonth: {
            labels: charts.totalBuyingByMonth?.labels || [],
            values: charts.totalBuyingByMonth?.values || [],
        },
        postsComments: {
            posts: charts.postsComments?.posts || 0,
            comments: charts.postsComments?.comments || 0,
        },
        transactionOutcome: {
            successful: charts.transactionOutcome?.successful ?? 0,
            failed: charts.transactionOutcome?.failed ?? 0,
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

const resizeCanvas = (canvas, width, height) => {
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.max(width * ratio, 1);
    canvas.height = Math.max(height * ratio, 1);
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    const context = canvas.getContext('2d');
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    return context;
};

const drawBarFallback = (canvas, labels, values) => {
    const width = canvas.parentElement?.clientWidth || 400;
    const height = canvas.parentElement?.clientHeight || 240;
    const context = resizeCanvas(canvas, width, height);

    context.clearRect(0, 0, width, height);
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, width, height);

    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const maxValue = Math.max(...values, 1);
    const barWidth = chartWidth / labels.length * 0.55;
    const gap = chartWidth / labels.length;

    context.strokeStyle = '#cbd5e1';
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(padding, padding);
    context.lineTo(padding, padding + chartHeight);
    context.lineTo(padding + chartWidth, padding + chartHeight);
    context.stroke();

    labels.forEach((label, index) => {
        const value = values[index];
        const barHeight = (value / maxValue) * (chartHeight - 20);
        const x = padding + gap * index + (gap - barWidth) / 2;
        const y = padding + chartHeight - barHeight;

        context.fillStyle = index === 0 ? '#2563eb' : '#06b6d4';
        context.fillRect(x, y, barWidth, barHeight);

        context.fillStyle = '#475569';
        context.font = '12px sans-serif';
        context.textAlign = 'center';
        context.fillText(label, x + barWidth / 2, padding + chartHeight + 16);
        context.fillText(String(value), x + barWidth / 2, y - 6);
    });
};

const drawLineFallback = (canvas, labels, values) => {
    const width = canvas.parentElement?.clientWidth || 400;
    const height = canvas.parentElement?.clientHeight || 240;
    const context = resizeCanvas(canvas, width, height);

    context.clearRect(0, 0, width, height);
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, width, height);

    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    const maxValue = Math.max(...values, 1);
    const stepX = labels.length > 1 ? chartWidth / (labels.length - 1) : 0;

    context.strokeStyle = '#cbd5e1';
    context.beginPath();
    context.moveTo(padding, padding);
    context.lineTo(padding, padding + chartHeight);
    context.lineTo(padding + chartWidth, padding + chartHeight);
    context.stroke();

    context.strokeStyle = '#2563eb';
    context.fillStyle = 'rgba(37, 99, 235, 0.12)';
    context.lineWidth = 3;
    context.beginPath();

    values.forEach((value, index) => {
        const x = padding + stepX * index;
        const y = padding + chartHeight - (value / maxValue) * (chartHeight - 20);

        if (index === 0) {
            context.moveTo(x, y);
        } else {
            context.lineTo(x, y);
        }
    });

    context.stroke();

    values.forEach((value, index) => {
        const x = padding + stepX * index;
        const y = padding + chartHeight - (value / maxValue) * (chartHeight - 20);

        context.beginPath();
        context.arc(x, y, 4, 0, Math.PI * 2);
        context.fill();

        context.fillStyle = '#475569';
        context.font = '12px sans-serif';
        context.textAlign = 'center';
        context.fillText(labels[index], x, padding + chartHeight + 16);
    });
};

const drawPieFallback = (canvas, labels, values) => {
    const width = canvas.parentElement?.clientWidth || 400;
    const height = canvas.parentElement?.clientHeight || 240;
    const context = resizeCanvas(canvas, width, height);
    const total = values.reduce((sum, value) => sum + value, 0) || 1;
    const centerX = width / 2;
    const centerY = height / 2 - 10;
    const radius = Math.min(width, height) * 0.28;
    const colors = ['#16a34a', '#ef4444'];

    context.clearRect(0, 0, width, height);
    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, width, height);

    let startAngle = -Math.PI / 2;
    values.forEach((value, index) => {
        const sliceAngle = (value / total) * Math.PI * 2;
        const endAngle = startAngle + sliceAngle;

        context.beginPath();
        context.moveTo(centerX, centerY);
        context.arc(centerX, centerY, radius, startAngle, endAngle);
        context.closePath();
        context.fillStyle = colors[index % colors.length];
        context.fill();

        startAngle = endAngle;
    });

    context.font = '12px sans-serif';
    context.fillStyle = '#475569';
    context.textAlign = 'center';
    context.fillText(`${labels[0]}: ${values[0]}`, centerX, height - 34);
    context.fillText(`${labels[1]}: ${values[1]}`, centerX, height - 18);
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
    const postsCommentsCanvas = document.getElementById('postsCommentsBarChart');
    const postsCount = profile.charts.postsComments.posts;
    const commentsCount = profile.charts.postsComments.comments;
    const hasPostsCommentsData = postsCount > 0 || commentsCount > 0;
    toggleChartPlaceholder('postsCommentsBarChart', 'placeholder-posts-comments', !hasPostsCommentsData);

    if (postsCommentsCanvas && hasPostsCommentsData) {
        if (typeof Chart !== 'undefined') {
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
        } else {
            drawBarFallback(postsCommentsCanvas, ['Posts', 'Comments'], [postsCount, commentsCount]);
        }
    }

    const totalBuyingCanvas = document.getElementById('totalBuyingLineChart');
    const totalBuyingLabels = profile.charts.totalBuyingByMonth.labels;
    const totalBuyingValues = profile.charts.totalBuyingByMonth.values;
    const hasTotalBuyingData = totalBuyingLabels.length > 0 && totalBuyingValues.some((value) => value > 0);
    toggleChartPlaceholder('totalBuyingLineChart', 'placeholder-total-buying', !hasTotalBuyingData);

    if (totalBuyingCanvas && hasTotalBuyingData) {
        if (typeof Chart !== 'undefined') {
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
        } else {
            drawLineFallback(totalBuyingCanvas, totalBuyingLabels, totalBuyingValues);
        }
    }

    const outcomeCanvas = document.getElementById('transactionOutcomePieChart');
    const successful = profile.charts.transactionOutcome?.successful ?? profile.user.stats.successfulTransactions;
    const failed = profile.charts.transactionOutcome?.failed ?? Math.max(profile.user.stats.totalTransactions - successful, 0);
    const hasOutcomeData = successful + failed > 0;
    toggleChartPlaceholder('transactionOutcomePieChart', 'placeholder-outcome', !hasOutcomeData);

    if (outcomeCanvas && hasOutcomeData) {
        if (typeof Chart !== 'undefined') {
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
        } else {
            drawPieFallback(outcomeCanvas, ['Successful', 'Failed'], [successful, failed]);
        }
    }
};

const initProfilePage = async () => {
    let profile = normalizeProfile({});

    try {
        const profileRawData = await DataSources.fromApi();
        profile = normalizeProfile(profileRawData);
        renderProfile(profile);
    } catch (error) {
        console.error('Profile data load failed:', error);
    }

    try {
        const chartRawData = await DataSources.fromChartMock();
        profile.charts = normalizeChartData(chartRawData);
        renderCharts(profile);
    } catch (error) {
        console.error('Chart data load failed:', error);
    }
};

initProfilePage();
setupPasswordVisibilityToggles();