import React, { useEffect, useRef, useState } from "react";
import TransactionCarousel from "./transactionCarousel";


function DashboardCarousel({headerToggle, onChange}) {
  const [error, setError] = useState(<></>)
  const [cardData, setCardData] = useState([])
  const [limitText, setLimitText] = useState('')


  const cardDataRef = useRef(cardData);

  function handleError(error) {
    setError(
      <div className='error-message'>
      <h1 className="error-head">The following error has occured:</h1>
      {String(error)}
      <button className="error-dismiss" onClick={() => setError(<></>)}>Dismiss</button>
      </div>
    );
  }

  async function getTransactionData() {
    
    try {
      const response = await fetch('/api/record_data', {method: 'GET'});
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        setCardData(data.data)
        if (data.data.length === 0) {
          setLimitText('No more records to display')
        }
      }
    } catch (error) {
      handleError(error)
    }
  }

  useEffect(() => {
    getTransactionData()
  },[])

  async function fetchExcess(isFetching) {
    try {
      const response = await fetch(`/api/record_data/${cardDataRef.current.length}`, {method: 'GET'});
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        if (data.data.length === 0) {
          setLimitText('No more records to display')
          return true
        } else {
        setCardData(prevData => [...prevData, ...data.data])}
      }
    } catch (error) {
      handleError(error)
    } finally {
      isFetching.current = false; // Reset fetching flag after completion
    }
  }

  useEffect(() => {
    cardDataRef.current = cardData;
  }, [cardData]);

  

  return (
    <>
    {error}
    <TransactionCarousel cardDataParam={cardData} fetchExcess={fetchExcess} onModalClose={onChange} headerToggle={headerToggle} limitText={limitText} handleError={handleError}/>
    </>
  );

};

export default DashboardCarousel;
