from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Category, Account, User, Merchant


class Transaction:
    def __init__(
            self,
            transaction_id: UUID,
            amount: Decimal,
            date: datetime,
            description: str,
            balance: Decimal | None,
            transaction_type: str,
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
        self.__id = transaction_id
        self.__amount = amount
        self.__date = date
        self.__description = description
        self.__balance = balance
        self.__type = transaction_type
        self.__status = status
        self.__pending = pending
        self.__created = created
        self.__latitude = latitude
        self.__longitude = longitude

        self.__user = user
        self.__account = account
        self.__category = category
        self.__merchant = merchant

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
        if not isinstance(value, Decimal):
            raise TypeError
        self.__amount = value

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, value):
        if not isinstance(value, datetime):
            raise TypeError
        self.__date = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__description = value

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        if value is not None and not isinstance(value, Decimal):
            raise TypeError
        self.__balance = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__type = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__status = value

    @property
    def pending(self):
        return self.__pending

    @pending.setter
    def pending(self, value):
        if not isinstance(value, bool):
            raise TypeError
        self.__pending = value

    @property
    def created(self):
        return self.__created

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        if value is not None and not isinstance(value, float):
            raise TypeError
        self.__latitude = value

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        if value is not None and not isinstance(value, float):
            raise TypeError
        self.__longitude = value

    @property
    def user(self):
        return self.__user

    @property
    def account(self):
        return self.__account

    @account.setter
    def account(self, value: 'Account'):
        if not isinstance(value, Account):
            raise TypeError
        self.__account = value

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value: 'Category | None'):
        if value is not None and not isinstance(value, Category):
            raise TypeError
        self.__category = value

    @property
    def merchant(self):
        return self.__merchant

    @merchant.setter
    def merchant(self, value: 'Merchant | None'):
        if value is not None and not isinstance(value, Merchant):
            raise TypeError
        self.__merchant = value
