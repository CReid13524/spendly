from FlaskApp.domainmodel import Merchant, User
from FlaskApp.infra.db.orm import MerchantORM


def merchant_orm_to_domain(
        tx: MerchantORM,
        user: User
) -> Merchant:
    return Merchant(
        merchant_id=tx.id,
        nzbn=tx.nzbn,
        name=tx.name,
        website=tx.website,
        logo=tx.logo,

        user=user,
    )


def merchant_domain_to_orm(
        tx: Merchant,
) -> MerchantORM:
    return MerchantORM(
        id=tx.id,
        nzbn=tx.nzbn,
        name=tx.name,
        website=tx.website,
        logo=tx.logo,
        user_id=tx.user.id
    )
