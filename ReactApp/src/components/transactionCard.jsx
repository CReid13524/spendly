import React, { useState } from 'react'
import TransactionModal from './transactionModal'
import { LuCircleDashed } from "react-icons/lu";

function TransactionCard({ data, onClick, onClose, handleDelete, handleCategoryUpdate, categoryData, staticColor}) {
  if (!data) return null  
  const [isModalOpen, setIsModalOpen] = useState(false)
    const [modalData, setModalData] = useState(null)

    function handleClick() {
        onClick(data.transactionID)
        setIsModalOpen(true)
        setModalData(data)
    }

    function handleClose() {
        setIsModalOpen(false)
        onClose()
    }

    const categoryObject = categoryData.find((category) => (category.categoryID === data.categoryID))
    const backgroundColor = categoryObject ? categoryObject.colour+'99' : ''
    const icon = categoryObject && categoryObject.icon ? categoryObject.icon : <LuCircleDashed/>
    
    
    return (
        <>
        <TransactionModal transactionData={modalData} open={isModalOpen} onClose={handleClose} handleDelete={handleDelete} handleCategoryUpdate={handleCategoryUpdate} categoryData={categoryData}/>
        <div style={{backgroundColor: staticColor ? staticColor+'99' : backgroundColor}} className="carousel-card" onClick={handleClick}>
          <div className="carousel-card-algin-left">
            <div>{data.type.includes('Visa')||data.type.includes('Transfer') ? data.code : data.details}</div>
            <div className="date">{data.date}</div>
          </div>
          <div className="carousel-card-algin-right">
            <div>{data.amount}</div>
            <div className='transaction-card-icon'>{icon}</div>
          </div>
        </div>
        </>
    );
  }

export default TransactionCard