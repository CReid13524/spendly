import React, { useEffect, useRef, useState } from 'react'
import TransactionCarousel from './transactionCarousel';
import TransactionCard from './transactionCard';
import Select from 'react-select'
import { IoChevronForwardCircle } from "react-icons/io5";
import { IoChevronBackCircle } from "react-icons/io5";


function QuickCategory({ headerToggle}) {
    const defaultSelectOption = {value:null, label:"No category", color:''}
    const [limitText, setLimitText] = useState('')
    const [isAuto, setIsAuto] = useState(false)
    const [cardData, setCardData] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [selectedOption, setSelectedOption] = useState(defaultSelectOption)
    const [selectedCardIndex, setSelectedCardIndex] = useState(0)
    const [categoryData, setCategoryData] = useState([])
    const cardDataRef = useRef(cardData);
    

    async function getTransactionData() {
        
        try {
          const response = await fetch(`/api/record_data/0/null`, {method: 'GET'});
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
        getCategoryData()
        getTransactionData()
    }, [])

    useEffect(() => {
          cardDataRef.current = cardData;
        }, [cardData]);

    async function handleCategorySelect(e) {
            setSelectedOption(e)
            setIsLoading(true)
            await handleCategoryUpdate(cardData[selectedCardIndex].transactionID, e.value,)
            setIsLoading(false)
        }

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
                cardData[selectedCardIndex] = { ...cardData[selectedCardIndex], categoryID: categoryID}
                if (isAuto) {
                    if (selectedCardIndex !== cardData.length-1) setSelectedCardIndex((e) => e+1)
                }
              }
            } catch (error) {
              handleError(error)
            }
          }
    
        function handleDeleteClose() {
            onClose()
            handleDelete()  
        }
    
       
        const selectOptions = [defaultSelectOption,...categoryData.map((e) => (
            {value:e.categoryID, label:`${e.icon ? e.icon : '⚪'} ${e.name}`, color:e.colour}
        ))]
    

    
        const customStyles = {
            option: (provided, state) => ({
              ...provided,
              backgroundColor:
                (state.isFocused || state.isSelected)// Apply styles only if the option has a value
                  ? (state.value ? state.data.color : '#d2d2d2')
                  : "white",
              color:
                (state.isFocused || state.isSelected) && state.data.value
                  ? "white"
                  : state.data.color,
              cursor: "pointer",
              ":active": {
                backgroundColor: state.data.value ? state.data.color : "white",
                color: state.data.value ? "white" : "inherit",
              },
            }),
            singleValue: (provided, state) => ({
              ...provided,
              color: state.data.color, // Color of the selected option
            }),
          };

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
          

  return (<div id='quick-category-select'>
            <TransactionCard data={cardData[selectedCardIndex]} onClick={headerToggle} onClose={headerToggle} categoryData={categoryData} staticColor={selectedOption.value ? '' : '#ffffff'}/>
            {limitText}
            <div id='quick-select-buttons'>
                <button onClick={() => setIsAuto((e) => !e)} style={{color: isAuto ? '#3080d0af' : ''}}>Auto</button>
                <div id='change-select-buttons'>
                    <IoChevronBackCircle onClick={() => {if (selectedCardIndex !== 0) setSelectedCardIndex((e) => e-1)}}/>
                    <IoChevronForwardCircle onClick={() => {if (selectedCardIndex !== cardData.length-1) setSelectedCardIndex((e) => e+1)}}/>
                </div>
            </div>
            <Select options={selectOptions} closeMenuOnSelect noOptionsMessage={"Go to 'Categories' page to make some new Categories!"}
                placeholder="Select a category for this transaction" styles={customStyles} value={selectedOption} onChange={handleCategorySelect}
                isLoading={isLoading} isDisabled={isLoading} menuIsOpen={Boolean(cardData) && Boolean(cardData.length)}
                components={{ DropdownIndicator: () => null }}
                />
        </div>
  )
}

export default QuickCategory