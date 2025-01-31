import React, { useState } from 'react'
import PageHeader from '../components/pageHeader'
import UploadCSV from '../components/uploadCSV'
import DeleteCSV from '../components/deleteCSV'

function settings() {
  
  return (
    <div id='settings-container'>
      <div id='settings-page'>
        <PageHeader/>
        <div id="page-title">Settings</div>
        <div id="page-section">Transaction Data</div>
        <div id="section-info">Upload CSV</div>
        <UploadCSV/>
        <div id="section-info">Delete CSV Data</div>
        <DeleteCSV/>
        <div id="page-section">User Data</div>
        <div id="section-info">Upload CSV</div>
      </div>
    </div>

  )
}

export default settings