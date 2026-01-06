import React, { useState, useRef, useEffect } from 'react';
import TransactionCarouselBasic from '../components/transactionCarouselBasic';
import Mapbox from '../components/mapbox'


function map() {
  const [transactionData, setTransactionData] = useState<any[]>([])
  const [selectedTransaction, setSelectedTransaction] = useState<any | null>(null)
  const [fullscreenMap, setFullscreenMap] = useState<boolean>(false)
  const [updateTransaction, setUpdateTransaction] = useState<any>(null)


  const updateSelectedTransaction = (transaction: any, options: {updateFlag?: boolean, deleteFlag?: boolean} | undefined = undefined) => {
    if (transaction === null) {
      setSelectedTransaction(null)
      return
    }
    setSelectedTransaction({...transaction})
    // Update the transaction in transactionData
    if (options?.updateFlag || options?.deleteFlag) {
      const mode = options?.deleteFlag ? 'delete' : 'update'
      if (!mode) return
      setUpdateTransaction({mode:mode, transaction:{...transaction}})
    }
  }

  return (
    <div id='map-container'>
        {!fullscreenMap &&
        <div className='map-aside'>
            <div className="page-title">Map</div>
            <TransactionCarouselBasic setTransactionData={setTransactionData}
            transactionData={transactionData}
            setSelectedTransaction={setSelectedTransaction}
            selectedTransaction={selectedTransaction}
            updateTransaction={updateTransaction}
            />
        </div>
        }
        
        <Mapbox selectedTransaction={selectedTransaction} 
        setSelectedTransaction={updateSelectedTransaction}
        transactionData={transactionData}
        setFullscreenMap={setFullscreenMap}
        fullscreenMap={fullscreenMap}/>
    </div>
  )
}

export default map