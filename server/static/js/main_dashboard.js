// 🟡 משתנה גלובלי לשמירה על גרפים פעילים
let existingCharts = {};

document.addEventListener('DOMContentLoaded', function () {
  // 🔹 תרשים עוגה – בקרת איכות
  const qualityLabels = window.qualityLabels;
  const qualityValues = window.qualityValues;

  const qualityCanvas = document.getElementById("qualityPie");
  if (existingCharts.qualityPie) {
    existingCharts.qualityPie.destroy();
  }
  existingCharts.qualityPie = new Chart(qualityCanvas, {
    type: 'pie',
    data: {
      labels: qualityLabels,
      datasets: [{
        data: qualityValues,
        backgroundColor: ['#dc3545', '#198754', '#ffc107', '#0dcaf0']
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: function (context) {
              const label = context.label || '';
              const value = context.parsed;
              const total = context.chart._metasets[0].total;
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        },
        datalabels: {
          color: '#000',
          font: { weight: 'bold' },
          formatter: (value, context) => {
            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${percentage}%`;
          }
        }
      }
    },
    plugins: [ChartDataLabels]
  });

  // 🔹 תרשים עמודות – ייצור לפי תאריכים
  const barLabels = window.barLabels;
  const barValues = window.barValues;

  const barCanvas = document.getElementById("productionBar");
  if (existingCharts.productionBar) {
    existingCharts.productionBar.destroy();
  }
  existingCharts.productionBar = new Chart(barCanvas, {
    type: 'bar',
    data: {
      labels: barLabels,
      datasets: [{
        label: 'תוכניות ייצור',
        data: barValues,
        backgroundColor: '#0d6efd'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function (context) {
              return `כמות: ${context.parsed.y}`;
            }
          }
        },
        datalabels: {
          anchor: 'end',
          align: 'top',
          color: '#000',
          font: { weight: 'bold' },
          formatter: (value) => value
        }
      }
    },
    plugins: [ChartDataLabels]
  });

  // 🔸 תרשים עוגה – התפלגות עדיפות
  fetch('/api/production/priority-distribution')
    .then(response => response.json())
    .then(data => {
      const ctx = document.getElementById('priorityPieChart').getContext('2d');

      if (existingCharts.priorityPieChart) {
        existingCharts.priorityPieChart.destroy();
      }

      existingCharts.priorityPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: Object.keys(data),
          datasets: [{
            label: 'עדיפות',
            data: Object.values(data),
            backgroundColor: ['#ffc107', '#dc3545', '#28a745']
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'bottom' },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || '';
                  const value = context.parsed;
                  const total = context.chart._metasets[0].total;
                  const percentage = ((value / total) * 100).toFixed(1);
                  return `${label}: ${value} (${percentage}%)`;
                }
              }
            },
            datalabels: {
              color: '#000',
              font: { weight: 'bold' },
              formatter: (value, context) => {
                const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return `${percentage}%`;
              }
            }
          }
        },
        plugins: [ChartDataLabels]
      });
    });
});
