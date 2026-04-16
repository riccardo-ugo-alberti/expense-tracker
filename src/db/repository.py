from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.schema import Account, Base, ImportRun, TransactionClean, TransactionRaw


ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        return instance

    def get(self, instance_id: int) -> ModelT | None:
        return self.session.get(self.model, instance_id)

    def list_all(self) -> Sequence[ModelT]:
        return self.session.scalars(select(self.model)).all()

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)


class FinanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.accounts = Repository(session, Account)
        self.import_runs = Repository(session, ImportRun)
        self.transactions_raw = Repository(session, TransactionRaw)
        self.transactions_clean = Repository(session, TransactionClean)

    def create_account(
        self,
        *,
        bank_name: str,
        account_name: str,
        currency: str = "EUR",
        account_type: str | None = None,
        is_active: bool = True,
    ) -> Account:
        account = Account(
            bank_name=bank_name,
            account_name=account_name,
            account_type=account_type,
            currency=currency,
            is_active=is_active,
        )
        return self.accounts.add(account)

    def list_accounts(self) -> Sequence[Account]:
        statement = select(Account).order_by(Account.bank_name, Account.account_name)
        return self.session.scalars(statement).all()

    def get_account(self, account_id: int) -> Account | None:
        return self.accounts.get(account_id)

    def create_import_run(
        self,
        *,
        account_id: int,
        file_name: str,
        file_type: str,
        row_count: int,
        status: str = "previewed",
    ) -> ImportRun:
        import_run = ImportRun(
            account_id=account_id,
            file_name=file_name,
            file_type=file_type,
            row_count=row_count,
            status=status,
        )
        return self.import_runs.add(import_run)

    def list_import_runs(self, account_id: int | None = None) -> Sequence[ImportRun]:
        statement = select(ImportRun).order_by(ImportRun.imported_at.desc(), ImportRun.id.desc())
        if account_id is not None:
            statement = statement.where(ImportRun.account_id == account_id)
        return self.session.scalars(statement).all()

    def add_raw_transaction(self, transaction: TransactionRaw) -> TransactionRaw:
        return self.transactions_raw.add(transaction)

    def add_clean_transaction(self, transaction: TransactionClean) -> TransactionClean:
        return self.transactions_clean.add(transaction)
