import React, { useState } from 'react'
import PageHeader from '../components/pageHeader'
import CategoryCarousel from '../components/CategoryCarousel'

function categories() {
  const [headerEnabled, setHeaderEnabled] = useState(true)

  return (
    <div id='categories-container'>
    <div id="transactionModalPortal"></div>
    <div id="category-portal"></div>
    <div id='categories-page'>
      {headerEnabled ? <PageHeader/> : <></>}
      <div id="page-title">Categories</div>
      <CategoryCarousel headerToggle={() => setHeaderEnabled(!headerEnabled)}/>
    </div>
    </div>
  )
}

export default categories