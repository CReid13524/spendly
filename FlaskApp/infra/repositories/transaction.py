from uuid import UUID

from sqlalchemy.orm import Session

from FlaskApp.domainmodel import Transaction, User
from FlaskApp.infra.db.mappers import transaction_orm_to_domain, transaction_domain_to_orm, user_orm_to_domain
from FlaskApp.infra.db.orm import TransactionORM, MerchantORM


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, transaction: Transaction):
        orm = transaction_domain_to_orm(transaction)
        self.session.add(orm)

    def get(self, transaction_id: str | UUID, user: User) -> Transaction | None:
        if isinstance(transaction_id, str):
            transaction_id = UUID(transaction_id)
        orm = self.session.query(TransactionORM).filter_by(id=transaction_id, user_id=user.id).first()
        if orm is None:
            return None
        user = user_orm_to_domain(orm.account.user)
        return transaction_orm_to_domain(orm, user=user)

    def exists(self, transaction_id: str | UUID, user: User) -> bool:
        if isinstance(transaction_id, str):
            transaction_id = UUID(transaction_id)
        return self.session.query(TransactionORM).filter_by(id=transaction_id, user_id=user.id).first() is not None

    def add_or_update(self, transaction: Transaction, user: User):
        existing = self.session.query(TransactionORM).filter_by(id=transaction.id, user_id=user.id).first()
        if existing:
            # Update existing fields
            existing.amount = transaction.amount
            existing.date = transaction.date
            existing.description = transaction.description
            existing.balance = transaction.balance
            existing.type = transaction.type
            existing.status = transaction.status
            existing.pending = transaction.pending
            existing.latitude = transaction.latitude
            existing.longitude = transaction.longitude
            existing.account_id = transaction.account.id
            existing.category_id = transaction.category.id if transaction.category else None
            existing.merchant_id = transaction.merchant.id if transaction.merchant else None
        else:
            orm = transaction_domain_to_orm(transaction)
            self.session.add(orm)

    def get_with_filters(self, user, **filters):
        query = self.session.query(TransactionORM).join(TransactionORM.account).filter_by(user_id=user.id)
        # Apply filters
        if 'start_date' in filters:
            query = query.filter(TransactionORM.date >= filters['start_date'])
        if 'end_date' in filters:
            query = query.filter(TransactionORM.date <= filters['end_date'])
        if 'search' in filters:
            from sqlalchemy import or_, func, case, literal_column
            search_val = filters['search']
            if search_val:
                words = [w.strip() for w in search_val.split() if w.strip()]
                if words:
                    query = query.outerjoin(MerchantORM, TransactionORM.merchant_id == MerchantORM.id)
                    # Build score: sum of matches in description or merchant name
                    score_cases = []
                    for word in words:
                        word_like_any = f"%{word}%"
                        word_like_start = f"{word}%"
                        # Prefer start-of-word matches (score 2), fallback to anywhere (score 1)
                        # Description field
                        score_cases.append(
                            case((TransactionORM.description.ilike(word_like_start), 2),
                                 else_=case((TransactionORM.description.ilike(word_like_any), 1), else_=0))
                        )
                        # Merchant name field
                        score_cases.append(
                            case((MerchantORM.name.ilike(word_like_start), 2),
                                 else_=case((MerchantORM.name.ilike(word_like_any), 1), else_=0))
                        )
                    score_expr = sum(score_cases)
                    query = query.add_columns(score_expr.label('match_score'))
                    query = query.filter(score_expr > 0)
                    query = query.order_by(literal_column('match_score').desc())
        if 'type' in filters:
            query = query.filter(TransactionORM.type.ilike(f"%{filters['type']}%"))
        if 'pending' in filters:
            if filters['pending'] == True:
                query = query.filter(TransactionORM.pending.is_(True))
            elif filters['pending'] == False:
                query = query.filter(TransactionORM.pending.is_(False))
        if 'status' in filters:
            query = query.filter(TransactionORM.status.ilike(f"{filters['status']}"))
        if 'category_id' in filters:
            if filters['category_id'] == True:
                query = query.filter(TransactionORM.category_id != None)
            elif filters['category_id'] == False:
                query = query.filter(TransactionORM.category_id == None)
            else:
                category_id = filters['category_id']
                if isinstance(category_id, str):
                    category_id = UUID(category_id)
                query = query.filter(TransactionORM.category_id == category_id)
        if 'account_id' in filters:
            account_id = filters['account_id']
            if isinstance(account_id, str):
                account_id = UUID(account_id)
            query = query.filter(TransactionORM.account_id == account_id)
        if 'merchant_id' in filters:
            if filters['merchant_id'] == True:
                query = query.filter(TransactionORM.merchant_id != None)
            elif filters['merchant_id'] == False:
                query = query.filter(TransactionORM.merchant_id == None)
            else:
                merchant_id = filters['merchant_id']
                if isinstance(merchant_id, str):
                    merchant_id = UUID(merchant_id)
                query = query.filter(TransactionORM.merchant_id == merchant_id)
        if 'start_amount' in filters:
            query = query.filter(TransactionORM.amount >= filters['start_amount'])
        if 'end_amount' in filters:
            query = query.filter(TransactionORM.amount <= filters['end_amount'])
        if 'start_lat' in filters:
            if filters['start_lat'] == True:
                query = query.filter(TransactionORM.latitude != None)
            elif filters['start_lat'] == False:
                query = query.filter(TransactionORM.latitude == None)
            else:
                if 'end_lat' not in filters:
                    query = query.filter(TransactionORM.latitude == filters['start_lat'])
                else:
                    query = query.filter(TransactionORM.latitude >= filters['start_lat'])
        if 'end_lat' in filters:
            query = query.filter(TransactionORM.latitude <= filters['end_lat'])
        if 'start_lng' in filters:
            if filters['start_lng'] == True:
                query = query.filter(TransactionORM.longitude != None)
            elif filters['start_lng'] == False:
                query = query.filter(TransactionORM.longitude == None)
            else:
                if 'end_lng' not in filters:
                    query = query.filter(TransactionORM.longitude == filters['start_lng'])
                else:
                    query = query.filter(TransactionORM.longitude >= filters['start_lng'])

        if 'end_lng' in filters:
            query = query.filter(TransactionORM.longitude <= filters['end_lng'])

        # Sorting
        if 'sort' in filters:
            sort_field = filters['sort']
            desc = False
            if sort_field.startswith('-'):
                desc = True
                sort_field = sort_field[1:]
            sort_attr = getattr(TransactionORM, sort_field)
            if desc:
                sort_attr = sort_attr.desc()
            query = query.order_by(sort_attr)

        query = query.order_by(TransactionORM.pending.desc())  # Always show pending transactions first

        # Pagination
        page = int(filters['page'])
        per_page = int(filters['per_page'])
        query = query.offset((page - 1) * per_page).limit(per_page)

        results = query.all()
        # If search was used, results are (orm, score); otherwise, just orm
        if 'search' in filters:
            return [transaction_orm_to_domain(orm, user=user) for orm, _ in results]
        else:
            return [transaction_orm_to_domain(orm, user=user) for orm in results]

    def delete(self, transaction_id: str | UUID, user: User):
        if isinstance(transaction_id, str):
            transaction_id = UUID(transaction_id)
        orm = self.session.query(TransactionORM).filter_by(id=transaction_id, user_id=user.id).first()
        if not orm:
            raise Exception("Transaction not found")
        orm.status = 'deleted'
