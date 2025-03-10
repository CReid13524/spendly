import React, { useEffect, useRef, useState } from "react";
import TransactionCarousel from "./transactionCarousel";


function DashboardCarousel({headerToggle, onChange, dateSpecify}) {
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
      const response = await fetch(`/api/record_data${dateSpecify ? '_filter' : ''}/0${dateSpecify ? `/${dateSpecify}` : ''}`, {method: 'GET'});
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        setCardData(data.data)
        if (data.data.length === 0) {
          setLimitText(dateSpecify ? 'No more records to display' : <div>Get started by adding transactions in <a href="/settings">settings</a>!</div>)
        }
      }
    } catch (error) {
      handleError(error)
    }
  }

  useEffect(() => {
    getTransactionData()
  },[dateSpecify])

  async function fetchExcess(isFetching, dateSpecify) {
    try {
      
      const response = await fetch(`/api/record_data${dateSpecify ? '_filter' : ''}/${cardDataRef.current.length}${dateSpecify ? `/${dateSpecify}` : ''}`, {method: 'GET'});
      
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
    <TransactionCarousel cardDataParam={cardData} fetchExcess={fetchExcess} onModalClose={onChange} headerToggle={headerToggle} limitText={limitText} handleError={handleError} dateSpecifyParam={dateSpecify}/>
    </>
  );

};

export default DashboardCarousel;
