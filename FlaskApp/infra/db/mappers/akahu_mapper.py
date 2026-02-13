from FlaskApp.domainmodel import AkahuAccount, AkahuCategory, AkahuMerchant, AkahuTransaction, \
    User, Merchant
from FlaskApp.infra.db.mappers.account_mapper import account_orm_to_domain
from FlaskApp.infra.db.mappers.transaction_mapper import transaction_orm_to_domain
from FlaskApp.infra.db.mappers.merchant_mapper import merchant_orm_to_domain
from FlaskApp.infra.db.orm import AkahuAccountORM, AkahuTransactionORM, AkahuMerchantORM, AkahuCategoryORM


def akahu_transaction_orm_to_domain(
        tx: AkahuTransactionORM,
        user: User,
) -> AkahuTransaction:
    return AkahuTransaction(
        akahu_transaction_id=tx.id,
        created=tx.created,
        updated=tx.updated,
        meta=tx.meta,

        user=user,
        transaction=transaction_orm_to_domain(tx.transaction, user=user),
        akahu_account=akahu_account_orm_to_domain(tx.akahu_account, user=user),
        akahu_category=akahu_category_orm_to_domain(tx.akahu_category, user=user) if tx.akahu_category else None,
        akahu_merchant=akahu_merchant_orm_to_domain(tx.akahu_merchant) if tx.akahu_merchant else None,
    )


def akahu_transaction_domain_to_orm(
        tx: AkahuTransaction,
) -> AkahuTransactionORM:
    return AkahuTransactionORM(
        id=tx.id,
        created=tx.created,
        updated=tx.updated,
        meta=tx.meta,
        user_id=tx.user.id,
        transaction_id=tx.transaction.id,
        akahu_account_id=tx.akahu_account.id,
        akahu_category_id=tx.akahu_category.id if tx.akahu_category else None,
        akahu_merchant_id=tx.akahu_merchant.id if tx.akahu_merchant else None,
    )


def akahu_category_orm_to_domain(
        tx: AkahuCategoryORM
) -> AkahuCategory:
    return AkahuCategory(
        nzfcc_id=tx.id,
        nzfcc_name=tx.name,
        groups=tx.groups,
    )


def akahu_category_domain_to_orm(
        tx: AkahuCategory,
) -> AkahuCategoryORM:
    return AkahuCategoryORM(
        id=tx.id,
        name=tx.name,
        groups=tx.groups,
    )


def akahu_account_orm_to_domain(
        tx: AkahuAccountORM,
        user: User
) -> AkahuAccount:
    return AkahuAccount(
        akahu_account_id=tx.id,
        authorisation=tx.authorisation,
        meta=tx.meta,
        connection_id=tx.connection_id,
        connection_name=tx.connection_name,
        connection_logo=tx.connection_logo,
        connection_type=tx.connection_type,
        refreshed=tx.refreshed,
        refresh_attempt=tx.refresh_attempt,
        user=user,
        account=account_orm_to_domain(tx.account, user=user),
    )


def akahu_account_domain_to_orm(
        tx: AkahuAccount,
) -> AkahuAccountORM:
    return AkahuAccountORM(
        id=tx.id,
        authorisation=tx.authorisation,
        meta=tx.meta,
        connection_id=tx.connection_id,
        connection_name=tx.connection_name,
        connection_logo=tx.connection_logo,
        connection_type=tx.connection_type,
        refreshed=tx.refreshed,
        refresh_attempt=tx.refresh_attempt,
        user_id=tx.user.id,
        account_id=tx.account.id,
    )


def akahu_merchant_orm_to_domain(
        tx: AkahuMerchantORM
) -> AkahuMerchant:
    return AkahuMerchant(
        akahu_merchant_id=tx.id,
        nzbn=tx.nzbn,
        name=tx.name,
        website=tx.website,
        logo=tx.logo,
    )


def akahu_merchant_domain_to_orm(
        tx: AkahuMerchant
) -> AkahuMerchantORM:
    return AkahuMerchantORM(
        id=tx.id,
        nzbn=tx.nzbn,
        name=tx.name,
        website=tx.website,
        logo=tx.logo,
    )
