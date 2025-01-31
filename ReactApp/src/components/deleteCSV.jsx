import React, { useEffect, useState } from 'react'
import Select from 'react-select'

function DeleteCSV() {
  const [isLoading, setIsLoading] = useState(false)
  const [uploadData, setUploadData] = useState([])
  const [error, setError] = useState(<></>)
  const [selectedOption, setSelectedOption] = useState(null)

  async function handleDelete(event) {
    event.preventDefault()
    setIsLoading(true)
    if (!window.confirm(`Are you sure you want to delete Upload: ${selectedOption.label}?`)) {
      return
    }
    try {
      const response = await fetch('/api/record_data_mass_delete', {
        method: 'DELETE',
        headers:  {'Content-Type' : 'application/json'},
        body: JSON.stringify({uploadID:selectedOption.value})
      });

      const data = await response.json();
      if (!response.ok) {
        throw data.error
      } else {
        setUploadData((prev) => prev.filter((e) => e.uploadID !== selectedOption.value));
        setSelectedOption(null)
      }
    } catch (error) {
      setError(
        <div className='error-message'>
            <h1 className="error-head">The following error has occured:</h1>
            {String(error)}
            <button className="error-dismiss" onClick={(e) => setError(<></>)}>Dismiss</button>
        </div>
    );
    } finally {
      setIsLoading(false)
    }
  }

  async function getUploadData() {
    try {
      const response = await fetch('/api/record_data_mass_delete', {
        method: 'GET',
      });

      const data = await response.json();
      if (!response.ok) {
        throw data.error
      } else {
        setUploadData(data.data)
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

  useEffect(() => {
    getUploadData()
  },[])

  const options = uploadData.map((e) => (
      {label:`#${e.uploadID} | Uploaded on: ${e.date}, Transaction count: ${e.count}`, value:e.uploadID }
    ))
  
  
  return (
    <div id='csv-delete'>
      {error}
      <form onSubmit={handleDelete}>
      <Select required options={options} closeMenuOnSelect placeholder="Select upload for deletion" value={selectedOption} onChange={setSelectedOption}
        isLoading={isLoading} isDisabled={isLoading}/>
        <button type='submit'>Delete</button>
      </form>
    </div>
  )
}

export default DeleteCSV