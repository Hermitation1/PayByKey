import pandas as pd
import plotly.express as px


DARK_THEME = dict(
    paper_bgcolor="#1e1e1e",
    plot_bgcolor="#1e1e1e",
    font=dict(family="Inter, sans-serif", size=14, color="#aaa"),
)
DARK_THEME_AXES = dict(gridcolor="#333", zerolinecolor="#555")


def create_daily_cost_by_model_chart(df: pd.DataFrame, theme: str = "light"):
    fig = px.line(df, x="utc_date", y="cost", color="model")
    if theme == "dark":
        fig.update_layout(**DARK_THEME)
        fig.update_yaxes(**DARK_THEME_AXES)
        fig.update_xaxes(**DARK_THEME_AXES)
    else:
        fig.update_layout(
            template="plotly_white", font=dict(family="Inter, sans-serif", size=14)
        )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=16),
        ),
        hovermode="x unified",
        height=400,
    )
    fig.update_traces(line=dict(width=5))
    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_daily_cost_by_type_chart(df: pd.DataFrame, theme: str = "light"):
    fig = px.line(df, x="utc_date", y="cost", color="type")
    if theme == "dark":
        fig.update_layout(**DARK_THEME)
        fig.update_yaxes(**DARK_THEME_AXES)
        fig.update_xaxes(**DARK_THEME_AXES)
    else:
        fig.update_layout(
            template="plotly_white", font=dict(family="Inter, sans-serif", size=14)
        )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=16),
        ),
        hovermode="x unified",
        height=400,
    )
    fig.update_traces(line=dict(width=5))
    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_cost_by_api_key_chart(df: pd.DataFrame, theme: str = "light"):
    fig = px.bar(df, x="cost", y="api_key_name", color="api_key_name", orientation="h")
    if theme == "dark":
        fig.update_layout(**DARK_THEME)
        fig.update_yaxes(**DARK_THEME_AXES)
        fig.update_xaxes(**DARK_THEME_AXES)
    else:
        fig.update_layout(
            template="plotly_white", font=dict(family="Inter, sans-serif", size=14)
        )
    fig.update_yaxes(title=None, showticklabels=False)
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=16),
        ),
        height=400,
    )
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="#222" if theme == "dark" else "#fff",
            font=dict(
                color="#fff" if theme == "dark" else "#111",
                size=12,
                family="Inter, sans-serif",
            ),
            bordercolor="#fff" if theme == "dark" else "#111",
        )
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_cache_hit_rate_chart(df: pd.DataFrame, theme: str = "light"):
    fig = px.line(df, x="utc_date", y="cache_hit_rate")
    if theme == "dark":
        fig.update_layout(**DARK_THEME)
        fig.update_yaxes(**DARK_THEME_AXES)
        fig.update_xaxes(**DARK_THEME_AXES)
    else:
        fig.update_layout(
            template="plotly_white", font=dict(family="Inter, sans-serif", size=14)
        )
    fig.update_layout(
        yaxis=dict(range=[0, 100]),
        margin=dict(l=10, r=10, t=30, b=10),
        hovermode="x unified",
        height=400,
    )
    fig.update_layout(showlegend=False)
    fig.update_traces(line=dict(width=5))
    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_daily_cost_by_api_key_chart(df: pd.DataFrame, theme: str = "light"):
    fig = px.bar(df, x = "utc_date", y = "cost", color = "api_key_name", barmode = "stack",)
    if theme == "dark":
        fig.update_layout(**DARK_THEME)
        fig.update_yaxes(**DARK_THEME_AXES)
        fig.update_xaxes(**DARK_THEME_AXES)
    else:
        fig.update_layout(template="plotly_white", font=dict(family="Inter, sans-serif", size=14))

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=16),
        ),
        hovermode="x unified",
        height=400,
        xaxis_title=None,
        yaxis_title = "Cost (CNY)",
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)