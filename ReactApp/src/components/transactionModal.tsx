import React, { useEffect, useState, useRef } from 'react'
import { createPortal } from 'react-dom';
import { MdOutlineArrowBack } from "react-icons/md";
import { MdDelete } from "react-icons/md";
import Select, { SingleValue } from 'react-select'

import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

interface TransactionModalProps {
  open: boolean;
  transactionData: any;
  onClose: () => void;
  handleDelete: () => void;
  handleCategoryUpdate: (categoryId: any) => Promise<void>;
  categoryData: any[];
  dateString?: string
}

function TransactionModal({open, transactionData, onClose, handleDelete, handleCategoryUpdate, categoryData, dateString}: TransactionModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [selectedOption, setSelectedOption] = useState<SingleValue<{ value: any; label: string; color: any; } | null>>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoiY3JlaWQxMzUyNCIsImEiOiJjbWp1ZGdlNWQ1YjdxM2ZwdXE1MDN0d3JqIn0.-TUhqjgScfnYvsfxfYgPvA"

  if (open) {
    const [year, month, day] = transactionData.date.split('-'); // Split the input string
    const date = new Date(year, month - 1, day); // Create a Date object
    const options: Intl.DateTimeFormatOptions = { weekday: 'long', day: 'numeric', month: 'short' };
    dateString = date.toLocaleDateString('en-US', options)
  }

  async function handleCategorySelect(e: SingleValue<{ value: any; label: string; color: any; } | null>) {
    if (!e) return;
      setSelectedOption(e)
      setIsLoading(true)
      await handleCategoryUpdate(e.value)
      setIsLoading(false)
  }

  function handleDeleteClose() {
      onClose()
      handleDelete()  
  }

  const defaultSelectOption = {value:null, label:"No category", color:''}
  const selectOptions = [defaultSelectOption,...categoryData.map((e) => (
      {value:e.categoryID, label:`${e.icon ? e.icon : '⚪'} ${e.name}`, color:e.colour}
  ))]

  useEffect(() => {
      if (transactionData?.categoryID) {
        const foundOption = selectOptions.find(
          (item) => item.value === transactionData.categoryID
        );
        setSelectedOption(foundOption || null); // Set to null if not found
      } else {
        setSelectedOption(null);
      }
    }, [transactionData]);

  const customStyles = {
      option: (provided: any, state: any) => ({
        ...provided,
        backgroundColor:
          (state.isFocused || state.isSelected)// Apply styles only if the option has a value
            ? (state.value ? state.data.color : '#d2d2d2')
            : "white",
        color:
          (state.isFocused || state.isSelected) && state.data.value
            ? "white"
            : state.data.color,
        cursor: "pointer",
        ":active": {
          backgroundColor: state.data.value ? state.data.color : "white",
          color: state.data.value ? "white" : "inherit",
        },
      }),
      singleValue: (provided: any, state: any) => ({
        ...provided,
        color: state.data.color, // Color of the selected option
      }),
    };
    
  // Mapbox
  useEffect(() => {
    if (!open) return;
    if (!mapContainerRef.current) return;
    if (mapRef.current) return; // prevent re-init

    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN

    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current!,
      center: [-77.03915, 38.90025],
      zoom: 12.5,
      style: 'mapbox://styles/mapbox/dark-v11',
    });

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [open]);

  return open ? createPortal(
    <div className='transaction-modal-container'>
      <div className='transaction-modal'>
        <div style={{backgroundColor:selectedOption && selectedOption.value ? selectedOption.color+'99' : ''}} className='transaction-title'>
          <div className='title-header'>
            <div className='title-return'>
              <MdOutlineArrowBack onClick={onClose}/>
              {transactionData.title}
            </div>
            <MdDelete onClick={handleDeleteClose}/>
          </div>
          <div className='title-amount'>
            {transactionData.amount}
          </div>
        </div>
        <Select options={selectOptions} closeMenuOnSelect noOptionsMessage={() => "Go to 'Categories' page to make some new Categories!"}
        placeholder="Select a category for this transaction" styles={customStyles} value={selectedOption} onChange={handleCategorySelect}
        isLoading={isLoading} isDisabled={isLoading}
        />
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
        <div className="w-3/4">
          <div ref={mapContainerRef} className="map" />
        </div>
      </div>
    </div>
  , document.getElementById('transactionModalPortal')!) : null
}

export default TransactionModal