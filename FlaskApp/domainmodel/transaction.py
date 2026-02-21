from datetime import datetime
import enum
from typing import TYPE_CHECKING
from uuid import UUID
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Category, Account, User, Merchant

# ... (enum definitions remain same)


class TransactionType(enum.Enum):
    CREDIT = 'credit'
    DEBIT = 'debit'
    PAYMENT = 'payment'
    TRANSFER = 'transfer'
    STANDING_ORDER = 'standing order'
    EFTPOS = 'eftpos'
    INTEREST = 'interest'
    FEE = 'fee'
    TAX = 'tax'
    CREDIT_CARD = 'credit card'
    DIRECT_CREDIT = 'direct credit'
    DIRECT_DEBIT = 'direct debit'
    ATM = 'atm'
    LOAN = 'loan'


class Transaction(ValidatingBaseModel):
    def __init__(
            self,
            transaction_id: UUID,
            amount: int,
            date: datetime,
            description: str,
            balance: int | None,
            transaction_type: TransactionType,
            status: str,
            pending: bool,
            created: datetime,
            latitude: float | None,
            longitude: float | None,

            user: 'User',
            account: 'Account',
            category: 'Category | None',
            merchant: 'Merchant | None',
    ):
        # Validate and assign immutable fields
        self.__id = self._validate_uuid(transaction_id, "transaction_id")
        self.__created = self._validate_datetime(created, "created")
        self.__user = self._validate_not_none(user, "user")

        # Assign mutable fields via setters
        self.amount = amount
        self.date = date
        self.description = description
        self.balance = balance
        self.type = transaction_type
        self.status = status
        self.pending = pending
        self.latitude = latitude
        self.longitude = longitude

        self.account = account
        self.category = category
        self.merchant = merchant

    def __repr__(self):
        return f"<Transaction {self.id}: {self.description}>"

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        return self.__id

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
        if isinstance(value, str):
            try:
                test_value = TransactionType(value)
                self._validate_type(test_value, TransactionType, "type")
            except ValueError:
                raise ValueError(f"Invalid TransactionType: {value}")
        elif isinstance(value, TransactionType):
            self._validate_type(value, TransactionType, "type")
        else:
            raise TypeError(f"Invalid type for TransactionType: {type(value).__name__}")
        self.__type = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = self._validate_string_not_empty(value, "status")

    @property
    def pending(self):
        return self.__pending

    @pending.setter
    def pending(self, value):
        self.__pending = self._validate_boolean(value, "pending")

    @property
    def created(self):
        return self.__created

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        self.__latitude = self._validate_float(value, "latitude", allow_none=True)

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        self.__longitude = self._validate_float(value, "longitude", allow_none=True)

    @property
    def user(self):
        return self.__user

    @property
    def account(self):
        return self.__account

    @account.setter
    def account(self, value: 'Account'):
        # Specific check for domain object
        from FlaskApp.domainmodel.account import Account
        if not isinstance(value, Account):
            raise TypeError(f"account must be an Account object, got {type(value).__name__}")
        self.__account = value

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value: 'Category | None'):
        # Specific check for domain object
        from FlaskApp.domainmodel.category import Category
        if value is not None and not isinstance(value, Category):
            raise TypeError(f"category must be a Category object, got {type(value).__name__}")
        self.__category = value

    @property
    def merchant(self):
        return self.__merchant

    @merchant.setter
    def merchant(self, value: 'Merchant | None'):
        # Specific check for domain object
        from FlaskApp.domainmodel.merchant import Merchant
        if value is not None and not isinstance(value, Merchant):
            raise TypeError(f"merchant must be a Merchant object, got {type(value).__name__}")
        self.__merchant = value
