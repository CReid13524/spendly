import React, { useEffect, useRef, useState } from 'react'
import ReactDOM from 'react-dom';
import { MdOutlineArrowBack } from "react-icons/md";
import { LuCircleDashed } from "react-icons/lu";
import TransactionCarousel from './transactionCarousel';
import { AiFillEdit } from "react-icons/ai";
import { AiOutlineEdit } from "react-icons/ai";
import EmojiPickerModal from './emojiPickerModal';
import { MdDelete } from "react-icons/md";

function CategoryModal({open, categoryData, onClose, handleError, onUpdate}) {
    const [cardData, setCardData] = useState([])
    const [categoryUpdatePending, setCategoryUpdatePending] = useState(null)
    const [editActive, setEditActive] = useState(false)
    const [selectColor, setSelectColor] = useState(categoryData.colour)
    const [selectIncome, setSelectIncome] = useState(categoryData.isIncome)
    const [selectName, setSelectName] = useState(categoryData.name)
    const [selectIcon, setSelectIcon] = useState(categoryData.icon)
    const [emojiModalOpen, setEmojiModalOpen] = useState(false)
    const [limitText, setLimitText] = useState('')
    const cardDataRef = useRef(cardData);
    const inputRef = useRef(null);
    
    async function getTransactionData() {
        
        try {
          const response = await fetch(`/api/record_data/0/${categoryData.categoryID}`, {method: 'GET'});
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
    
        useEffect(() => {
          cardDataRef.current = cardData;
        }, [cardData]);
      
      async function fetchExcess(isFetching) {
        try {
          const response = await fetch(`/api/record_data/${cardDataRef.current.length}/${categoryData.categoryID}`, {method: 'GET'});
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
        if (editActive && inputRef.current) {
          inputRef.current.focus();
        }
      }, [editActive]);


      async function handleUpdate(isIncome=selectIncome) {
        try {
          const response = await fetch('/api/categories', {
            method: 'PUT',
            headers:  {'Content-Type' : 'application/json'},
            body: JSON.stringify({"categoryID":categoryData.categoryID, 'color':selectColor, 'name':selectName, 'icon':selectIcon, 'isIncome': isIncome ? 1 : 0})
          });
          const data = await response.json();
          if (!response.ok) {
              throw data.error
          } else {
            onUpdate()
          }
        } catch (error) {
          handleError(error)
        }
      }

      const handleToggleEmojiPicker = (e) => {
        e.stopPropagation(); 
        setEmojiModalOpen((prev) => !prev);
      };
      const handleEmojiPickerClose = (e) => {
        handleToggleEmojiPicker(e)
        handleUpdate()
      };

    function handleTransactionModalClose() {
      if (categoryUpdatePending) {
        onUpdate()
        setCardData((prevTransactions) => {
          const index = prevTransactions.findIndex(
            (item) => item.transactionID === categoryUpdatePending
          );
          const updatedTransactions = [...prevTransactions]
          updatedTransactions.splice(index, 1);
          return updatedTransactions;
        })
        setCategoryUpdatePending(null)
      }
    }

    async function handleDelete() {
      if (window.confirm(`Are you sure? ${categoryData.name} (ID: ${categoryData.categoryID}) will be deleted forever.
All existing transaction will be unset.`))
      try {
        const response = await fetch('/api/categories', {
          method: 'DELETE',
          headers:  {'Content-Type' : 'application/json'},
          body: JSON.stringify({"categoryID":categoryData.categoryID})
        });
        const data = await response.json();
        if (!response.ok) {
            throw data.error
        } else {        
            onUpdate()
        }
      } catch (error) {
        handleError(error)
    }
  }

  function handleIsIncome(e) {
    e.stopPropagation()
    handleUpdate(!selectIncome)
    setSelectIncome((e) => !e)
    
  }

    if (!open) return null
    return ReactDOM.createPortal(
        <div className='category-modal-container'>
          <EmojiPickerModal open={emojiModalOpen} onSelect={e => setSelectIcon(e)} onClose={handleEmojiPickerClose}/>
            <div className='category-modal'>
                <div className='category-title' style={{backgroundColor:selectColor+'99'}}>
                    <div className='title-header'>
                        <div className='title-return'>
                            <MdOutlineArrowBack onClick={onClose}/>
                            <input disabled={!editActive} value={selectName} onChange={(e) => setSelectName(e.target.value)} ref={inputRef} onBlur={handleUpdate}/>
                        </div>
                        <div className='header-align-right'>
                          {editActive ? <AiOutlineEdit onClick={() => setEditActive(!editActive)}/> : <AiFillEdit onClick={() => setEditActive(!editActive)}/>}
                          { editActive ? <div style={{backgroundColor:selectColor}} className="color-select">
                            <input type='color' value={selectColor} onChange={e => setSelectColor(e.target.value)} onBlur={handleUpdate}/>
                          </div> : null }
                          {editActive ? <MdDelete onClick={handleDelete}/> : null}
                          <div className='category-icon' onClick={handleToggleEmojiPicker}>
                            {selectIcon ?  selectIcon : <LuCircleDashed />}
                          </div>
                        </div>
                        
                    </div>
                    {editActive ? <div className='income-check'>Income
                      <input type='checkbox' checked={selectIncome} onChange={handleIsIncome}/>
                    </div> : null }
                    <div className='title-amount'>
                    {categoryData.amount}
                    </div>
                </div>
                
                <div className='category-data'>
                  <div id="emoji-picker" style={{ display: emojiModalOpen ? '' : 'none'}}></div>
                <TransactionCarousel cardDataParam={cardData} fetchExcess={fetchExcess} 
                limitText={limitText} handleError={handleError} onModalClose={handleTransactionModalClose} staticColor={selectColor} onCategoryUpdate={setCategoryUpdatePending}/>
                </div>
            </div>
        </div>
    , document.getElementById('category-portal'))
}

export default CategoryModal