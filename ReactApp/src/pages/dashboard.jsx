import React, { useState } from 'react'
import DashboardChart from '../components/dashboardChart'
import DashboardCarousel from '../components/dashboardCarousel'
import PageHeader from '../components/pageHeader'
import { IoChevronForwardCircle } from "react-icons/io5";
import { IoChevronBackCircle } from "react-icons/io5";

function dashboard() {
  const [headerEnabled, setHeaderEnabled] = useState(true)
  const [refreshOnState, setRefreshOnState] = useState(false)
  const [dateSpecify, setDateSpecify] = useState('')

  function test() {
    setHeaderEnabled(!headerEnabled)
  }

  async function onCarouselChange() {
    await new Promise(resolve => setTimeout(resolve, 100));
    setRefreshOnState(!refreshOnState)
  }

  function changeMonth(isPrev) {
    let [year, month] = dateSpecify.split('-').map(Number);
    const now = new Date();
    const year_now = now.getFullYear();
    const month_now = now.getMonth() + 1;

    if (!dateSpecify && isPrev) {
      year = year_now
      month = month_now
      
    } else if (year_now <= year && month_now <= month && !isPrev || !dateSpecify && !isPrev) {
      setDateSpecify('')
      return
    } else if (isPrev) {
        month -= 1;
        if (month === 0) {

            month = 12;
            year -= 1;
        }
    } else {
        month += 1;
        if (month === 13) {
            month = 1;
            year += 1;
        }
    }

    // Format the updated date back to 'YYYY-MM' format
    setDateSpecify(`${year}-${String(month).padStart(2, '0')}`)
}


  return (
    <div id='dashboard-container'>
      <div id='transactionModalPortal'></div>
      <div id='dashboard-page'>
        {headerEnabled ? <PageHeader/> : <></>}
        <DashboardChart refreshOnState={refreshOnState} dateSpecify={dateSpecify}/>
        <div id='date-select'>
          <IoChevronBackCircle onClick={() => changeMonth(true)}/>
          {dateSpecify ? <input type='month' value={dateSpecify} placeholder='All Time' onChange={(e) => setDateSpecify(e.target.value)}/>
          : 'All Time'}
          <IoChevronForwardCircle onClick={() => changeMonth(false)}/>
        </div>
        <DashboardCarousel headerToggle={test} onChange={onCarouselChange} dateSpecify={dateSpecify}/>
      </div>
    </div>
  )
}

export default dashboard