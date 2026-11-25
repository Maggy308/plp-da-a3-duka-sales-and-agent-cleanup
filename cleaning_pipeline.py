"""Reusable cleaning pipeline for agent transactions."""
import pandas as pd


def clean_agent_data(txns: pd.DataFrame, agents: pd.DataFrame):
    """Return (clean_df, log) after cleaning and enriching transactions.

    Duplicate txn_id values: retain first. Standardise transaction labels.
    Coerce amounts to numeric and impute missing values with transaction-type
    medians (overall median fallback). Flag IQR outliers but retain them.
    Parse ISO and day/month/year dates to ISO format. Left-join agent county;
    preserve unmatched transactions and label their county Unknown.
    """
    df = txns.copy()
    log_rows = []

    def record(issue, dimension, column, count):
        log_rows.append({"issue": issue, "dimension": dimension,
                         "column": column, "rows affected": int(count)})

    duplicate_mask = df.duplicated(subset=["txn_id"], keep="first")
    record("Duplicate transaction IDs removed (keep first)", "Uniqueness",
           "txn_id", duplicate_mask.sum())
    df = df.loc[~duplicate_mask].copy()

    df["txn_type"] = df["txn_type"].astype("string").str.strip().str.casefold().map(
        {"deposit": "Deposit", "withdrawal": "Withdrawal"})
    record("Missing or unrecognised transaction type", "Validity",
           "txn_type", df["txn_type"].isna().sum())

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    missing = df["amount"].isna()
    record("Missing or non-numeric amounts", "Completeness", "amount", missing.sum())
    df["amount_imputed"] = missing
    medians = df.groupby("txn_type")["amount"].median()
    for txn_type, median in medians.items():
        mask = df["amount"].isna() & (df["txn_type"] == txn_type)
        df.loc[mask, "amount"] = median
    df["amount"] = df["amount"].fillna(df["amount"].median())

    q1, q3 = df["amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    df["is_outlier"] = (df["amount"] < q1 - 1.5 * iqr) | (df["amount"] > q3 + 1.5 * iqr)
    record("Amounts outside 1.5×IQR bounds flagged and retained",
           "Accuracy", "amount", df["is_outlier"].sum())

    raw_dates = df["txn_date"].astype("string")
    iso_mask = raw_dates.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False)
    parsed = pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")
    parsed.loc[iso_mask] = pd.to_datetime(raw_dates.loc[iso_mask], format="%Y-%m-%d", errors="coerce")
    parsed.loc[~iso_mask] = pd.to_datetime(raw_dates.loc[~iso_mask], format="%d/%m/%Y", errors="coerce")
    record("Unparseable transaction dates", "Validity", "txn_date", parsed.isna().sum())
    df["txn_date"] = parsed.dt.strftime("%Y-%m-%d")

    merged = df.merge(agents[["agent_id", "county"]], on="agent_id",
                      how="left", indicator=True)
    unknown = merged["_merge"].ne("both")
    record("Transactions with agent IDs absent from agent master",
           "Referential Integrity", "agent_id", unknown.sum())
    merged["county"] = merged["county"].fillna("Unknown")
    merged = merged.drop(columns="_merge")
    record("Rows retained after deduplication", "Completeness",
           "transaction rows", len(merged))
    log = pd.DataFrame(log_rows, columns=[
        "issue", "dimension", "column", "rows affected"])
    return merged, log
