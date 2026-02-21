from typing import TYPE_CHECKING
from uuid import UUID
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class Merchant(ValidatingBaseModel):
    def __init__(self,
                 merchant_id: UUID,
                 nzbn: str | None,
                 name: str,
                 website: str | None,
                 logo: str | None,

                 user: 'User'
                 ):

        # Validate and assign immutable fields
        self.__id = self._validate_uuid(merchant_id, "merchant_id")
        self.__user = self._validate_not_none(user, "user")

        # Assign mutable fields via setters
        self.name = name
        self.nzbn = nzbn
        self.website = website
        self.logo = logo

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

    @nzbn.setter
    def nzbn(self, value):
        self.__nzbn = self._validate_string_not_empty(value, "nzbn", allow_none=True)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = self._validate_string_not_empty(value, "name")

    @property
    def website(self):
        return self.__website

    @website.setter
    def website(self, value):
        self.__website = self._validate_string_not_empty(value, "website", allow_none=True)

    @property
    def logo(self):
        return self.__logo

    @logo.setter
    def logo(self, value):
        self.__logo = self._validate_string_not_empty(value, "logo", allow_none=True)
