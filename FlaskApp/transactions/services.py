from FlaskApp.services import get_user_from_token, get_db
import pandas as pd


def get_transactions(userID, count, categoryID, date):
    try:
        curr = get_db()
        hidden_filter = ["LEFT Join Category on Transactions.categoryID = Category.categoryID", "AND (isHidden=0 OR isHidden IS NULL)"]
        category_filter = (f'AND Transactions.categoryID'\
            f'{'is NULL' if categoryID=='null' else f'= {categoryID}'}'
            if categoryID else '')
        date_filter = (f"AND strftime('%Y-%m', Transactions.date) = '{date}'"
                       if date else '')
        
        curr.execute(f"""select transactionID, title, Transactions.categoryID, type, details, particulars, code, reference, amount, Transactions.date
                        From Transactions
                        Inner Join Upload on Upload.uploadID = Transactions.uploadID
                        {hidden_filter[0] if not category_filter else ''}
                        Where Upload.userID = ? {category_filter if category_filter else hidden_filter[1]} {date_filter}
                        Order By JULIANDAY(Transactions.date) DESC
                        Limit 50 OFFSET ?""", (userID,count))
        data = curr.fetchall()

        columns = [column[0] for column in curr.description]  # Get column names
        result = [dict(zip(columns, row)) for row in data]

        for x in result:
            x['amount'] = f"{'-$' if x['amount']<0 else '$'}{abs(x['amount']):.2f}"
        
        return None, result
    except Exception as e:
        return e, None
    
def get_uploads_by_id(userID):
    try:
        curr = get_db()

        curr.execute("""Select Upload.uploadID, Upload.date, count(TransactionID) count FROM Upload
                        LEFT JOIN TRANSACTIONs on Upload.uploadID = Transactions.uploadID
                        Where Upload.userID = ?
                        Group By Upload.uploadID
                    """, (userID,))
        data = curr.fetchall()

        columns = [column[0] for column in curr.description]  # Get column names
        result = [dict(zip(columns, row)) for row in data]

        return None, result
    except Exception as e:
        return e, None

def upload_csv(file, userID, bank):
    try:
        if file.filename.lower().endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return {'error': 'Unsupported file format'}, 400
        
        #Get uploadID
        curr = get_db()
        curr.execute('insert into Upload(userID) VALUES (?)',(userID,))
        uploadID = curr.lastrowid
        
        #Apply uploadID
        df['uploadID'] = uploadID
        
        # Handle ANZ CSV
        if bank == 'anz':
            upload_csv_anz(df)
        # Handle Kiwibank 'FULL CSV'
        elif bank == 'kiwibank':
            upload_csv_kiwibank(df)

        #Insert Data
        df.to_sql('Transactions', curr.connection, if_exists='append', index=False)
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.close()

def upload_csv_kiwibank(df):
    df.rename(columns={
        'Source Code (payment type)': 'type',
        'Memo/Description': 'details',
        'TP part': 'tp_part',
        'TP code': 'tp_code',
        'TP ref': 'tp_ref',
        'OP ref': 'op_ref',
        'OP part': 'op_part',
        'OP code': 'op_code',
        'Amount': 'amount',
        'Date': 'date'
    }, inplace=True)
     
    df['title'] = None
    
    # Combine TP and OP references into a single 'reference' column
    df['reference'] = df.apply(lambda row: f"(TP) {row['tp_ref']} " if not pd.isna(row['tp_ref']) else '' + f"(OP) {row['op_ref']}" if not pd.isna(row['op_ref']) else '', axis=1)
    df['code'] = df.apply(lambda row: f"(TP) {row['tp_code']} " if not pd.isna(row['tp_code']) else '' + f"(OP) {row['op_code']}" if not pd.isna(row['op_code']) else '', axis=1)
    df['particulars'] = df.apply(lambda row: f"(TP) {row['tp_part']} " if not pd.isna(row['tp_part']) else '' + f"(OP) {row['op_part']}" if not pd.isna(row['op_part']) else '', axis=1)
    
    # Split 'Memo/Description' column on semicolon into 'details' and 'code'
    df[['title', 'details']] = df['details'].str.split(';', n=1, expand=True)

        

    df = df.drop(columns=['Account number', 'tp_part', 'tp_code', 'tp_ref', 'op_ref', 'op_part', 'op_code', 'OP name', 'OP Bank Account Number', 'Amount (credit)', 'Amount (debit)', 'Balance'])

    #Apply Date Formatting
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

def upload_csv_anz(df):
    df.rename(columns={
        'Type': 'type',
        'Details': 'details',
        'Particulars': 'particulars',
        'Code': 'code',
        'Reference': 'reference',
        'Amount': 'amount',
        'Date': 'date'
    }, inplace=True)
    
    df['title'] = df.apply(lambda row: row['code'] if 'Visa' in row['type'] or 'Transfer' in row['type'] else row['details'], axis=1)
    
    df = df.drop(columns=['ForeignCurrencyAmount', 'ConversionCharge'])
    
    #Apply Date Formatting
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

def update_category(transactionID, categoryID):
    try:
        curr = get_db()
        curr.execute("""Update Transactions
                        Set categoryID = ?
                        Where transactionID = ?""", (categoryID, transactionID))
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.close()

def delete_upload(uploadID):
    try:
        curr = get_db()
        curr.execute("PRAGMA foreign_keys = ON")
        curr.execute("""Delete from Upload
                    Where uploadID=?;
                    """, (uploadID,))
        curr.connection.commit()
        return {}, 200
    except Exception as e:
        return e
    finally:
        curr.close()

def delete_transaction(transactionID):
    try:
        curr = get_db()
        curr.execute("""Delete from Transactions
                                Where transactionID = ?""",(transactionID,))
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.close()