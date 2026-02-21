from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID
from FlaskApp.domainmodel.base import ValidatingBaseModel

import bcrypt

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Account, Category, ExternalIdentity

# Runtime import for Account
from FlaskApp.domainmodel.account import Account
from FlaskApp.domainmodel.category import Category


class User(ValidatingBaseModel):
    def __init__(self,
                 user_id: UUID,
                 email: str,
                 name: str,
                 password: str | None,  # None if user is created via external identity and has not set a password yet
                 status: str,
                 created: datetime,
                 last_active: datetime | None,  # None if never logged in
                 ):

        # Validate and assign fields
        self.__id = self._validate_uuid(user_id, "user_id")
        self.__email = self._validate_string_not_empty(email, "email")
        self.__name = self._validate_string_not_empty(name, "name")
        self.__password = self._validate_string_not_empty(password, "password", allow_none=True)
        self.__status = self._validate_string_not_empty(status, "status")
        self.__created = self._validate_datetime(created, "created")
        self.__last_active = self._validate_datetime(last_active, "last_active", allow_none=True)

        self.__accounts: List['Account'] = []
        self.__categories: List['Category'] = []
        self.__external_identities: dict[str, 'ExternalIdentity'] = {}

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.__email}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self):
        return self.__id

    @property
    def email(self):
        return self.__email

    @property
    def name(self):
        return self.__name

    @property
    def password(self):
        return self.__password

    @property
    def accounts(self):
        return self.__accounts

    @property
    def categories(self):
        return self.__categories

    @property
    def status(self):
        return self.__status

    @property
    def created(self):
        return self.__created

    @property
    def last_active(self):
        return self.__last_active

    @property
    def external_identities(self):
        return self.__external_identities

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.__password.encode('utf-8'))

    def connect_identity(self, identity: 'ExternalIdentity'):
        self.__external_identities[identity.provider] = identity

    # def disconnect_identity(self, provider: str):
    #     if provider in self.__external_identities:
    #         del self.__external_identities[provider]

    # def set_password(self, new_password: str):
    #     ...

    def add_account(self, account: 'Account'):
        if not isinstance(account, Account):
            raise ValueError("Invalid account")
        self.__accounts.append(account)

    # def remove_account(self, account: 'Account'):
    #     if account in self.__accounts:
    #         self.__accounts.remove(account)

    def add_category(self, category: 'Category'):
        if not isinstance(category, Category):
            raise ValueError("Invalid category")
        self.__categories.append(category)
