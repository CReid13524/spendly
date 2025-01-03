import React, { useEffect, useRef } from 'react'
import Chart from 'chart.js/auto';

const DashboardChart = () => {
  const chartRef = useRef(null);

  //Example Data
  const data = [12, 19, 3, 5];
  const labels = ['Red', 'Blue', 'Yellow', 'Green'];
  const backgroundColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'];
  const borderColors = ['white'];

  useEffect(() => {
    const ctx = chartRef.current.getContext('2d');

    const doughnutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            data: data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 2,
            hoverOffset: 10
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            enabled: true,
          },
        },
        animation: {
          animateScale: true,
          animateRotate: true,
        },
        maintainAspectRatio: false,
      },
    });

    return () => {
      doughnutChart.destroy();
    };
  }, [data, labels, backgroundColors, borderColors]);

  return <canvas id="dashboard-chart-main" ref={chartRef}></canvas>;
};

export default DashboardChart