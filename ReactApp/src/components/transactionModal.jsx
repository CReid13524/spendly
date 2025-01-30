import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom';
import { MdOutlineArrowBack } from "react-icons/md";
import { LuCircleDashed } from "react-icons/lu";
import { MdDelete } from "react-icons/md";
import Select from 'react-select'

function TransactionModal({open, transactionData, onClose, handleDelete, handleCategoryUpdate, categoryData}) {
    const [isLoading, setIsLoading] = useState(false)
    const [selectedOption, setSelectedOption] = useState(null)
    if (open) {
    const [year, month, day] = transactionData.date.split('-'); // Split the input string
    const date = new Date(year, month - 1, day); // Create a Date object
    const options = { weekday: 'long', day: 'numeric', month: 'short' };
    var dateString = date.toLocaleDateString('en-US', options)}


    async function handleCategorySelect(e) {
        setSelectedOption(e)
        setIsLoading(true)
        await handleCategoryUpdate(e.value)
        setIsLoading(false)
    }

    function handleDeleteClose() {
        onClose()
        handleDelete()  
    }

    const defaultSelectOption = {value:null, label:"No category", color:''}
    const selectOptions = [defaultSelectOption,...categoryData.map((e) => (
        {value:e.categoryID, label:`${e.icon ? e.icon : '⚪'} ${e.name}`, color:e.colour}
    ))]

    useEffect(() => {
        if (transactionData?.categoryID) {
          const foundOption = selectOptions.find(
            (item) => item.value === transactionData.categoryID
          );
          setSelectedOption(foundOption || null); // Set to null if not found
        } else {
          setSelectedOption(null);
        }
      }, [transactionData]);

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
      

    return open ? ReactDOM.createPortal(
        <div className='transaction-modal-container'>
            <div className='transaction-modal'>
                <div style={{backgroundColor:selectedOption && selectedOption.value ? selectedOption.color+'99' : ''}} className='transaction-title'>
                    <div className='title-header'>
                        <div className='title-return'>
                            <MdOutlineArrowBack onClick={onClose}/>
                            {transactionData.title}
                        </div>
                        <MdDelete onClick={handleDeleteClose}/>
                    </div>
                    <div className='title-amount'>
                        {transactionData.amount}
                    </div>
                </div>
                <Select options={selectOptions} closeMenuOnSelect noOptionsMessage={"Go to 'Categories' page to make some new Categories!"}
                placeholder="Select a category for this transaction" styles={customStyles} value={selectedOption} onChange={handleCategorySelect}
                isLoading={isLoading} isDisabled={isLoading}
                />
                <div className='transaction-data'>
                    <div className='data-head'>
                        <div>{transactionData.details}</div>
                        <div>{dateString}</div>
                        <div><em>{transactionData.type}</em></div>
                    </div>
                    <div><strong>Particulars:</strong> {transactionData.particulars}</div>
                    <div><strong>Code:</strong> {transactionData.code}</div>
                    <div><strong>Reference:</strong> {transactionData.reference}</div>
                </div>
            </div>
        </div>
    , document.getElementById('transactionModalPortal')) : null
}

export default TransactionModal