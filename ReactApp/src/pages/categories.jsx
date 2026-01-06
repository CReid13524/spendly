import React, { useState } from 'react'
import CategoryCarousel from '../components/categoryCarousel'
import { RiApps2AddLine } from "react-icons/ri";
import QuickCategory from '../components/quickCategory';

function categories() {
  const [quickAddEnabled, setQuickAddEnabled] = useState(false)

  return (
    <div id='categories-container'>
    <div id="transactionModalPortal"></div>
    <div id="category-portal"></div>
    <div id='categories-page'>
      <div id='page-heading'>
        <div className="page-title">Categories</div>
        <button onClick={() => setQuickAddEnabled(!quickAddEnabled)}>
          Quick Add <RiApps2AddLine/>
        </button>
      </div>
      {quickAddEnabled ? <QuickCategory/> : <CategoryCarousel/>}
    </div>
    </div>
  )
}

export default categories