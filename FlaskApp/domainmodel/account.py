from __future__ import annotations

from datetime import datetime
import enum
from typing import List
from typing import TYPE_CHECKING
from uuid import UUID
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User

class AccountType(enum.Enum):
    CHECKING = 'checking'
    SAVINGS = 'savings'
    CREDITCARD = 'credit'
    LOAN = 'loan'
    KIWISAVER = 'kiwisaver'
    INVESTMENT = 'investment'
    TERMDEPOSIT = 'term_deposit'
    FOREIGN = 'foreign'
    TAX = 'tax'
    REWARDS = 'rewards'
    WALLET = 'wallet'

class AccountAttribute(enum.Enum):
    TRANSACTIONS = 'transactions'
    TRANSFER_TO = 'transfer_to'
    TRANSFER_FROM = 'transfer_from'
    PAYMENT_TO = 'payment_to'
    PAYMENT_FROM = 'payment_from'


class Account(ValidatingBaseModel):
    def __init__(self,
                 account_id: UUID,
                 account_name: str,
                 account_type: AccountType,
                 formatted_account: str,
                 attributes: List[AccountAttribute],
                 currency: str,
                 current_balance: int,
                 available_balance: int | None,
                 status: str,
                 created: datetime,
                 credit_limit: int | None,
                 overdrawn: bool | None,
                 provider_name: str,
                 provider_logo: str,

                 user: 'User',
                 ):
        # Validate and assign immutable fields directly
        self.__id = self._validate_uuid(account_id, "account_id")
        self.__user = self._validate_not_none(user, "user")
        self.__created = self._validate_datetime(created, "created")
        self.__current_balance = self._validate_type(current_balance, int, "current_balance")
        self.__available_balance = self._validate_type(available_balance, int, "available_balance", allow_none=True)
        self.__overdrawn = self._validate_boolean(overdrawn, "overdrawn", allow_none=True)
        self.__provider_name = self._validate_string_not_empty(provider_name, "provider_name")
        self.__provider_logo = self._validate_string_not_empty(provider_logo, "provider_logo")

        # Assign mutable fields via setters for validation
        self.name = account_name
        self.type = account_type
        self.formatted_account = formatted_account
        self.attributes = attributes
        self.currency = currency
        self.status = status
        self.credit_limit = credit_limit

    def __repr__(self):
        return f"Account {self.id}: {self.name}"

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        return self.__id

    @property
    def user(self):
        return self.__user

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = self._validate_string_not_empty(value, "name")

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        # Handle coercion from string if necessary, then validate type
        if isinstance(value, str):
            try:
                test_value = AccountType(value)
                self._validate_type(test_value, AccountType, "type")
            except ValueError:
                raise ValueError(f"Invalid AccountType: {value}")
        elif isinstance(value, AccountType):
            self._validate_type(value, AccountType, "type")
        else:
            raise TypeError(f"Invalid type for AccountType: {type(value).__name__}")
        self.__type = value

    @property
    def formatted_account(self):
        return self.__formatted_account

    @formatted_account.setter
    def formatted_account(self, value):
        self.__formatted_account = self._validate_string_not_empty(value, "formatted_account")

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, value):
        # Validate list and its items
        self._validate_type(value, list, "attributes")
        for attr in value:
            if isinstance(attr, str):
                try:
                    AccountAttribute(attr)
                except ValueError:
                    raise ValueError(f"Invalid AccountAttribute: {attr}")
            else:
                raise TypeError(f"Invalid attribute type in list: {type(attr)}")
        self.__attributes = value

    @property
    def currency(self):
        return self.__currency

    @currency.setter
    def currency(self, value):
        self.__currency = self._validate_string_not_empty(value, "currency")

    @property
    def current_balance(self):
        return self.__current_balance

    @property
    def available_balance(self):
        return self.__available_balance

    @property
    def credit_limit(self):
        return self.__credit_limit

    @credit_limit.setter
    def credit_limit(self, value):
        self.__credit_limit = self._validate_type(value, int, "credit_limit", allow_none=True)

    @property
    def overdrawn(self):
        return self.__overdrawn

    @property
    def provider_name(self):
        return self.__provider_name

    @property
    def provider_logo(self):
        return self.__provider_logo

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = self._validate_string_not_empty(value, "status")

    @property
    def created(self):
        return self.__created
