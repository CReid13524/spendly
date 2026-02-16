from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class Upload:
    def __init__(self,
                 upload_id: UUID,
                 created: datetime,
                 bank: str,
                 file_name: str,
                 status: str,
                 transaction_ids: list[UUID],

                 user: 'User'
                 ):

        self.__id = upload_id
        self.__created = created
        self.__bank = bank
        self.__file_name = file_name
        self.__transaction_ids = transaction_ids
        self.__status = status
        self.__user = user

    def __repr__(self):
        return f"<Upload {self.id}: {self.file_name}>"

    def __eq__(self, other):
        if not isinstance(other, Upload):
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
    def created(self):
        return self.__created

    @property
    def bank(self):
        return self.__bank

    @property
    def file_name(self):
        return self.__file_name

    @property
    def status(self):
        return self.__status

    @property
    def transaction_ids(self):
        return self.__transaction_ids

    def add_transaction(self, transaction_id: UUID):
        if not isinstance(transaction_id, UUID):
            raise TypeError
        self.__transaction_ids.append(transaction_id)
