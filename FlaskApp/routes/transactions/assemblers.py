import pandas as pd


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

        if any(keyword.lower() in type_val for keyword in ['Visa', 'Transfer']):
            parts = [row.get('code'), row.get('particulars'), row.get('reference'), '\n', row.get('details')]
        else:
            parts = [row.get('details'), row.get('code'), row.get('particulars'), row.get('reference')]
        desc = join_with_space(parts)
        return desc.strip() if desc else None

    # Format columns
    # Description: For Visa and Transfer transactions, use code as the primary description. For all other transactions, use details as the primary description. In both cases, merge particulars, code, and reference into the description if they are not empty.
    df["description"] = df.apply(merge_description, axis=1)
    df = df.drop(columns=['code', 'particulars', 'reference', 'details'])

    # Date: Convert from DD/MM/YYYY to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

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

    # Format columns
    # Description: Merge memo_description, TP details, and OP details into a single description field. Only include non-empty values.
    df['description'] = df.apply(merge_description, axis=1)
    df = df.drop(
        columns=['memo_description', 'tp_part', 'tp_code', 'tp_ref', 'op_ref', 'op_part', 'op_code', 'OP name'])

    # Date: Convert from DD/MM/YYYY to datetime
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce').dt.strftime('%Y-%m-%d')

    return df
