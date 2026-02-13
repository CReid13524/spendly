from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class Category:
    def __init__(self,
                 category_id: UUID,
                 name: str,
                 description: str,
                 colour: str,
                 icon: str | None,
                 category_type: str,
                 created: datetime,

                 parent_category: 'Category | None',
                 user: 'User'
                 ):
        self.__id = category_id
        self.__name = name
        self.__description = description
        self.__colour = colour
        self.__icon = icon
        self.__type = category_type
        self.__created = created

        self.__user = user
        self.__parent_category = parent_category

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
        if not isinstance(value, str):
            raise TypeError
        self.__name = value

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__description = value

    @property
    def colour(self):
        return self.__colour

    @colour.setter
    def colour(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__colour = value

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, value):
        if not isinstance(value, str | None):
            raise TypeError
        self.__icon = value

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        if not isinstance(value, str):
            raise TypeError
        self.__type = value

    @property
    def created(self):
        return self.__created

    @property
    def parent_category(self):
        return self.__parent_category

    @parent_category.setter
    def parent_category(self, value):
        if not isinstance(value, Category | None):
            raise TypeError
        self.__parent_category = value

    @property
    def user(self):
        return self.__user
