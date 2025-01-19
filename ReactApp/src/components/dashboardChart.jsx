import React, { useEffect, useRef, useState } from 'react'
import Chart from 'chart.js/auto';
import { AiOutlinePlus } from "react-icons/ai";

const DashboardChart = ({refreshOnState}) => {
  const chartRef = useRef(null);
  const [categoryData, setCategoryData] = useState([])
  const [error, setError] = useState(<></>)
  const chartInstance = useRef(null);
  const incomeButtonRef = useRef(null);
  const categoriesButtonRef = useRef(null);
  const categoryDataRef = useRef([])

  useEffect(() => {
    categoryDataRef.current = categoryData
  },[categoryData])

  useEffect(() => {
  async function getCategoryData() {
    
    try {
      const response = await fetch('/api/categories/advanced', {method: 'GET'});
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        console.log()
        setCategoryData(data.data.filter(e => e.amount.includes('-')))
      
      }
    } catch (error) {
      setError(
        <div className='error-message'>
        <h1 className="error-head">The following error has occured:</h1>
        {String(error)}
        <button className="error-dismiss" onClick={(e) => setError(<></>)}>Dismiss</button>
        </div>
      );
    }
  }
  getCategoryData()
},[refreshOnState])


  useEffect(() => {

    const data = categoryData.map((e) => Number(e.amount.split('$')[1]))
    const labels = categoryData.map((e) => e.name)
    const backgroundColors = categoryData.map((e) => e.colour)
    const ctx = chartRef.current.getContext('2d');

    if (!chartInstance.current) {

      chartInstance.current = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [
            { 
              label: 'Spending',
              data: data,
              backgroundColor: backgroundColors,
              borderColor: 'white',
              borderWidth: 2,
              hoverOffset: 10
            },
            { 
              label: 'Income',
              data: data,
              backgroundColor: categoryData.map((e) => e.isIncome ? '#44b60f' : e.colour),
              borderColor: 'white',
              borderWidth: 2,
              hoverOffset: 10,
            }
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {  
              callbacks: {
                label: function (tooltipItem) {
                  const dataPoint = categoryDataRef.current[tooltipItem.dataIndex];
                  const amount = dataPoint.amount;
                  return ` ${amount}`;
                },
                afterLabel: function (tooltipItem) {
                  const dataPoint = categoryDataRef.current[tooltipItem.dataIndex];
                  const isIncomeTag = dataPoint?.isIncome ? '(Income)' : '';
                  if (tooltipItem.datasetIndex === 1) {
                    return `${isIncomeTag}`;
                  }
                  return ''; // Return empty string if not in dataset 1
                },
                title: function (tooltipItems) {
                  const tooltipItem = tooltipItems[0]; 
                  const dataPoint = categoryDataRef.current[tooltipItem.dataIndex];
                  const icon = dataPoint?.icon || '⚪'; 
                  return `${tooltipItem.label} ${icon}`;
                },
              },
            },
          },
          animation: {
            animateScale: true,
            animateRotate: true,
          },
          maintainAspectRatio: false,
        },
      });
      
      toggleDatasetVisibility(chartInstance.current,1)
    } else {
      // Update the chart data
      chartInstance.current.data.labels = [...labels, 'Income'];
      chartInstance.current.data.datasets[0].data = data;
      chartInstance.current.data.datasets[1].data = data;
      chartInstance.current.data.datasets[0].backgroundColor = [...backgroundColors];
      chartInstance.current.data.datasets[1].backgroundColor = categoryData.map((e) => e.isIncome ? '#44b60f' : e.colour);
      chartInstance.current.options.animation = {
        duration: 1000, // Short animation for update
      };
      chartInstance.current.update();
    }
  }, [categoryData]);

  const toggleDatasetVisibility = (chart, datasetIndex) => {
    if (!chart) return;
    const meta = chart.getDatasetMeta(datasetIndex);
    meta.hidden = !meta.hidden;
    chart.update();
  };

  useEffect(() => {
    const incomeButton = incomeButtonRef.current;
    const categoriesButton = categoriesButtonRef.current;

    const handleIncomeToggle = () => toggleDatasetVisibility(chartInstance.current, 1);
    const handleCategoryToggle = () => toggleDatasetVisibility(chartInstance.current, 0);

    if (incomeButton) {
      incomeButton.addEventListener('click', handleIncomeToggle);
    }
    if (categoriesButton) {
      categoriesButton.addEventListener('click', handleCategoryToggle);
    }

    return () => {
      if (incomeButton) {
        incomeButton.removeEventListener('click', handleIncomeToggle);
      }
      if (categoriesButton) {
        categoriesButton.removeEventListener('click', handleCategoryToggle);
      }
    };
  }, [chartInstance]);

 

  return (
    <>
    {error}
      <canvas id="dashboard-chart-main" ref={chartRef}></canvas>
      <div className='chart-actions'>
        <button id="toggleIncome" ref={incomeButtonRef} className='chart-action'>Toggle Income</button>
        <button id="toggleCategories" ref={categoriesButtonRef} className='chart-action'>Toggle Categories</button>
      </div>
    </>
)};

export default DashboardChart