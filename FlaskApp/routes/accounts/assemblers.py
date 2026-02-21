from decimal import Decimal
import pandas as pd

from FlaskApp.domainmodel.transaction import TransactionType
from FlaskApp.infra.services import to_amount_cents


def upload_csv_anz(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: Keep ForeignCurrencyAmount and ConversionCharge
    df.drop(columns=['ForeignCurrencyAmount', 'ConversionCharge'], inplace=True)

    df.rename(columns={
        'Type': 'type',
        'Details': 'details',  # Merge into description
        'Particulars': 'particulars',  # Merge into description
        'Code': 'code',  # Merge into description
        'Reference': 'reference',  # Merge into description
        'Amount': 'amount',
        'Date': 'date'
    }, inplace=True)

    def merge_description(row: pd.Series) -> str | None:
        import numpy as np
        type_val = str(row.get('type', '')).lower()

        def is_valid(val):
            return val is not None and not pd.isna(val) and (not isinstance(val, float) or not np.isnan(val)) and str(
                val).strip() != ''

        def join_with_space(parts):
            result = []
            for p in parts:
                if p == '\n':
                    result.append('\n')
                elif is_valid(p):
                    result.append(str(p))
            # Build string, preserving newlines between valid values
            out = ''
            for i, val in enumerate(result):
                if val == '\n':
                    out = out.rstrip() + '\n'
                else:
                    if out and out[-1] != '\n':
                        out += ' '
                    out += val
            return out

        if any(keyword.lower() in type_val for keyword in ['visa', 'transfer']):
            parts = [row.get('code'), row.get('particulars'), row.get('reference'), '\n', row.get('details')]
        else:
            parts = [row.get('details'), row.get('code'), row.get('particulars'), row.get('reference')]
        desc = join_with_space(parts)
        return desc.strip() if desc else None

    def convert_type(row: pd.Series) -> str | None:
        type = row.get('type').lower()

        match type:
            case 'visa purchase': return TransactionType.CREDIT_CARD.value
            # case 'visa refund': return TransactionType.CREDIT.value
            case 'transfer': return TransactionType.TRANSFER.value
            case 'payment': return TransactionType.PAYMENT.value if row.get('amount', 0) < 0 else TransactionType.CREDIT.value
            case 'salary': return TransactionType.CREDIT.value
            case 'eftpos': return TransactionType.EFTPOS.value
            case 'direct credit': return TransactionType.DIRECT_CREDIT.value
            case 'direct debit': return TransactionType.DIRECT_DEBIT.value
            case 'bill payment': return TransactionType.PAYMENT.value
            case _ if 'atm' in type: return TransactionType.ATM.value
            case _ if 'tax' in type: return TransactionType.TAX.value
            case _ if 'interest' in type: return TransactionType.INTEREST.value
            case _ if 'fee' in type: return TransactionType.FEE.value
            case _ if 'loan' in type: return TransactionType.LOAN.value
            case _ if 'auto' in type: return TransactionType.STANDING_ORDER.value

            case _ if row.get('amount', 0) <= 0: return TransactionType.DEBIT.value
            case _ if row.get('amount', 0) > 0: return TransactionType.CREDIT.value
            case _: return TransactionType.PAYMENT.value


    # Description: For Visa and Transfer transactions, use code as the primary description. For all other transactions, use details as the primary description. In both cases, merge particulars, code, and reference into the description if they are not empty.
    df["description"] = df.apply(merge_description, axis=1)
    df = df.drop(columns=['code', 'particulars', 'reference', 'details'])

    # Date: Convert from DD/MM/YYYY to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

    # Amount: Convert from dollars to cents
    df['amount'] = df['amount'].apply(lambda x: to_amount_cents(x) if pd.notnull(x) else None)

    # Type: Convert to our types
    df['type'] = df.apply(convert_type, axis=1)

    return df


def upload_csv_kiwibank(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: Better format incoming data
    # Note: Split 'Memo/Description' column on semicolon for 'details' and 'code'
    df = df.drop(columns=['Account number', 'OP Bank Account Number', 'Amount (credit)', 'Amount (debit)'])

    df.rename(columns={
        'Source Code (payment type)': 'type',
        'Memo/Description': 'memo_description',
        'TP part': 'tp_part',
        'TP code': 'tp_code',
        'TP ref': 'tp_ref',
        'OP ref': 'op_ref',
        'OP part': 'op_part',
        'OP code': 'op_code',
        'Amount': 'amount',
        'Date': 'date',
        'Balance': 'balance'
    }, inplace=True)

    def merge_description(row: pd.Series) -> str | None:
        import numpy as np
        def is_valid(val):
            return val is not None and not pd.isna(val) and (not isinstance(val, float) or not np.isnan(val)) and str(
                val).strip() != ''

        memo = row.get('memo_description')
        memo_part = ' '.join([x.strip() for x in memo.split(';')]).strip() if is_valid(memo) else ''
        tp_parts = [row.get('tp_part'), row.get('tp_code'), row.get('tp_ref')]
        tp_valid = [str(x) for x in tp_parts if is_valid(x)]
        op_parts = [row.get('op_ref'), row.get('op_part'), row.get('op_code')]
        op_valid = [str(x) for x in op_parts if is_valid(x)]
        desc_lines = []
        if memo_part:
            desc_lines.append(memo_part)
        if tp_valid:
            desc_lines.append(f"TP: ({', '.join(tp_valid)})")
        if op_valid:
            desc_lines.append(f"OP: ({', '.join(op_valid)})")
        return '\n'.join(desc_lines) if desc_lines else None

    def convert_type(row: pd.Series) -> str | None:
        type = row.get('type').lower()

        match type:

            case 'dd': return TransactionType.DIRECT_CREDIT.value
            case 'dc': return TransactionType.DIRECT_DEBIT.value
            case _ if row['memo_description'][:2].lower() == 'ap': return TransactionType.STANDING_ORDER.value
            case _ if row['memo_description'][:3].lower() == 'pos': return TransactionType.EFTPOS.value

            case _ if row.get('amount', 0) <= 0: return TransactionType.PAYMENT.value
            case _ if row.get('amount', 0) > 0: return TransactionType.CREDIT.value
            case _: return TransactionType.PAYMENT.value

    # Type: Map Kiwibank source codes to our transaction types.
    df['type'] = df.apply(convert_type, axis=1)

    # Description: Merge memo_description, TP details, and OP details into a single description field. Only include non-empty values.
    df['description'] = df.apply(merge_description, axis=1)
    df = df.drop(
        columns=['memo_description', 'tp_part', 'tp_code', 'tp_ref', 'op_ref', 'op_part', 'op_code', 'OP name'])

    # Date: Convert from DD/MM/YYYY to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

    # Amount: Convert from dollars to cents
    df['amount'] = df['amount'].apply(lambda x: to_amount_cents(x) if pd.notnull(x) else None)

    # Balance: Convert from dollars to cents
    df['balance'] = df['balance'].apply(lambda x: to_amount_cents(x) if pd.notnull(x) else None)

    return df
