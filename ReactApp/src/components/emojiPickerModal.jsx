import React from 'react'
import ReactDOM from 'react-dom';
import Picker from '@emoji-mart/react'

function EmojiPickerModal({open, onSelect, onClose}) {
    if (!open) return null

    return ReactDOM.createPortal(
        <div>
           <Picker onEmojiSelect={e => onSelect(e.native)} theme="light" onClickOutside={onClose}/>
        </div>
    , document.getElementById('emoji-picker'))
}

export default EmojiPickerModal