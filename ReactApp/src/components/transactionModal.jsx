import React from 'react'
import ReactDOM from 'react-dom';
import { MdOutlineArrowBack } from "react-icons/md";
import { LuCircleDashed } from "react-icons/lu";

function TransactionModal({open, transactionData, onClose}) {
    if (!open) return null

    const [day, month, year] = transactionData.date.split('/'); // Split the input string
    const date = new Date(year, month - 1, day); // Create a Date object
    const options = { weekday: 'long', day: 'numeric', month: 'short' };
    const dateString = date.toLocaleDateString('en-US', options)

    return ReactDOM.createPortal(
        <div className='transaction-modal-container'>
            <div className='transaction-modal'>
                <div className='transaction-title'>
                    <div className='title-header'>
                        <div className='title-return'>
                            <MdOutlineArrowBack onClick={onClose}/>
                            {transactionData.type.includes('Visa')||transactionData.type.includes('Transfer') ? transactionData.code : transactionData.details}
                        </div>
                        <LuCircleDashed />
                    </div>
                    <div className='title-amount'>
                        {transactionData.amount >= 0 ? '$' : '-$'}{Math.abs(transactionData.amount).toFixed(2)}
                    </div>
                </div>
                <div className='transaction-data'>
                    <div className='data-head'>
                        <div>{transactionData.details}</div>
                        <div>{dateString}</div>
                        <div><em>{transactionData.type}</em></div>
                    </div>
                    <div><strong>Particulars:</strong> {transactionData.particulars}</div>
                    <div><strong>Code:</strong> {transactionData.code}</div>
                    <div><strong>Reference:</strong> {transactionData.reference}</div>
                </div>
            </div>
        </div>
    , document.getElementById('portal'))
}

export default TransactionModal