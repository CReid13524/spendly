from FlaskApp.domainmodel import Upload, User
from FlaskApp.infra.db.orm.upload import UploadORM


def upload_orm_to_domain(
        tx: UploadORM,
        user: User
) -> Upload:
    return Upload(
        upload_id=tx.id,
        created=tx.created,
        file_name=tx.file_name,
        bank=tx.bank,
        transaction_ids=[k.transaction_id for k in tx.upload_transactions],
        status=tx.status,

        user=user,
    )


def upload_domain_to_orm(
        tx: Upload,
) -> UploadORM:
    return UploadORM(
        id=tx.id,
        bank=tx.bank,
        created=tx.created,
        file_name=tx.file_name,
        user_id=tx.user.id,
        status=tx.status
    )
