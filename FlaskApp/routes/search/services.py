# TODO: Refactor this file to work with new database structure and akahu integration.
from FlaskApp.serv.services import get_user_from_token, get_db

def get_transactions(userID, start_date, end_date):
    try:
        curr = get_db()
        params = [userID]
        if (start_date and end_date):
            params.extend([start_date, end_date])
        curr.execute(f"""select transactionID, title, Transactions.categoryID, type, details, particulars, code, reference, amount, Transactions.date, latitude, longitude,
                        Category.colour, Category.icon
                        From Transactions
                        Inner Join Upload on Upload.uploadID = Transactions.uploadID
                        LEFT Join Category on Transactions.categoryID = Category.categoryID
                        Where Upload.userID = ?
                        {"""AND JULIANDAY(Transactions.date)-JULIANDAY(?) >= 0
                        AND JULIANDAY(Transactions.date)-JULIANDAY(?) <= 0"""
                        if start_date and end_date else ''}
                        Order By JULIANDAY(Transactions.date) DESC
                        """, params)
        data = curr.fetchall()

        columns = [column[0] for column in curr.description]  # Get column names
        result = [dict(zip(columns, row)) for row in data]

        for x in result:
            x['amount'] = f"{'-$' if x['amount']<0 else '$'}{abs(x['amount']):.2f}"

        return None, result
    except Exception as e:
        return e, None