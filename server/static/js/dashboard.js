// קוד JS לקבלת משתנים מהשרת
const qualityLabels = window.dashboardData.quality_labels;
const qualityValues = window.dashboardData.quality_values;
const barLabels = window.dashboardData.bar_labels;
const barValues = window.dashboardData.bar_values;

// Pie Chart - Quality Distribution
const pieCtx = document.getElementById('qualityPie');
new Chart(pieCtx, {
    type: 'pie',
    data: {
        labels: qualityLabels,
        datasets: [{
            data: qualityValues,
            backgroundColor: ['#198754', '#dc3545', '#ffc107', '#0dcaf0']
        }]
    },
    options: {
        responsive: true
    }
});

// Bar Chart - Production by Date
const barCtx = document.getElementById('productionBar');
new Chart(barCtx, {
    type: 'bar',
    data: {
        labels: barLabels,
        datasets: [{
            label: 'תוכניות',
            data: barValues,
            backgroundColor: '#0d6efd'
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
