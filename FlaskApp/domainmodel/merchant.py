from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class Merchant:
    def __init__(self,
                 merchant_id: UUID,
                 nzbn: str | None,
                 name: str,
                 website: str | None,
                 logo: str | None,

                 user: 'User'
                 ):

        self.__id = merchant_id
        self.__nzbn = nzbn
        self.__name = name
        self.__website = website
        self.__logo = logo

        self.__user = user

    def __repr__(self):
        return f"<Merchant {self.id}: {self.name}>"

    def __eq__(self, other):
        if not isinstance(other, Merchant):
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
    def nzbn(self):
        return self.__nzbn

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            raise TypeError
        self.__name = value

    @property
    def website(self):
        return self.__website

    @website.setter
    def website(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__website = value

    @property
    def logo(self):
        return self.__logo

    @logo.setter
    def logo(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__logo = value
