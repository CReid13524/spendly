import React, { useState } from 'react'
import TransactionModal from './transactionModal'

function Card({ data, onClick, onClose }) {
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

    return (
        <>
        <TransactionModal transactionData={modalData} open={isModalOpen} onClose={handleClose}/>
        <div className="carousel-card" onClick={handleClick}>
          <div className="carousel-card-algin-left">
            <div>{data.type.includes('Visa')||data.type.includes('Transfer') ? data.code : data.details}</div>
            <div className="date">{data.date}</div>
          </div>
          <div className="carousel-card-algin-right">
            {data.amount >= 0 ? '$' : '-$'}{Math.abs(data.amount).toFixed(2)}
          </div>
        </div>
        </>
    );
  }

export default Card