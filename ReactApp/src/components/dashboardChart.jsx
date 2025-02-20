import React, { useEffect, useRef, useState } from 'react'
import Chart from 'chart.js/auto';
import { AiOutlinePlus } from "react-icons/ai";

const DashboardChart = ({refreshOnState, dateSpecify}) => {
  const defaultCategory = {categoryID:0,name:'No Categories',icon:' ',amount:'-$0.01', colour:'#6062647a', isDefault:1, isHidden:0, isIncome:false}
  const chartRef = useRef(null);
  const [categoryData, setCategoryData] = useState([])
  const hiddenLabels = useRef([])
  const [error, setError] = useState(<></>)
  const chartInstance = useRef(null);
  const incomeButtonRef = useRef(null);
  const categoriesButtonRef = useRef(null);
  const categoryDataRef = useRef([])
  const defaultInitialised = useRef(false)

  useEffect(() => {
    categoryDataRef.current = categoryData
  },[categoryData])

  useEffect(() => {
    defaultInitialised.current = false
  async function getCategoryData() {
    
    try {
      const response = await fetch(`/api/categories/advanced${dateSpecify ? `/${dateSpecify}` : ''}`, {method: 'GET'});
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        
        if (!data.data.length) {
          setCategoryData([defaultCategory])
        } else setCategoryData(data.data.filter((e) => Number(e.amount.replace('$','')) && e.isHidden===0))
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
},[refreshOnState, dateSpecify])


  useEffect(() => {

    const data = categoryData.map((e) => Number(e.amount.replace('$','')))
    const spendingData = data.map((e) => e<0 ? e : 0)
    const labels = categoryData.map((e) => [e.name, e.icon])
    const backgroundColors = categoryData.map((e) => e.colour)
    const ctx = chartRef.current.getContext('2d');

    if (!chartInstance.current) {

      chartInstance.current = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: labels[0],
          datasets: [
            { 
              label: 'Spending',
              data: spendingData,
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
              display: false,
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
                  const icon = tooltipItem.label[1] || '⚪'; 
                  return `${tooltipItem.label[0]} ${icon}`;
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
      chartInstance.current.data.labels = labels;
      chartInstance.current.data.datasets[0].data = spendingData;
      chartInstance.current.data.datasets[1].data = data;
      chartInstance.current.data.datasets[0].backgroundColor = [...backgroundColors];
      chartInstance.current.data.datasets[1].backgroundColor = categoryData.map((e) => e.isIncome ? '#44b60f' : e.colour)
      chartInstance.current.options.animation = {
        duration: 1000, // Short animation for update
      };
      chartInstance.current.update();
    }

    const customLegendContainer = document.getElementById('custom-legend');

    

    customLegendContainer.innerHTML = legendCallback(chartInstance.current);

  }, [categoryData]);

  function strikethroughLegend(labelIndex, addStrike) {
    
    const legendElements = document.querySelectorAll('.legend-item');
    const element = legendElements[labelIndex]
    element.children[0].style.textDecoration = ''

    element.style.textDecoration = addStrike ? 'line-through' : ''
  }


  function legendCallback(chart) {
    if (!chart.data.labels) return null
    const legendItems = chart.data.labels.map((label, index) => {
      const color = chart.data.datasets[0].backgroundColor[index];
      const isHidden = hiddenLabels.current.includes(index);
      return `
        <div class="legend-item" key=${index}>
          <span class="legend-label" style="text-decoration:${isHidden ?  'line-through' : '' /*Inital load*/ };">${label[1]}${label[0]}</span>
          <span class="legend-icon" style="background-color: ${color};"></span>
        </div>`;
    });

    setTimeout(() => {
    const legendElements = document.querySelectorAll('.legend-item');
    legendElements.forEach((item) => {
        const index = parseInt(item.getAttribute('key'), 10);
        item.addEventListener('click', () => toggleLabelVisibility(chart, index));
      });
    }, 0);

  
    return legendItems.join('');
  }

  const toggleDatasetVisibility = (chart, datasetIndex) => {
    if (!chart) return;
    const meta = chart.getDatasetMeta(datasetIndex);
    meta.hidden = !meta.hidden;
    chart.update();
  };


const toggleLabelVisibility = (chart, labelIndex, forceOff=null) => {
  if (!chart) return;
  // Toggle the visibility of the label
  if (hiddenLabels.current.includes(labelIndex) && !forceOff) {
    hiddenLabels.current = hiddenLabels.current.filter((i) => i !== labelIndex);
    strikethroughLegend(labelIndex, false);
  } else if (forceOff === null || forceOff) {
    if (!hiddenLabels.current.includes(labelIndex)) {
      hiddenLabels.current.push(labelIndex);
      strikethroughLegend(labelIndex, true);
    }
  }
  

  // Update the chart to reflect hidden labels
  chart.data.labels.forEach((label, i) => {
    const meta = chart.getDatasetMeta(0);
    const meta1 = chart.getDatasetMeta(1);
    meta.data[i].hidden = hiddenLabels.current.includes(i);
    meta1.data[i].hidden = hiddenLabels.current.includes(i);
  });

  // Update the chart to reflect the changes
  
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

  const animateSpending = async (chart) => {
    if (!chart) return;

  const datasetMeta = chart.getDatasetMeta(0);
  datasetMeta.data.forEach((meta, index) => {
    toggleLabelVisibility(chart, index, true)
  });
  datasetMeta.hidden = false;

  const meta = chart.getDatasetMeta(1);
  meta.hidden = true;
  chart.update();

  for (let i = 0; i < chart.data.labels.length; i++) {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    toggleLabelVisibility(chart, i, false)
    chart.tooltip.setActiveElements(
        [{ datasetIndex: 0, index: i }]
      );
    chart.update();
  }
  }

  useEffect(() => {
    if (categoryData.length && !defaultInitialised.current) {
      if (!categoryData[0].categoryID) return
      categoryData.forEach((e, index) => {
        if (e.isDefault === 0) {
          toggleLabelVisibility(chartInstance.current, index, true);
        }
      });
      defaultInitialised.current = true;
    }
  }, [categoryData]);

  return (
    <>
    {error}
      <div id="custom-legend"></div>
      <canvas id="dashboard-chart-main" ref={chartRef}></canvas>
      <div className='chart-actions'>
        <button id="toggleIncome" ref={incomeButtonRef} className='chart-action'>Toggle Income</button>
        <button id="toggleCategories" ref={categoriesButtonRef} className='chart-action'>Toggle Spending</button>
        <button id="toggleCategories" className='chart-action' onClick={() => animateSpending(chartInstance.current)}>Animate Spending</button>
      </div>
    </>
)};

export default DashboardChart