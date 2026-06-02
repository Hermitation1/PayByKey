import pandas as pd

from data_loader import (
    preprocess,
    get_total_metrics,
    get_daily_cache_hit_rate,
    get_detail_table,
)
from data_loader import apply_filters


def test_preprocess(raw_df: pd.DataFrame):
    result = preprocess(raw_df)
    assert pd.api.types.is_datetime64_any_dtype(result["utc_date"])
    assert (result["amount"] > 0).all()
    assert result["amount"].notna().all()
    assert len(result) == 4
    assert "cost" in result.columns
    assert "user_id" not in result.columns
    assert "api_key" not in result.columns


def test_apply_filters_date_from(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, date_from="2026-05-02")
    assert len(result) == 3
    assert (result["utc_date"] >= pd.Timestamp("2026-05-02")).all()


def test_apply_filters_date_to(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, date_to="2026-05-02")
    assert len(result) == 3
    assert (result["utc_date"] <= pd.Timestamp("2026-05-02")).all()


def test_apply_filters_models(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, models=["deepseek-v4-pro"])
    assert len(result) == 3
    assert (result["model"] == "deepseek-v4-pro").all()


def test_apply_filters_api_keys(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, api_keys=["work-api"])
    assert len(result) == 2


def test_apply_filters_types(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, types=["output_tokens"])
    assert len(result) == 1


def test_apply_filters_empty_string_ignored(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, date_from="")
    assert len(result) == 4


def test_apply_filters_empty_list_ignored(clean_df: pd.DataFrame):
    result = apply_filters(clean_df, models=[])
    assert len(result) == 4


def test_get_total_metrics(clean_df: pd.DataFrame):
    m = get_total_metrics(clean_df)
    assert m["total_cost"] == 160.0
    assert m["total_requests"] == 5
    assert m["total_tokens"] == 600
    assert m["cache_hit_rate"] == 40.0
    assert len(m) == 4


def test_get_daily_cache_hit_rate(clean_df: pd.DataFrame):
    result = get_daily_cache_hit_rate(clean_df)
    assert len(result) == 1
    assert list(result.columns) == ["utc_date", "cache_hit_rate"]
    assert result.iloc[0]["cache_hit_rate"] == 40.0


def test_get_daily_cache_hit_rate_no_cache():
    df = pd.DataFrame(
        {
            "utc_date": pd.to_datetime(["2026-05-01", "2026-05-02"]),
            "type": ["output_tokens", "output_tokens"],
            "amount": [100, 200],
        }
    )
    result = get_daily_cache_hit_rate(df)
    assert len(result) == 0


def test_get_daily_cache_hit_rate_only_hit():
    df = pd.DataFrame(
        {
            "utc_date": pd.to_datetime(["2026-05-01"]),
            "type": ["input_cache_hit_tokens"],
            "amount": [100],
        }
    )
    result = get_daily_cache_hit_rate(df)
    assert result.iloc[0]["cache_hit_rate"] == 100.0


def test_get_daily_cache_hit_rate_only_miss():
    df = pd.DataFrame(
        {
            "utc_date": pd.to_datetime(["2026-05-01"]),
            "type": ["input_cache_miss_tokens"],
            "amount": [100],
        }
    )
    result = get_daily_cache_hit_rate(df)
    assert result.iloc[0]["cache_hit_rate"] == 0.0


def test_get_detail_table(clean_df: pd.DataFrame):
    table, _ = get_detail_table(clean_df, per_page=2)
    assert len(table) == 2
    assert (table["type"] != "request_count").all()
    assert table["utc_date"].is_monotonic_decreasing
