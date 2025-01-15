import React, { useState } from 'react'
import CategoryModal from './categoryModal'
import { LuCircleDashed } from "react-icons/lu";

function CategoryCard({ data, onClick, onClose, handleError, onUpdate}) {
    const [isModalOpen, setIsModalOpen] = useState(false)

    function handleClick() {
        onClick(data.categoryID)
        setIsModalOpen(true)
    }

    function handleClose() {
        setIsModalOpen(false)
        onClose()
    }

    return (
        <>
        <CategoryModal categoryData={data} open={isModalOpen} onClose={handleClose} handleError={handleError} onUpdate={onUpdate}/>
        <div style={{backgroundColor : data.colour +'99'}} className="category-carousel-card" onClick={handleClick}>
          <div className="carousel-card-algin-left">
            <div className='card-icon'>{data.icon ? data.icon : <LuCircleDashed/>}</div>
            <div className='card-name'>{data.name}</div>
          </div>
        </div>
        </>
    );
  }

export default CategoryCard