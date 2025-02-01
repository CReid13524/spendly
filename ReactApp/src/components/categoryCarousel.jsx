import React, { useEffect, useRef, useState } from "react";
import "./categoryCarousel.css"
import CategoryCard from "./categoryCard";
import CreateCategory from './createCategory'

const CategoryCarousel = ({headerToggle}) => {
  const [error, setError] = useState(<></>)
  const [cardData, setCardData] = useState([])
  const [limitText, setLimitText] = useState('')
  const [refreshState, setRefreshState] = useState(false)

  function handleError(error) {
    setError(
      <div className='error-message'>
      <h1 className="error-head">The following error has occured:</h1>
      {String(error)}
      <button className="error-dismiss" onClick={() => setError(<></>)}>Dismiss</button>
      </div>
    );
  }

  async function getCategoryData() {
    
    try {
      const response = await fetch('/api/categories/advanced', {method: 'GET'});
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        setCardData(data.data)
        if (data.data.length === 0) {
          setLimitText("Click 'Add' to make some categories! ")
        }
      }
    } catch (error) {
      handleError(error)
    }
  }

  async function createCategory(name,color,icon) {

    try {
      const response = await fetch('/api/categories', {
        method: 'POST',
        headers:  {'Content-Type' : 'application/json'},
        body: JSON.stringify({"name":name,"color":color,"icon":icon})
      });
      const data = await response.json();
      if (!response.ok) {
          throw data.error
      } else {
        getCategoryData()
        return true
      }
    } catch (error) {
      handleError(error)
    }
  }

  useEffect(() => {
    getCategoryData()
  },[refreshState])

  return (
    <>
    {error}
    <div id="emoji-picker"></div>
    <div id="category-vertical-scroll-carousel">
      <CreateCategory onSubmit={createCategory}/>
      
    {cardData.map((card) => (
        <CategoryCard key={card.categoryID} data={card} onClick={headerToggle} onClose={headerToggle} handleError={handleError} onUpdate={() => setRefreshState(!refreshState)}/>
        ))}
      <div className="limit-reached-text">{limitText}</div>
    </div>
    </>
  );

};

export default CategoryCarousel;
