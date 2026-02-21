from typing import TYPE_CHECKING, List
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import AkahuTransaction


class AkahuCategory(ValidatingBaseModel):
    def __init__(self,
                 nzfcc_id: str,
                 nzfcc_name: str,
                 groups: dict[str, dict[str, str]],
                 ):
        # Validate and assign immutable fields
        self.__id = self._validate_string_not_empty(nzfcc_id, "nzfcc_id")
        self.__name = self._validate_string_not_empty(nzfcc_name, "nzfcc_name")
        self.__groups = self._validate_dict(groups, "groups")
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
