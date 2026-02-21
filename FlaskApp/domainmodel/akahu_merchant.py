from typing import TYPE_CHECKING
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Merchant


class AkahuMerchant(ValidatingBaseModel):
    def __init__(self,
                 akahu_merchant_id: str,
                 nzbn: str | None,
                 name: str,
                 website: str | None,
                 logo: str | None,
                 ):
        # Validate and assign immutable fields
        self.__id = self._validate_string_not_empty(akahu_merchant_id, "akahu_merchant_id")
        self.__nzbn = self._validate_string_not_empty(nzbn, "nzbn", allow_none=True)
        self.__name = self._validate_string_not_empty(name, "name")
        self.__website = self._validate_string_not_empty(website, "website", allow_none=True)
        self.__logo = self._validate_string_not_empty(logo, "logo", allow_none=True)


    def __repr__(self):
        return f"<AkahuMerchant: {self.merchant}>"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, AkahuMerchant):
            return False
        return self.id == other.id

    @property
    def id(self):
        return self.__id

    @property
    def nzbn(self):
        return self.__nzbn

    @property
    def name(self):
        return self.__name

    @property
    def website(self):
        return self.__website

    @property
    def logo(self):
        return self.__logo

