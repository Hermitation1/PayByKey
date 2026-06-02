import pandas as pd


def preprocess(df: pd.DataFrame):
    df["utc_date"] = pd.to_datetime(df["utc_date"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[(df["amount"] > 0) & (df["amount"].notna())]
    df["cost"] = df["price"] * df["amount"]
    df = df.drop(columns=["user_id", "api_key"])
    return df


def apply_filters(
    df: pd.DataFrame,
    date_from: str | None = None,
    date_to: str | None = None,
    models: list[str] | None = None,
    api_keys: list[str] | None = None,
    types: list[str] | None = None,
) -> pd.DataFrame:
    mask: pd.Series = pd.Series(True, index=df.index)

    if date_from:
        mask &= df["utc_date"] >= pd.to_datetime(date_from)

    if date_to:
        mask &= df["utc_date"] <= pd.to_datetime(date_to)

    if models:
        mask &= df["model"].isin(models)

    if api_keys:
        mask &= df["api_key_name"].isin(api_keys)

    if types:
        mask &= df["type"].isin(types)

    df = df[mask]

    return df


def get_total_metrics(df: pd.DataFrame) -> dict:
    total_cost = float(df["cost"].sum())
    total_requests = int(df.query("type == 'request_count'")["amount"].sum())
    total_tokens = int(df.query("type != 'request_count'")["amount"].sum())
    cache_hit = int(df.query("type == 'input_cache_hit_tokens'")["amount"].sum())
    cache_miss = int(df.query("type == 'input_cache_miss_tokens'")["amount"].sum())
    if cache_hit + cache_miss > 0:
        cache_hit_rate = cache_hit / (cache_hit + cache_miss) * 100
    else:
        cache_hit_rate = None

    return {
        "total_cost": total_cost,
        "total_requests": total_requests,
        "total_tokens": total_tokens,
        "cache_hit_rate": cache_hit_rate,
    }


def get_daily_cost_by_model(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["utc_date", "model"], as_index=False)["cost"].sum()  # type: ignore


def get_daily_cost_by_type(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.query("type != 'request_count'")
        .groupby(["utc_date", "type"], as_index=False)["cost"]
        .sum()
    )  # type: ignore


def get_cost_by_api_key(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("api_key_name", as_index=False)["cost"].sum()  # type: ignore


def get_daily_cache_hit_rate(df: pd.DataFrame) -> pd.DataFrame:
    pv = df[
        df["type"].isin(
            [
                "input_cache_hit_tokens",
                "input_cache_miss_tokens",
            ]
        )
    ].pivot_table(
        index="utc_date",
        columns="type",
        values="amount",
        aggfunc="sum",
        fill_value=0,
    )

    for col in ["input_cache_hit_tokens", "input_cache_miss_tokens"]:
        if col not in pv.columns:
            pv[col] = 0

    pv["cache_hit_rate"] = (
        pv["input_cache_hit_tokens"]
        / (pv["input_cache_hit_tokens"] + pv["input_cache_miss_tokens"])
        * 100
    )

    return pv.reset_index()[["utc_date", "cache_hit_rate"]]


def get_detail_table(df: pd.DataFrame, page: int = 1, per_page: int = 50):
    df = df.sort_values("utc_date", ascending=False)
    df = df.query("type != 'request_count'")
    start = (page - 1) * per_page
    end = start + per_page
    lines = len(df)
    return df.iloc[
        start:end
    ], lines  # iloc[start:end] — slice by strings (like LIMIT/OFFSET в SQL)
