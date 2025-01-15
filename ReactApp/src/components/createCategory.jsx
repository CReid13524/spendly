import EmojiPickerModal from './emojiPickerModal';
import React, { useEffect, useState } from 'react'
import { AiOutlinePlus } from "react-icons/ai";


function CreateCategory({onSubmit}) {
    const [selectIcon, setSelectIcon] = useState(null)
    const [selectColor, setSelectColor] = useState('#ffffff')
    const [selectName, setSelectName] = useState('')
    const [emojiModalOpen, setEmojiModalOpen] = useState(false)
    const [isActive, setIsActive] = useState(false)

    function handleSubmit(e) {
        e.preventDefault()
        if (onSubmit(selectName, selectColor, selectIcon)) {
            setSelectIcon(<AiOutlinePlus/>)
            setSelectColor('#ffffff')
            setSelectName('')
            setEmojiModalOpen(false)
        }
    }

    const handleToggleEmojiPicker = (e) => {
        e.stopPropagation(); 
        setEmojiModalOpen((prev) => !prev);
      };

    return (
        <>
        <EmojiPickerModal open={emojiModalOpen} onSelect={e => setSelectIcon(e)} onClose={handleToggleEmojiPicker}/>
        { !isActive ? 
        <div className="category-carousel-card" onClick={() => setIsActive(!isActive)}>
          <div className="carousel-card-algin-left">
            <div className='card-icon'><AiOutlinePlus/></div>
            <div className='card-name'>Create category</div>
          </div>
        </div>
        : <form style={{backgroundColor : selectColor +'99'}} className="category-carousel-card" onSubmit={handleSubmit}>
          <div className="carousel-card-algin-left">
            <div onClick={handleToggleEmojiPicker} className='card-icon'>{selectIcon ? selectIcon : <AiOutlinePlus/>}</div>
            <input className='card-name' required placeholder='Category label' value={selectName} onChange={e => setSelectName(e.target.value)} />
          </div>
          <button type='submit' className='new-category-done-text'>DONE</button>
          <div style={{backgroundColor:selectColor}}className="carousel-card-algin-right">
          <input type='color' value={selectColor} required onChange={e => setSelectColor(e.target.value)}/>
          </div>
        </form> }
        </>
    );
  }

export default CreateCategory