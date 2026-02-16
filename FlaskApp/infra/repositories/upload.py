from uuid import UUID

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Upload, User
from FlaskApp.infra.db.mappers import upload_orm_to_domain, upload_domain_to_orm
from FlaskApp.infra.db.mappers.user_mapper import user_orm_to_domain
from FlaskApp.infra.db.orm import UploadORM, TransactionORM, UploadTransactionORM


class UploadRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, upload: Upload):
        orm = upload_domain_to_orm(upload)
        self.session.add(orm)

        for tx in [UploadTransactionORM(transaction_id=tx_id, upload_id=upload.id) for tx_id in upload.transaction_ids]:
            self.session.add(tx)

    def get(self, upload_id: str | UUID, user: User) -> Upload | None:
        if isinstance(upload_id, str):
            upload_id = UUID(upload_id)
        orm = self.session.query(UploadORM).filter_by(id=upload_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.user)
        return upload_orm_to_domain(orm, user=user)

    def list_uploads(self, user: User) -> list[Upload]:
        orms = self.session.query(UploadORM).filter_by(user_id=user.id).all()
        user = user_orm_to_domain(orms[0].user) if orms else user
        return [upload_orm_to_domain(orm, user=user) for orm in orms]

    def exists(self, upload_id: str | UUID, user: User) -> bool:
        if isinstance(upload_id, str):
            upload_id = UUID(upload_id)
        return self.session.query(UploadORM).filter_by(id=upload_id, user_id=user.id).first() is not None

    def delete(self, upload_id: str | UUID, user: User):
        if isinstance(upload_id, str):
            upload_id = UUID(upload_id)
        orm = self.session.query(UploadORM).filter_by(id=upload_id, user_id=user.id).first()
        if not orm:
            raise Exception("Upload not found")
        orm.status = 'deleted'

        for tx in self.session.query(TransactionORM).filter(TransactionORM.id.in_([tx.transaction_id for tx in
                                                                                   self.session.query(
                                                                                       UploadTransactionORM).filter_by(
                                                                                       upload_id=upload_id).all()])).all():
            tx.status = 'deleted'
