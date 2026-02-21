from datetime import datetime
from typing import TYPE_CHECKING, List, Dict, Optional
from FlaskApp.domainmodel.base import ValidatingBaseModel

if TYPE_CHECKING:
    from FlaskApp.domainmodel import Account, User


class AkahuAccount(ValidatingBaseModel):
    def __init__(self,
                 akahu_account_id: str,
                 authorisation: str,
                 meta: Dict,
                 connection_id: str,
                 connection_type: str,
                 refreshed: Dict[str, datetime],
                 refresh_attempt: datetime,

                 account_name: str,
                 account_type: str,
                 formatted_account: str | None,
                 attributes: List[str],
                 currency: str,
                 current_balance: int,
                 available_balance: int | None,
                 status: str,
                 created: datetime,
                 credit_limit: int,
                 overdrawn: bool,
                 connection_name: str,
                 connection_logo: str,

                 user: 'User',
                 account: 'Account',
                ):
        # Validate and assign immutable fields directly
        self.__id = self._validate_string_not_empty(akahu_account_id, "akahu_account_id")
        self.__user = self._validate_not_none(user, "user") # Simple check as it's a domain object
        self.__account = self._validate_not_none(account, "account")
        self.__created = self._validate_datetime(created, "created")

        # Assign mutable fields via setters for validation
        self.authorisation = authorisation
        self.meta = meta
        self.connection_id = connection_id
        self.connection_type = connection_type
        self.refreshed = refreshed
        self.refresh_attempt = refresh_attempt

        self.name = account_name
        self.type = account_type
        self.formatted_account = formatted_account
        self.attributes = attributes
        self.currency = currency
        self.current_balance = current_balance
        self.available_balance = available_balance
        self.status = status
        self.credit_limit = credit_limit
        self.overdrawn = overdrawn
        self.connection_name = connection_name
        self.connection_logo = connection_logo

    def __repr__(self):
        return f"AkahuAccount: {self.account}"

    def __eq__(self, other):
        if not isinstance(other, AkahuAccount):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @property
    def id(self):
        return self.__id

    @property
    def authorisation(self):
        return self.__authorisation

    @authorisation.setter
    def authorisation(self, value):
        self.__authorisation = self._validate_string_not_empty(value, "authorisation")

    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self, value):
        self.__meta = self._validate_dict(value, "meta")

    @property
    def connection_id(self):
        return self.__connection_id

    @connection_id.setter
    def connection_id(self, value):
        self.__connection_id = self._validate_string_not_empty(value, "connection_id")

    @property
    def connection_type(self):
        return self.__connection_type

    @connection_type.setter
    def connection_type(self, value):
        self.__connection_type = self._validate_string_not_empty(value, "connection_type")

    @property
    def refreshed(self):
        return self.__refreshed

    @refreshed.setter
    def refreshed(self, value):
        self.__refreshed = self._validate_dict(value, "refreshed")

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = self._validate_string_not_empty(value, "name")

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = self._validate_string_not_empty(value, "type")

    @property
    def formatted_account(self):
        return self.__formatted_account

    @formatted_account.setter
    def formatted_account(self, value):
        self.__formatted_account = self._validate_string_not_empty(value, "formatted_account", allow_none=True)

    @property
    def attributes(self):
        return self.__attributes

    @attributes.setter
    def attributes(self, value):
        self.__attributes = self._validate_list_of_strings(value, "attributes")

    @property
    def currency(self):
        return self.__currency

    @currency.setter
    def currency(self, value):
        self.__currency = self._validate_string_not_empty(value, "currency")

    @property
    def current_balance(self):
        return self.__current_balance

    @current_balance.setter
    def current_balance(self, value):
        self.__current_balance = self._validate_type(value, int, "current_balance")

    @property
    def available_balance(self):
        return self.__available_balance

    @available_balance.setter
    def available_balance(self, value):
        self.__available_balance = self._validate_type(value, int, "available_balance", allow_none=True)

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        self.__status = self._validate_string_not_empty(value, "status")

    @property
    def created(self):
        return self.__created

    @property
    def credit_limit(self):
        return self.__credit_limit

    @credit_limit.setter
    def credit_limit(self, value):
        self.__credit_limit = self._validate_type(value, int, "credit_limit")

    @property
    def overdrawn(self):
        return self.__overdrawn

    @overdrawn.setter
    def overdrawn(self, value):
        self.__overdrawn = self._validate_boolean(value, "overdrawn")

    @property
    def refresh_attempt(self):
        return self.__refresh_attempt

    @refresh_attempt.setter
    def refresh_attempt(self, value):
        self.__refresh_attempt = self._validate_datetime(value, "refresh_attempt")

    @property
    def connection_name(self):
        return self.__connection_name

    @connection_name.setter
    def connection_name(self, value):
        self.__connection_name = self._validate_string_not_empty(value, "connection_name")

    @property
    def connection_logo(self):
        return self.__connection_logo

    @connection_logo.setter
    def connection_logo(self, value):
        self.__connection_logo = self._validate_string_not_empty(value, "connection_logo")

    @property
    def user(self):
        return self.__user

    @property
    def account(self):
        return self.__account

