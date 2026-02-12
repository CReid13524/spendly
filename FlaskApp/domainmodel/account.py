from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class Account:
    def __init__(self,
                 account_id: UUID,
                 account_name: str,
                 account_type: str,
                 formatted_account: str,
                 attributes: List[str],
                 currency: str,
                 current_balance: Decimal,
                 available_balance: Decimal,
                 status: str,
                 created: datetime,
                 credit_limit: Decimal,
                 overdrawn: bool,

                 user: 'User',
                 ):
        self.__id = account_id
        self.__name = account_name
        self.__type = account_type
        self.__formatted_account = formatted_account
        self.__attributes = attributes
        self.__currency = currency
        self.__current_balance = current_balance
        self.__available_balance = available_balance
        self.__status = status
        self.__created = created
        self.__credit_limit = credit_limit
        self.__overdrawn = overdrawn

        self.__user = user

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

    @property
    def type(self):
        return self.__type

    @property
    def formatted_account(self):
        return self.__formatted_account

    @formatted_account.setter
    def formatted_account(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__formatted_account = value

    @property
    def attributes(self):
        return self.__attributes

    @property
    def currency(self):
        return self.__currency

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
        if not isinstance(value, Decimal):
            raise TypeError
        self.__credit_limit = value

    @property
    def overdrawn(self):
        return self.__overdrawn

    @overdrawn.setter
    def overdrawn(self, value):
        if not isinstance(value, bool):
            raise TypeError
        self.__overdrawn = value

    @property
    def status(self):
        return self.__status

    @property
    def created(self):
        return self.__created
