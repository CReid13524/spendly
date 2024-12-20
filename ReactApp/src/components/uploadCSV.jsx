import React, { useState } from 'react'

function UploadCSV() {
  const [file, setFile] = useState()
  const [error, setError] = useState(<></>)

  async function handleUpload(event) {
    event.preventDefault()
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/record_data', {
        method: 'POST',
        body: formData, // FormData object is passed as the body
      });

      const data = await response.json();
      if (!response.ok) {
        throw data.error
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
  
  return (
    <>
      {error}
      <form onSubmit={handleUpload}>
        <input type='file' accept='.csv' onChange={e => setFile(e.target.files[0])} required/>
        <button type='submit'>Upload File</button>
      </form>
    </>

  )
}

export default UploadCSV