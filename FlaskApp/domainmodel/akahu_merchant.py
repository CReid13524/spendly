from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Merchant


class AkahuMerchant:
    def __init__(self,
                 akahu_merchant_id: str,
                 nzbn: str | None,
                 name: str,
                 website: str | None,
                 logo: str | None,
                 ):
        self.__id = akahu_merchant_id
        self.__nzbn = nzbn
        self.__name = name
        self.__website = website
        self.__logo = logo


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

