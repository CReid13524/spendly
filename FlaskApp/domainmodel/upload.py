from datetime import datetime
import enum
from typing import TYPE_CHECKING
from uuid import UUID
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import User


class SupportedBank(enum.Enum):
    ANZ = 'anz'
    KIWIBANK = 'kiwibank'


class Upload(ValidatingBaseModel):
    def __init__(self,
                 upload_id: UUID,
                 created: datetime,
                 bank: str,
                 file_name: str,
                 status: str,
                 transaction_ids: list[UUID],

                 user: 'User'
                 ):

        # Validate and assign fields
        self.__id = self._validate_uuid(upload_id, "upload_id")
        self.__created = self._validate_datetime(created, "created")
        test_bank = SupportedBank(bank)
        _ = self._validate_type(test_bank, SupportedBank, "bank") # Validate bank
        self.__bank = bank
        self.__file_name = self._validate_string_not_empty(file_name, "file_name")
        self.__status = self._validate_string_not_empty(status, "status")
        # Validate list of UUIDs
        self._validate_type(transaction_ids, list, "transaction_ids")
        for tid in transaction_ids:
            self._validate_uuid(tid, "transaction_id in list")
        self.__transaction_ids = transaction_ids
        self.__user = self._validate_not_none(user, "user")

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
        self._validate_uuid(transaction_id, "transaction_id")
        self.__transaction_ids.append(transaction_id)
