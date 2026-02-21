from datetime import datetime
from typing import TYPE_CHECKING
from FlaskApp.domainmodel.base import ValidatingBaseModel

from FlaskApp.domainmodel.akahu_merchant import AkahuMerchant
from FlaskApp.domainmodel.akahu_category import AkahuCategory

if TYPE_CHECKING:
    from FlaskApp.domainmodel import AkahuCategory, AkahuAccount, AkahuMerchant, Transaction, User


class AkahuTransaction(ValidatingBaseModel):
    def __init__(
            self,
            akahu_transaction_id: str,
            created: datetime,
            updated: datetime,
            meta: dict,

            amount: int,
            date: datetime,
            description: str,
            balance: int | None,
            type: str | None,
            pending: bool,

            user: 'User',
            transaction: 'Transaction',
            akahu_account: 'AkahuAccount',
            akahu_category: 'AkahuCategory | None',
            akahu_merchant: 'AkahuMerchant | None'
    ):
        # Validate and assign immutable fields
        self.__id = self._validate_string_not_empty(akahu_transaction_id, "akahu_transaction_id")
        self.__transaction = self._validate_not_none(transaction, "transaction")
        self.__akahu_account = self._validate_not_none(akahu_account, "akahu_account")
        self.__user = self._validate_not_none(user, "user")

        # Assign mutable fields via setters
        self.created = created
        self.updated = updated
        self.meta = meta

        self.amount = amount
        self.date = date
        self.description = description
        self.balance = balance
        self.type = type
        self.pending = pending

        self.akahu_category = akahu_category
        self.akahu_merchant = akahu_merchant

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

    @created.setter
    def created(self, value):
        self.__created = self._validate_datetime(value, "created")

    @property
    def updated(self):
        return self.__updated

    @updated.setter
    def updated(self, value):
        self.__updated = self._validate_datetime(value, "updated")

    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self, value):
        self.__meta = self._validate_dict(value, "meta")

    @property
    def amount(self):
        return self.__amount

    @amount.setter
    def amount(self, value):
        self.__amount = self._validate_type(value, int, "amount")

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, value):
        self.__date = self._validate_datetime(value, "date")

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = self._validate_string_not_empty(value, "description")

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = self._validate_type(value, int, "balance", allow_none=True)

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = self._validate_string_not_empty(value, "type", allow_none=True)

    @property
    def pending(self):
        return self.__pending

    @pending.setter
    def pending(self, value):
        self.__pending = self._validate_boolean(value, "pending")

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

    @akahu_category.setter
    def akahu_category(self, value):
        # Specific check for domain object type
        if value is not None and not isinstance(value, AkahuCategory):
             raise TypeError(f"akahu_category must be of type AkahuCategory, got {type(value).__name__}.")
        self.__akahu_category = value

    @property
    def akahu_merchant(self):
        return self.__akahu_merchant

    @akahu_merchant.setter
    def akahu_merchant(self, value):
        # Specific check for domain object type
        if value is not None and not isinstance(value, AkahuMerchant):
             raise TypeError(f"akahu_merchant must be of type AkahuMerchant, got {type(value).__name__}.")
        self.__akahu_merchant = value
