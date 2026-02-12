# TODO: Refactor this file to work with new database structure and akahu integration.
from FlaskApp.serv.services import get_db, get_user_from_token

def updateTransactionCoordinates(transactionID, longitude, latitude):
    try:
        curr = get_db()
        curr.execute("""Update Transactions
                     SET longitude=? , latitude = ?
                     WHERE transactionID=?""",(longitude,latitude,transactionID))
        curr.connection.commit()
    except Exception as e:
        return e
    finally:
        curr.connection.close()

def deleteTransactionCoordinates(transactionID):
    try:
        curr = get_db()
        curr.execute("""Update Transactions
                     SET longitude=null and latitude=null
                     WHERE transactionID=?""",(transactionID,))
        curr.connection.commit()
        return None,None
    except Exception as e:
        return e, None
    finally:
        curr.connection.close()