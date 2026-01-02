import React, { useState } from 'react'
import CategoryModal from './categoryModal'
import { LuCircleDashed } from "react-icons/lu";

function CategoryCard({ data, handleError, onUpdate}) {
    const [isModalOpen, setIsModalOpen] = useState(false)

    function handleClick() {
        setIsModalOpen(true)
    }

    function handleClose() {
        setIsModalOpen(false)
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