from FlaskApp.services import get_user_from_token, get_db

def get_advanced_categories(date, userID):
    try:
        date_filter = (f"Where strftime('%Y-%m', Transactions.date) = '{date}'"
                    if date else '')
        curr = get_db()
        curr.execute(f"""with transData as (
                            Select Category.categoryID, IFNULL(SUM(amount),0.0) amount
                            from Category
                            LEFT JOIN Transactions on Transactions.categoryID = Category.categoryID
                            {date_filter}
                            Group by Category.categoryID
                        )

                        Select  Category.categoryID, name, colour, icon, transData.amount, isIncome, isHidden, isDefault from Category
                        JOIN transData on transData.categoryID = Category.categoryID
                        Where userID=?""", (userID,))
        data = curr.fetchall()
        columns = [column[0] for column in curr.description]
        result = [dict(zip(columns, row)) for row in data]
        for x in result:
            x['amount'] = f"{'-$' if x['amount']<0 else '$'}{abs(x['amount']):.2f}"
            x['isIncome'] = bool(x['isIncome'])
        return None, result
    except Exception as e:
        return e , None
    finally:
        curr.connection.close()

def get_basic_categories(userID):
    try:
        curr = get_db()
        curr.execute("""Select  categoryID, name, colour, icon from Category
                    where userID=?""", (userID,))
        data = curr.fetchall()
        columns = [column[0] for column in curr.description]
        result = [dict(zip(columns, row)) for row in data]
        return None, result
    except Exception as e:
        return e , None
    finally:
        curr.connection.close()

def create_category(userID, name, color, icon):
    try:
        curr = get_db()
        curr.execute("Insert into Category(userID, name, colour, icon) VALUES (?,?,?,?)",
                     (userID,name,color,icon))
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.connection.close()

def update_category(name, color, icon, isIncome, isHidden, isDefault, categoryID):
    try:
        curr = get_db()
        curr.execute("""Update Category set name=?, colour=?, icon=?, isIncome=?, isHidden=?, isDefault=?
                        Where categoryID = ?""", (name,color,icon,isIncome,isHidden,isDefault,categoryID))
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.connection.close()

def delete_category(categoryID):
    try:
        curr = get_db()
        curr.execute("""Update Category 
                    SET status='inactive'
                    Where categoryID=?;""", (categoryID,))
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.connection.close()