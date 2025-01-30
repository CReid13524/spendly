import React, { useState } from 'react'
import PageHeader from '../components/pageHeader'
import UploadCSV from '../components/uploadCSV'

function settings() {
  
  return (
    <div id='settings-container'>
      <div id='settings-page'>
        <PageHeader/>
        <div id="page-title">Settings</div>
        <div id="page-section">Transaction Data</div>
        <UploadCSV/>
      </div>
    </div>

  )
}

export default settings