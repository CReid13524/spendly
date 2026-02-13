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
            description: str | None,
            balance: Decimal,
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

    @property
    def pending(self):
        return self.__pending

    @property
    def created(self):
        return self.__created

    @property
    def latitude(self):
        return self.__latitude

    @latitude.setter
    def latitude(self, value):
        if not isinstance(value, float):
            raise TypeError
        self.__latitude = value

    @property
    def longitude(self):
        return self.__longitude

    @longitude.setter
    def longitude(self, value):
        if not isinstance(value, float):
            raise TypeError
        self.__longitude = value

    @property
    def user(self):
        return self.__user

    @property
    def account(self):
        return self.__account

    @property
    def category(self):
        return self.__category

    @category.setter
    def category(self, value: 'Category'):
        if not isinstance(value, Category):
            raise TypeError
        self.__category = value

    @property
    def merchant(self):
        return self.__merchant
