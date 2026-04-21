import numpy as np
import pandas as pd


def _validate_input_data(df):
    """校验输入行情数据是否满足指标计算要求。"""
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("输入数据格式不正确，必须为 DataFrame。")

    if df.empty:
        raise ValueError("行情数据为空，无法计算技术指标。")

    required_columns = ["date", "open", "high", "low", "close", "volume"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"行情数据缺少必要字段：{', '.join(missing_columns)}")


def _clean_numeric_data(df):
    """清洗关键数值字段，确保 close 和 volume 可用于计算。"""
    result_df = df.copy()
    result_df["close"] = pd.to_numeric(result_df["close"], errors="coerce")
    result_df["volume"] = pd.to_numeric(result_df["volume"], errors="coerce")

    if result_df["close"].isna().all():
        raise ValueError("close 数据异常，无法计算技术指标。")

    if result_df["volume"].isna().all():
        raise ValueError("volume 数据异常，无法计算技术指标。")

    result_df = result_df.dropna(subset=["close", "volume"]).copy()
    if result_df.empty:
        raise ValueError("清洗后的行情数据为空，无法计算技术指标。")

    return result_df


def calculate_macd(close_series, short_period=12, long_period=26, signal_period=9):
    """计算 MACD 指标。"""
    ema_short = close_series.ewm(span=short_period, adjust=False).mean()
    ema_long = close_series.ewm(span=long_period, adjust=False).mean()
    dif = ema_short - ema_long
    dea = dif.ewm(span=signal_period, adjust=False).mean()
    macd_hist = (dif - dea) * 2
    return dif, dea, macd_hist


def calculate_rsi(close_series, period=14):
    """计算 RSI 指标。"""
    price_diff = close_series.diff()
    up = price_diff.clip(lower=0)
    down = -price_diff.clip(upper=0)

    avg_up = up.ewm(alpha=1 / period, adjust=False).mean()
    avg_down = down.ewm(alpha=1 / period, adjust=False).mean()
    avg_down = avg_down.astype("float64").replace(0, np.nan)
    rs = avg_up / avg_down
    rsi = 100 - (100 / (1 + rs))
    return rsi.astype("float64").fillna(50.0)


def calculate_indicators(df):
    """为行情数据计算常用技术指标。"""
    _validate_input_data(df)
    result_df = _clean_numeric_data(df)

    try:
        result_df = result_df.sort_values("date").reset_index(drop=True)
        result_df["ma5"] = result_df["close"].rolling(window=5).mean()
        result_df["ma10"] = result_df["close"].rolling(window=10).mean()
        result_df["ma20"] = result_df["close"].rolling(window=20).mean()
        result_df["ma60"] = result_df["close"].rolling(window=60).mean()
        result_df["volume_ma5"] = result_df["volume"].rolling(window=5).mean()

        dif, dea, macd_hist = calculate_macd(result_df["close"])
        result_df["dif"] = dif
        result_df["dea"] = dea
        result_df["macd_hist"] = macd_hist
        result_df["rsi"] = calculate_rsi(result_df["close"])
    except Exception as exc:
        raise RuntimeError(f"技术指标计算失败：{exc}") from exc

    result_df = result_df.dropna().reset_index(drop=True)
    if result_df.empty:
        raise ValueError("指标计算结果为空，请稍后重试。")

    return result_df
