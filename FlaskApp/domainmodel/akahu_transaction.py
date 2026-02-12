from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from FlaskApp.domainmodel import AkahuCategory, AkahuAccount, AkahuMerchant, Transaction, User


class AkahuTransaction:
    def __init__(
            self,
            akahu_transaction_id: str,
            created: datetime,
            updated: datetime,
            meta: dict,

            user: 'User',
            transaction: 'Transaction',
            akahu_account: 'AkahuAccount',
            akahu_category: 'AkahuCategory | None',
            akahu_merchant: 'AkahuMerchant | None'
    ):
        self.__id = akahu_transaction_id
        # Akahu hash is deprecated
        self.__created = created
        self.__updated = updated
        self.__meta = meta

        self.__transaction = transaction
        self.__akahu_account = akahu_account
        self.__akahu_category = akahu_category
        self.__akahu_merchant = akahu_merchant
        self.__user = user

    def __repr__(self):
        return f"<AkahuTransaction: {self.transaction}>"

    def __eq__(self, other):
        if not isinstance(other, AkahuTransaction):
            return False
        return self.__id == other.__id

    def __hash__(self):
        return hash(self.__id)

    @property
    def id(self):
        return self.__id

    @property
    def created(self):
        return self.__created

    @property
    def updated(self):
        return self.__updated

    @property
    def meta(self):
        return self.__meta

    @property
    def user(self):
        return self.__user

    @property
    def transaction(self):
        return self.__transaction

    @property
    def akahu_account(self):
        return self.__akahu_account

    @property
    def akahu_category(self):
        return self.__akahu_category

    @property
    def akahu_merchant(self):
        return self.__akahu_merchant
