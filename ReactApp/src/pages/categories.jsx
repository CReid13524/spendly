import React, { useState } from 'react'
import PageHeader from '../components/pageHeader'
import CategoryCarousel from '../components/categoryCarousel'
import { RiApps2AddLine } from "react-icons/ri";
import QuickCategory from '../components/quickCategory';

function categories() {
  const [headerEnabled, setHeaderEnabled] = useState(true)
  const [quickAddEnabled, setQuickAddEnabled] = useState(false)

  return (
    <div id='categories-container'>
    <div id="transactionModalPortal"></div>
    <div id="category-portal"></div>
    <div id='categories-page'>
      {headerEnabled ? <PageHeader/> : <></>}
      <div id='page-heading'>
        <div id="page-title">Categories</div>
        <button onClick={() => setQuickAddEnabled(!quickAddEnabled)}>
          Quick Add <RiApps2AddLine/>
        </button>
      </div>
      {quickAddEnabled ? <QuickCategory headerToggle={() => setHeaderEnabled(!headerEnabled)}/> : <CategoryCarousel headerToggle={() => setHeaderEnabled(!headerEnabled)}/>}
    </div>
    </div>
  )
}

export default categories