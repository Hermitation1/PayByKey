import pandas as pd
import pytest


@pytest.fixture
def raw_df():
    """Before preprocess - like in original CSV."""
    return pd.DataFrame(
        {
            "utc_date": [
                "2026-05-01",
                "2026-05-02",
                "2026-05-02",
                "2026-05-03",
                "2026-05-04",
                "2026-05-05",
            ],
            "model": [
                "deepseek-v4-pro",
                "deepseek-v4-pro",
                "deepseek-v4-pro",
                "deepseek-v4-flash",
                "deepseek-v4-pro",
                "deepseek-v4-flash",
            ],
            "api_key_name": [
                "work-api",
                "ilia-api",
                "ilia-api",
                "work-api",
                "work-api",
                "ilia-api",
            ],
            "type": [
                "output_tokens",
                "input_cache_hit_tokens",
                "input_cache_miss_tokens",
                "request_count",
                "output_tokens",
                "output_tokens",
            ],
            "price": ["0.5", "0.1", "0.3", "", "0.3", "0.2"],
            "amount": ["100", "200", "300", "5", "0", "NaN"],
            "user_id": [1, 2, 3, 4, 5, 6],
            "api_key": ["sk-abc", "sk-def", "sk-ghi", "sk-jkl", "sk-mno", "sk-pqr"],
        }
    )


@pytest.fixture
def clean_df(raw_df):
    """After preprocess — with cost, without user_id/api_key, utc_date -> datetime."""
    from data_loader import preprocess

    return preprocess(raw_df)
