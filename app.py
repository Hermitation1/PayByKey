import pathlib
from contextlib import asynccontextmanager

import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from charts import (
    create_daily_cost_by_model_chart,
    create_daily_cost_by_type_chart,
    create_cost_by_api_key_chart,
    create_cache_hit_rate_chart,
    create_daily_cost_by_api_key_chart,
)
from data_loader import (
    preprocess,
    apply_filters,
    get_total_metrics,
    get_daily_cost_by_model,
    get_daily_cost_by_type,
    get_cost_by_api_key,
    get_daily_cache_hit_rate,
    get_detail_table,
    get_daily_cost_by_api_key,
)

limiter = Limiter(key_func=get_remote_address)
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.limiter = limiter
    app.state.cache = {}
    for file in pathlib.Path("data/").glob("*.csv"):
        try:
            df = pd.read_csv(file)
        except pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError:
            continue

        app.state.cache[file.name] = preprocess(df)

    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc):
    return RedirectResponse("/?error=too_many_requests", status_code=303)


def _get_dashboard_data(request: Request) -> dict:
    """Parse params, load & filter data, compute metrics/charts/detail."""
    file = request.query_params.get("file")
    if file is None:
        if not app.state.cache:
            return {"error": "no data"}
        file = sorted(app.state.cache)[-1]

    if file == "all":
        df = pd.concat(app.state.cache.values(), ignore_index=True)
    else:
        df = app.state.cache[file]
    date_from = request.query_params.get("date_from") or None
    date_to = request.query_params.get("date_to") or None
    models = request.query_params.getlist("models") or None
    api_keys = request.query_params.getlist("api_keys") or None
    types = request.query_params.getlist("types") or None
    page = int(request.query_params.get("page", 1))
    theme = request.query_params.get("theme") or "light"

    files = []
    files.insert(0, ("all", "All Time"))
    for filename in app.state.cache:
        df_cached = app.state.cache[filename]
        min_date = df_cached["utc_date"].min()
        month_label = min_date.strftime("%B %Y")
        files.append((filename, month_label))

    all_models = df["model"].unique().tolist()
    all_api_keys = df["api_key_name"].unique().tolist()
    all_types = df.loc[df["type"] != "request_count", "type"].unique().tolist()

    df = apply_filters(
        df=df,
        date_from=date_from,
        date_to=date_to,
        models=models,
        api_keys=api_keys,
        types=types,
    )

    metrics = get_total_metrics(df=df)
    daily_cost_by_model = get_daily_cost_by_model(df=df)
    daily_cost_by_type = get_daily_cost_by_type(df=df)
    cost_by_api_key = get_cost_by_api_key(df=df)
    daily_cache_hit_rate = get_daily_cache_hit_rate(df=df)
    daily_cost_by_api_key = get_daily_cost_by_api_key(df=df)

    daily_cost_by_model_chart = create_daily_cost_by_model_chart(
        daily_cost_by_model, theme=theme
    )
    daily_cost_by_type_chart = create_daily_cost_by_type_chart(
        daily_cost_by_type, theme=theme
    )
    cost_by_api_key_chart = create_cost_by_api_key_chart(
        cost_by_api_key.sort_values("cost", ascending=True), theme=theme
    )
    daily_cache_hit_rate_chart = create_cache_hit_rate_chart(
        daily_cache_hit_rate, theme=theme
    )
    daily_cost_by_api_key_chart = create_daily_cost_by_api_key_chart(
        daily_cost_by_api_key, theme=theme
    )

    detail_page, total_rows = get_detail_table(df=df, page=page, per_page=50)
    total_pages = (total_rows + 50 - 1) // 50

    detail_html = templates.get_template("detail_partial.html").render(
        detail_page=detail_page,
        total_rows=total_rows,
        total_pages=total_pages,
        current_page=page,
    )

    return {
        "file": file,
        "date_from": date_from,
        "date_to": date_to,
        "models": models,
        "api_keys": api_keys,
        "types": types,
        "page": page,
        "files": files,
        "all_models": all_models,
        "all_api_keys": all_api_keys,
        "all_types": all_types,
        "metrics": metrics,
        "daily_cost_by_api_key_chart": daily_cost_by_api_key_chart,
        "daily_cost_by_model_chart": daily_cost_by_model_chart,
        "daily_cost_by_type_chart": daily_cost_by_type_chart,
        "cost_by_api_key_chart": cost_by_api_key_chart,
        "daily_cache_hit_rate_chart": daily_cache_hit_rate_chart,
        "detail_page": detail_page,
        "total_rows": total_rows,
        "total_pages": total_pages,
        "detail_html": detail_html,
    }


@app.get("/")
async def dashboard(request: Request):
    d = _get_dashboard_data(request)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            **d,
            "selected_file": d["file"],
            "selected_date_from": d["date_from"] or "",
            "selected_date_to": d["date_to"] or "",
            "selected_models": d["models"] or [],
            "selected_types": d["types"] or [],
            "selected_api_keys": d["api_keys"] or [],
            "total_rows": d["total_rows"],
            "total_pages": d["total_pages"],
            "current_page": d["page"],
        },
    )


@app.get("/api/dashboard")
async def api_dashboard(request: Request):
    d = _get_dashboard_data(request)
    m = d["metrics"]
    return {
        "kpi": {
            "total_cost": round(m["total_cost"], 2),
            "total_requests": m["total_requests"],
            "total_tokens": m["total_tokens"],
            "cache_hit_rate": round(m["cache_hit_rate"], 1)
            if m["cache_hit_rate"] is not None
            else None,
        },
        "charts": {
            "cost_by_api_key_daily": d["daily_cost_by_api_key_chart"],
            "cost_by_model": d["daily_cost_by_model_chart"],
            "cost_by_type": d["daily_cost_by_type_chart"],
            "cost_by_api_key": d["cost_by_api_key_chart"],
            "cache_hit_rate": d["daily_cache_hit_rate_chart"],
        },
        "detail_html": d["detail_html"],
    }


@app.post("/upload")
@limiter.limit("5/minute")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    if file.filename.endswith(".csv"):
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:  # 50MB
            return RedirectResponse("/?error=file_too_large", status_code=303)
        csv_name = file.filename
        csv_path = f"data/{csv_name}"
        with open(csv_path, "wb") as f:
            f.write(content)
        try:
            app.state.cache[csv_name] = preprocess(pd.read_csv(csv_path))
        except Exception:
            pathlib.Path(csv_path).unlink(missing_ok=True)
            return RedirectResponse("/?error=invalid_csv", status_code=303)

    else:
        return "Неверный формат файла"

    return RedirectResponse("/", status_code=303)


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
