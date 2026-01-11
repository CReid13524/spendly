import React, {useEffect, useState} from "react";
import { Exception } from "sass-embedded";
import '../components/transactionCarouselBasic.scss'
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { PickerValue } from "@mui/x-date-pickers/internals";
import dayjs, { Dayjs } from "dayjs";
import "dayjs/locale/en-gb";
import { FaMapPin } from "react-icons/fa6";
import { createTheme, ThemeProvider, Theme } from "@mui/material/styles";
import { useTheme } from './theme-context'
import { config } from '../config'

interface TransactionCarouselBasicProps {
    setTransactionData: React.Dispatch<React.SetStateAction<any[]>>;
    transactionData: any[];
    setSelectedTransaction: (transaction: any) => void;
    selectedTransaction: any;
    updateTransaction: {mode:string,transaction:any} | null;
}

function TransactionCarouselBasic(props: TransactionCarouselBasicProps) {
    const [endDate, setEndDate] = useState<PickerValue | null>(null)
    const [startDate, setStartDate] = useState<PickerValue | null>(null)
    const [error, setError] = useState<JSX.Element>(<></>)
    const { theme } = useTheme()
    const [dateTheme, setDateTheme] = useState<Theme>(createTheme({
            palette: {
                mode: theme === 'dark' ? 'dark' : 'light',
            },
        }))
    const { setTransactionData,
            transactionData,
            setSelectedTransaction: setSelectedTransaction,
            selectedTransaction: selectedTransaction,
            updateTransaction
     } = props; 

    function handleError(error: Exception) {
        setError(
        <div className='error-message'>
        <h1 className="error-head">The following error has occured:</h1>
        {String(error)}
        <button className="error-dismiss" onClick={() => setError(<></>)}>Dismiss</button>
        </div>
        );
    }

    async function getTransactionData() {
        try {
        let params: URLSearchParams | null = null
        if (startDate && endDate) {
            params = new URLSearchParams({startDate:startDate.toISOString(), endDate:endDate.toISOString()});
        }
        const response = await fetch(`${config.api}/search?${params}`, {
            method: 'GET',
            credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
            throw data.error
        } else {
            setTransactionData(data.data)
        }
        } catch (error: any) {
        handleError(error)
        }
    }

    async function updateSelectedTransaction(updatedTransaction: any) {
        try {
        const response = await fetch(`${config.api}/map`, {
            headers:  {'Content-Type' : 'application/json'},
            method: 'POST',
            credentials: "include",
            body: JSON.stringify({...updatedTransaction})
        
        });
        const data = await response.json();
        if (!response.ok) {
            throw data.error
        }
        } catch (error: any) {
        handleError(error)
        }
    }

    async function deleteSelectedTransaction(updatedTransaction: any) {
        try {
        const response = await fetch(`${config.api}/map`, {
            headers:  {'Content-Type' : 'application/json'},
            credentials: "include",
            method: 'DELETE',
            body: JSON.stringify({...updatedTransaction})
        
        });
        const data = await response.json();
        if (!response.ok) {
            throw data.error
        }
        } catch (error: any) {
        handleError(error)
        }
    }

    useEffect(() => {
        if (!updateTransaction) return
        if (updateTransaction.mode === 'delete') {
            deleteSelectedTransaction(updateTransaction.transaction)
            setTransactionData((prevData: any[]) =>
                prevData.map((t: any) => t.transactionID === updateTransaction.transaction.transactionID ? {...updateTransaction.transaction, longitude:null,latitude:null} : t)
            )
            setSelectedTransaction(null)
        } else {
            updateSelectedTransaction(updateTransaction.transaction)
            setTransactionData((prevData: any[]) =>
                prevData.map((t: any) => t.transactionID === updateTransaction.transaction.transactionID ? {...updateTransaction.transaction} : t)
            )
            setSelectedTransaction(updateTransaction.transaction) // Now exists in features, set active
        }
        
    }, [updateTransaction])

    useEffect(() => {

        if (transactionData && !validateDate) return
        getTransactionData()
      },[startDate, endDate])

    const validateDate = () => {
        return false
    }

    function groupTransactions(transactionData: any[]) {
        const table: JSX.Element[] = [];
        let lastDateKey: string | null = null;

        const options: Intl.DateTimeFormatOptions = {
            weekday: 'long',
            day: 'numeric',
            month: 'short',
        };
        let count: number = 0
        transactionData.forEach((card, index) => {
            const dateObj = new Date(card.date); // assumes ISO string
            const dateKey = dateObj.toISOString().split('T')[0]; // YYYY-MM-DD
            const isOnMap = card.longitude!==null && card.latitude !==null
            

            if (dateKey !== lastDateKey) {
            lastDateKey = dateKey;
            count = 0

            table.push(
                <div className="date-row" key={`date-${dateKey}`}>
                {dateObj.toLocaleDateString('en-GB', options)}
                </div>
            );
            }
            
            table.push(
            <div 
            className={`card-row ${selectedTransaction?.transactionID === card.transactionID ? 'active' : ''}`} key={`card-${card.transactionID}`}
            style={{backgroundColor: `var(--card-${count % 2 ? "light" : "medium"})`}}
            onClick={isOnMap ? () => setSelectedTransaction(card) : undefined}
            >
                <span>{card.title}</span>
                <div>
                    <span>{card.amount}</span>
                    {isOnMap ? null : <FaMapPin onClick={() => setSelectedTransaction(card)}/>}
                </div>
            </div>
            );
            count += 1
        });

        return table;
        }

    useEffect(() => {
        const newTheme = createTheme({
            palette: {
                mode: theme === 'dark' ? 'dark' : 'light',
            },
        })

        setDateTheme(newTheme)
    }, [theme])

    return (
        <>
        {error}

        <div className="date-picker">
            <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale="en-gb">
                <ThemeProvider theme={dateTheme}>
                    <DatePicker className="date-input"
                        label="Start date"
                        value={startDate}
                        onChange={(d) => setStartDate(d)}
                        maxDate={endDate ? endDate : dayjs()}
                        
                    />
                    <DatePicker className="date-input"
                        label="End date"
                        value={endDate}
                        onChange={(d) => setEndDate(d)}
                        maxDate={dayjs()}
                        minDate={startDate as Dayjs}
                    />
                </ThemeProvider>
            </LocalizationProvider>
        </div>

        <div className="transaction-container">
            {groupTransactions(transactionData)}
        </div>

        <div className="transaction-detail-modal">

        </div>
        </>
    )
}

export default TransactionCarouselBasic;