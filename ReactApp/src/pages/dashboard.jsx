import React, { useState } from 'react'
import DashboardChart from '../components/dashboardChart'
import DashboardCarousel from '../components/dashboardCarousel'
import PageHeader from '../components/pageHeader'

function dashboard() {
  const [headerEnabled, setHeaderEnabled] = useState(true)
  const [refreshOnState, setRefreshOnState] = useState(false)

  function test() {
    setHeaderEnabled(!headerEnabled)
  }

  async function onCarouselChange() {
    await new Promise(resolve => setTimeout(resolve, 100));
    setRefreshOnState(!refreshOnState)
  }

  return (
    <div id='dashboard-container'>
      <div id='transactionModalPortal'></div>
      <div id='dashboard-page'>
        {headerEnabled ? <PageHeader/> : <></>}
        <DashboardChart refreshOnState={refreshOnState}/>
        <DashboardCarousel headerToggle={test} onChange={onCarouselChange}/>
      </div>
    </div>
  )
}

export default dashboard