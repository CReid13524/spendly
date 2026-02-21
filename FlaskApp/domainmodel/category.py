from datetime import datetime
import enum
from typing import TYPE_CHECKING
from uuid import UUID
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class CategoryType(enum.Enum):
    EXPENSE = 'expense'
    INCOME = 'income'
    ALL = 'all'

class Category(ValidatingBaseModel):
    def __init__(self,
                 category_id: UUID,
                 name: str,
                 description: str,
                 colour: str,
                 icon: str | None,
                 category_type: CategoryType,
                 created: datetime,

                 parent_category: 'Category | None',
                 user: 'User'
                 ):
        # Validate and assign immutable fields
        self.__id = self._validate_uuid(category_id, "category_id")
        self.__created = self._validate_datetime(created, "created")
        self.__user = self._validate_not_none(user, "user")

        # Assign mutable fields via setters
        self.name = name
        self.description = description
        self.colour = colour
        self.icon = icon
        self.type = category_type
        self.parent_category = parent_category

    def __repr__(self):
        return f"<Category {self.id}: {self.name}>"

    def __eq__(self, other):
        if not isinstance(other, Category):
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

    @name.setter
    def name(self, value):
        self.__name = self._validate_string_not_empty(value, "name")

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = self._validate_type(value, str, "description")

    @property
    def colour(self):
        return self.__colour

    @colour.setter
    def colour(self, value):
        self.__colour = self._validate_string_not_empty(value, "colour")

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, value):
        self.__icon = self._validate_string_not_empty(value, "icon", allow_none=True)

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if isinstance(value, str):
            try:
                test_value = CategoryType(value)
                self._validate_type(test_value, CategoryType, "type")
            except ValueError:
                raise ValueError(f"Invalid CategoryType: {value}")
        elif isinstance(value, CategoryType):
            self._validate_type(value, CategoryType, "type")
        else:
            raise TypeError(f"Invalid type for CategoryType: {type(value).__name__}")
        self.__type = value

    @property
    def created(self):
        return self.__created

    @property
    def parent_category(self):
        return self.__parent_category

    @parent_category.setter
    def parent_category(self, value):
        if value is not None and not isinstance(value, Category):
            raise TypeError(f"parent_category must be a Category object, got {type(value).__name__}")
        self.__parent_category = value

    @property
    def user(self):
        return self.__user
