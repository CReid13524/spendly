import React, { useState } from 'react'
import Select from 'react-select'
import { FaExternalLinkAlt } from "react-icons/fa";

function UploadCSV() {
  const [file, setFile] = useState()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(<></>)
  const [selectedOption, setSelectedOption] = useState(null)

  async function handleUpload(event) {
    event.preventDefault()
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
      } else (
        alert("CSV upload was successful")
      )
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
    {value:'anz', label:'ANZ', color:"#007aff", text:"Required Type: CSV", link:"https://digital.anz.co.nz/preauth/web/service/login", image:"https://www.anz.co.nz/content/dam/anzconz/media/logo/logo-anz.svg"},
    {value:'kiwibank', label:'Kiwibank', color:"black", text:"Required Type: Full CSV",link:"https://www.ib.kiwibank.co.nz/login", image:"https://media.kiwibank.co.nz/media/images/Kiwibank_logo_white_250x250.width-500.webp"},

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
              <img className='select-image' src={e.image} alt=""/>
              <span>{e.label}</span>
            </div>
          )} styles={customStyles} isLoading={isLoading} isDisabled={isLoading}/>
          <div id="csv-external">
          {selectedOption ? selectedOption.text : null}
          {selectedOption ? <a href={selectedOption.link} target="_blank" rel="noopener noreferrer"><FaExternalLinkAlt/></a> : null }
          </div>
        <input type='file' accept='.csv' onChange={e => setFile(e.target.files[0])} required/>
        <button type='submit'>Upload File</button>
      </form>
    </div>
  )
}

export default UploadCSV