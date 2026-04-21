from datetime import datetime

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _get_symbol(stock_code):
    """根据股票代码生成腾讯行情使用的证券代码。"""
    if stock_code.startswith(("5", "6", "9")):
        return f"sh{stock_code}"
    if stock_code.startswith(("0", "2", "3")):
        return f"sz{stock_code}"
    raise ValueError("暂不支持该股票代码，请输入标准 A 股代码。")


def _build_session():
    """构建不继承系统代理的会话。"""
    session = requests.Session()
    session.trust_env = False
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/135.0.0.0 Safari/537.36"
            )
        }
    )
    return session


def _get_stock_name(symbol, stock_code):
    """获取股票名称，失败时返回代码本身。"""
    session = _build_session()
    url = f"https://qt.gtimg.cn/q={symbol}"

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        text = response.text
        parts = text.split("~")
        if len(parts) > 1 and parts[1].strip():
            return parts[1].strip()
        return stock_code
    except Exception:
        return stock_code
    finally:
        session.close()


def _parse_klines(payload, symbol):
    """解析腾讯前复权日线数据。"""
    data = payload.get("data", {}).get(symbol, {})
    klines = data.get("qfqday") or data.get("day") or []
    if not klines:
        return pd.DataFrame()

    rows = []
    for item in klines:
        if len(item) < 6:
            continue
        rows.append(
            {
                "date": item[0],
                "open": item[1],
                "close": item[2],
                "high": item[3],
                "low": item[4],
                "volume": item[5],
                "amount": 0,
            }
        )
    return pd.DataFrame(rows)


def get_stock_history(stock_code, period_days=250):
    """获取股票最近一段时间的历史行情数据。"""
    symbol = _get_symbol(stock_code)
    session = _build_session()
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {
        "param": f"{symbol},day,,,320,qfq",
        f"r": f"{datetime.now().timestamp():.6f}",
    }

    try:
        response = session.get(url, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise RuntimeError("历史行情数据获取失败，请检查网络环境或稍后重试。") from exc
    finally:
        session.close()

    df = _parse_klines(payload, symbol)
    if df.empty:
        raise ValueError("未获取到该股票的历史行情数据，请检查股票代码是否正确。")

    df["date"] = pd.to_datetime(df["date"])
    numeric_columns = ["open", "close", "high", "low", "volume", "amount"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["date", "close", "volume"]).sort_values("date").reset_index(drop=True)

    if len(df) < 80:
        raise ValueError("历史数据不足，无法完成指标计算，请更换股票代码后重试。")

    stock_name = _get_stock_name(symbol, stock_code)
    final_df = df.tail(period_days).reset_index(drop=True)
    return final_df, stock_name
