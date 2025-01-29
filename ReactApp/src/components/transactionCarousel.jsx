import React, { useEffect, useRef, useState } from 'react'
import "./transactionCarousel.css";
import TransactionCard from "./transactionCard";

function TransactionCarousel({cardDataParam, fetchExcess, onModalClose=() => {}, headerToggle=() => {}, limitText, handleError, staticColor=null, onCategoryUpdate=() => {}, dateSpecifyParam=null}) {
  const [cardData, setCardData] = useState([])
  const isFetching = useRef(false);
  const containerRef = useRef(null);
  const [selectedCardID, setSelectedCardID] = useState(null)
  const [categoryData, setCategoryData] = useState([])
  const dateSpecify = useRef(dateSpecifyParam)
  const cardDataRef = useRef(cardData);

    useEffect(() => {
      cardDataRef.current = cardData;
    }, [cardData]);
    
    useEffect(() => {
      setCardData(cardDataParam);
    }, [cardDataParam]);
    

    useEffect(() => {
      dateSpecify.current = dateSpecifyParam
      containerRef.current.scrollTop = 0
    }, [dateSpecifyParam]);

    useEffect(() => {
        const container = containerRef.current;
    
        if (container) {
          const handleScroll = () => {
            if (container.scrollTop + container.clientHeight >= container.scrollHeight - 5 && !isFetching.current) {
              isFetching.current = true
              if (fetchExcess(isFetching, dateSpecify.current)) {
                container.removeEventListener('scroll', handleScroll);
              }
            }
          };
          container.addEventListener('scroll', handleScroll);
        }
      }, []);

      async function handleDelete(transactionID) {
        try {
          const response = await fetch('/api/record_data', {
            method: 'DELETE',
            headers:  {'Content-Type' : 'application/json'},
            body: JSON.stringify({"transactionID":transactionID})
          });
          const data = await response.json();
          if (!response.ok) {
              throw data.error
          } else {        
            setCardData((prevTransactions) => {
              const index = prevTransactions.findIndex(
                (item) => item.transactionID === transactionID
              );
              const updatedTransactions = [...prevTransactions]
              updatedTransactions.splice(index, 1);
              return updatedTransactions;
            });
    
          }
        } catch (error) {
          handleError(error)
      }
    }

    async function getCategoryData() {
      try {
        const response = await fetch('/api/categories', {method: 'GET'});
        const data = await response.json();
        if (!response.ok) {
            throw data.error
        } else {
          setCategoryData(data.data)
        }
      } catch (error) {
        handleError(error)
      }
    }
  
    useEffect(() => {
      getCategoryData()
    },[])
    
      async function handleCategoryUpdate(transactionID, categoryID) {
        try {
          const response = await fetch('/api/record_data', {
            method: 'PUT',
            headers:  {'Content-Type' : 'application/json'},
            body: JSON.stringify({"transactionID":transactionID, "categoryID":categoryID})
          });
          const data = await response.json();
          if (!response.ok) {
              throw data.error
          } else {
            onCategoryUpdate(transactionID)
            const index = cardData.findIndex((card) => (card.transactionID === transactionID))
            cardData[index] = { ...cardData[index], categoryID: categoryID}
          }
        } catch (error) {
          handleError(error)
        }
      }
    
      function handleClick(e) {
        setSelectedCardID(e)
        headerToggle()
      }
    
      function handleModalClose() {
        setSelectedCardID(null)
        headerToggle()
          onModalClose()
      }
      
      return (
        <>
        <div id="transaction-carousel" ref={containerRef}>
        {cardData.map((card) => (
            card.transactionID === selectedCardID || selectedCardID === null ?
            <TransactionCard key={card.transactionID} data={card} onClick={handleClick} onClose={handleModalClose} handleDelete={() => handleDelete(card.transactionID)} handleCategoryUpdate={(e) => handleCategoryUpdate(card.transactionID, e)} categoryData={categoryData} staticColor={staticColor}/>
            : null
          ))}
          <div className="limit-reached-text">{limitText}</div>
        </div>
        </>
      );
    };

export default TransactionCarousel