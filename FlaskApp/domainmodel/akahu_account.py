from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Account, User


class AkahuAccount():
    def __init__(self,
                 akahu_account_id: str,
                 authorisation: str,
                 meta: dict,
                 connection_id: str,
                 connection_name: str,
                 connection_logo: str,
                 connection_type: str,
                 refreshed: dict[str, datetime],
                 refresh_attempt: datetime,

                 user: 'User',
                 account: 'Account',
                 ):
        self.__id = akahu_account_id
        self.__authorisation = authorisation
        self.__meta = meta
        self.__connection_id = connection_id
        self.__connection_name = connection_name
        self.__connection_logo = connection_logo
        self.__connection_type = connection_type
        self.__refreshed = refreshed
        self.__refresh_attempt = refresh_attempt
        self.__user = user
        self.__account = account

    def __repr__(self):
        return f"AkahuAccount: {self.account}"

    def __eq__(self, other):
        if not isinstance(other, AkahuAccount):
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
    def account(self):
        return self.__account

    @property
    def meta(self):
        return self.__meta

    @property
    def authorisation(self):
        return self.__authorisation

    @property
    def connection_id(self):
        return self.__connection_id

    @property
    def connection_name(self):
        return self.__connection_name

    @property
    def connection_logo(self):
        return self.__connection_logo

    @property
    def connection_type(self):
        return self.__connection_type

    @property
    def refreshed(self):
        return self.__refreshed

    @refreshed.setter
    def refreshed(self, value):
        if not isinstance(value, datetime):
            raise TypeError
        self.__refreshed = value

    @property
    def refresh_attempt(self):
        return self.__refresh_attempt

    @refresh_attempt.setter
    def refresh_attempt(self, value):
        if not isinstance(value, datetime):
            raise TypeError
        self.__refresh_attempt = value
