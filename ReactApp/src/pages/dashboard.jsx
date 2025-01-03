import React from 'react'
import DashboardChart from '../components/dashboardChart'
import CardCarousel from '../components/cardCarousel'
import PageHeader from '../components/pageHeader'

function dashboard() {
  return (
    <div id='dashboard-container'>
      <div id='portal'></div>
      <div id='dashboard-page'>
        <PageHeader/>
        <DashboardChart/>
        <CardCarousel/>
      </div>
    </div>
  )
}

export default dashboard