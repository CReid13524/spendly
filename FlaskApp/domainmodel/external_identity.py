from datetime import datetime
from FlaskApp.domainmodel.base import ValidatingBaseModel


class ExternalIdentity(ValidatingBaseModel):
    def __init__(
            self,
            provider: str,  # 'google', 'apple', 'akahu'
            external_id: str,
            email: str | None,
            name: str | None,
            avatar_url: str | None,
            meta: dict,
            connected_at: datetime,
    ):
        # Validate and assign fields
        self.__provider = self._validate_string_not_empty(provider, "provider")
        self.__external_id = self._validate_string_not_empty(external_id, "external_id")
        self.__email = self._validate_string_not_empty(email, "email", allow_none=True)
        self.__name = self._validate_string_not_empty(name, "name", allow_none=True)
        self.__avatar_url = self._validate_string_not_empty(avatar_url, "avatar_url", allow_none=True)
        self.__meta = self._validate_dict(meta, "meta")
        self.__connected_at = self._validate_datetime(connected_at, "connected_at")

    def __repr__(self):
        return f"<ExternalIdentity: {self.provider}"

    def __eq__(self, other):
        if not isinstance(other, ExternalIdentity):
            return False
        return self.provider == other.provider and self.external_id == other.external_id

    def __hash__(self):
        return hash((self.provider, self.external_id))

    @property
    def provider(self):
        return self.__provider

    @property
    def external_id(self):
        return self.__external_id

    @property
    def email(self):
        return self.__email

    @property
    def name(self):
        return self.__name

    @property
    def avatar_url(self):
        return self.__avatar_url

    @property
    def meta(self):
        return self.__meta

    @property
    def connected_at(self):
        return self.__connected_at

    def add_meta(self, key_value_pair: tuple[str, str]):
        key, value = key_value_pair
        self.__meta[key] = value

    def remove_meta(self, key: str):
        if key in self.__meta:
            del self.__meta[key]
