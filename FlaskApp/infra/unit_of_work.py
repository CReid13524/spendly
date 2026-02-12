from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from FlaskApp.infra.repositories import AccountRepository, TransactionRepository, MerchantRepository, \
    AkahuAccountRepository, AkahuTransactionRepository, AkahuMerchantRepository, AkahuCategoryRepository, UserRepository


class AbstractUnitOfWork(ABC):
    users: UserRepository
    accounts: AccountRepository
    transactions: TransactionRepository
    merchants: MerchantRepository
    akahu_accounts: AkahuAccountRepository
    akahu_transactions: AkahuTransactionRepository
    akahu_merchants: AkahuMerchantRepository
    akahu_categories: AkahuCategoryRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self):
        self.session = self._session_factory()

        # Wire repositories
        self.users = UserRepository(self.session)
        self.accounts = AccountRepository(self.session)
        self.transactions = TransactionRepository(self.session)
        self.merchants = MerchantRepository(self.session)
        self.akahu_accounts = AkahuAccountRepository(self.session)
        self.akahu_transactions = AkahuTransactionRepository(self.session)
        self.akahu_merchants = AkahuMerchantRepository(self.session)
        self.akahu_categories = AkahuCategoryRepository(self.session)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
