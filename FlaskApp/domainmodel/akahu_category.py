from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from FlaskApp.domainmodel import AkahuTransaction


class AkahuCategory:
    def __init__(self,
                 nzfcc_id: str,
                 nzfcc_name: str,
                 groups: dict[str, dict[str, str]],
                 ):
        self.__id = nzfcc_id
        self.__name = nzfcc_name
        self.__groups = groups
        self.__transactions: List['AkahuTransaction'] = []

    def __repr__(self):
        return f"<AkahuCategory: {self.name}>"

    def __eq__(self, other):
        if not isinstance(other, AkahuCategory):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    @property
    def groups(self):
        return self.__groups

    @property
    def transactions(self):
        return self.__transactions
