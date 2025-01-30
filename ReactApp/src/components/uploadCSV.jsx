import React, { useState } from 'react'
import Select from 'react-select'

function UploadCSV() {
  const [file, setFile] = useState()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(<></>)
  const [selectedOption, setSelectedOption] = useState(null)

  async function handleUpload(event) {
    event.preventDefault()
    if (!selectedOption) {
      console.log(event)
    }
    setIsLoading(true)
    const formData = new FormData();
    formData.append('file', file);
    formData.append('data', JSON.stringify({ "bank": selectedOption.value }));

    try {
      const response = await fetch('/api/record_data', {
        method: 'POST',
        body: formData,
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
    } finally {
      setIsLoading(false)
    }
  }
  const options = [
    {value:'anz', label:'ANZ', color:"#007aff", image:"https://www.anz.co.nz/content/dam/anzconz/media/logo/logo-anz.svg"},
    {value:'kiwibank', label:'Kiwibank', color:"black", image:"https://www.ib.kiwibank.co.nz/images/logo.png"},

  ]

  const customStyles = {
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.data.color,
      color: 'white',
      cursor: "pointer",
      ":active": {
        backgroundColor: state.data.color,
      },
    }),
    singleValue: (provided, state) => ({
      ...provided,
      color: 'white',
    }),
    control: (provided, state) => ({
      ...provided,
      backgroundColor: state.hasValue ? state.getValue()[0]?.color : "white",
    }),
  };
  
  
  return (
    <div id='csv-upload'>
      {error}
      <form onSubmit={handleUpload}>
      <Select required options={options} closeMenuOnSelect placeholder="Select your bank" value={selectedOption} onChange={setSelectedOption}
          formatOptionLabel={e => (
            <div className='select-option'>
              <img className='select-image' src={e.image} alt="" />
              <span>{e.label}</span>
            </div>
          )} styles={customStyles} isLoading={isLoading} isDisabled={isLoading}/>
        <input type='file' accept='.csv' onChange={e => setFile(e.target.files[0])} required/>
        <button type='submit'>Upload File</button>
      </form>
    </div>
  )
}

export default UploadCSV