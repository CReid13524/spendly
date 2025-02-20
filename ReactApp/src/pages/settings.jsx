import React, { useState } from 'react'
import PageHeader from '../components/pageHeader'
import UploadCSV from '../components/uploadCSV'
import DeleteCSV from '../components/deleteCSV'
import EditSettings from '../components/editSettings'

function settings() {
  const [helpTextCSV, setHelpTextCSV] = useState(false)
  const [helpTextDelete, setHelpTextDelete] = useState(false)
  
  return (
    <div id='settings-container'>
      <div id='settings-page'>
        <PageHeader/>
        <div id="page-title">Settings</div>
        <div id="page-section">Transaction Data</div>
        <div id="section-info">Upload CSV  <button onClick={() => setHelpTextCSV((e) => !e)}>Help</button>
        </div>
        {helpTextCSV ? <ol>
          <li>Select your bank</li>
          <li>Follow popup and login to internet banking</li>
          <li>Download the required CSV</li>
          <li>Select CSV as upload file, and press <strong>Upload File</strong> to import your CSV!</li>
        </ol> : null }
        <UploadCSV/>
        <div id="section-info">Delete CSV Data  <button onClick={() => setHelpTextDelete((e) => !e)}>Help</button></div>
        {helpTextDelete ? <ol>
          <li>Select an upload occurence using <em>time</em> and <em>transaction counts</em> to assist your search</li>
          <li>Once deleted all transaction will be deleted</li>
          <li>Press <strong>Delete</strong> to preform deletion.</li>
        </ol> : null }
        <DeleteCSV/>
        <div id="page-section">User Data</div>
        <div id="section-info">Login</div>
        <EditSettings/>
      </div>
    </div>

  )
}

export default settings