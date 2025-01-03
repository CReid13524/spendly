import React, { useEffect, useRef, useState } from "react";
import "./CardCarousel.css";
import Card from "./card";

const VerticalScrollCarousel = () => {
  const [error, setError] = useState(<></>)
  const [cardData, setCardData] = useState([])
  const [selectedCardID, setSelectedCardID] = useState(null)
  const [limitText, setLimitText] = useState('')
  const containerRef = useRef(null);
  const cardDataRef = useRef(cardData);
  const isFetching = useRef(false);


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
    getTransactionData()
  },[])

  useEffect(() => {
    const container = containerRef.current;

    // Only proceed if the container is available
    if (container) {
      const handleScroll = () => {
        if (container.scrollTop + container.clientHeight >= container.scrollHeight - 5 && !isFetching.current) {
          isFetching.current = true
          async function fetchExcess() {
            try {
              const response = await fetch(`/api/record_data/${cardDataRef.current.length}`, {method: 'GET'});
              const data = await response.json();
              if (!response.ok) {
                  throw data.error
              } else {
                if (data.data.length === 0) {
                  setLimitText('No more records to display')
                } else {
                setCardData(prevData => [...prevData, ...data.data])}
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
              isFetching.current = false; // Reset fetching flag after completion
            }
          }
          fetchExcess()
        }
      };
      container.addEventListener('scroll', handleScroll);
    }
  }, []);

  useEffect(() => {
    cardDataRef.current = cardData;
  }, [cardData]);
  
  function handleClick(transactionID) {
    setSelectedCardID(transactionID)
  }

  function handleModalClose() {
    setSelectedCardID(null)
  }

  return (
    <>
    {error}
    <div id="vertical-scroll-carousel" ref={containerRef}>
    {cardData.map((card) => (
        card.transactionID === selectedCardID || selectedCardID === null ?
        <Card key={card.transactionID} data={card} onClick={handleClick} onClose={handleModalClose}/>
        : null
      ))}
      <div className="limit-reached-text">{limitText}</div>
    </div>
    </>
  );

};

export default VerticalScrollCarousel;
