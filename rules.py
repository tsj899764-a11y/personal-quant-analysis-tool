def _validate_analysis_data(df):
    """校验指标数据是否满足规则判断要求。"""
    if df is None:
        raise ValueError("指标数据不能为空。")

    if df.empty:
        raise ValueError("指标数据为空，无法进行条件判断。")

    required_columns = [
        "close",
        "ma5",
        "ma10",
        "ma20",
        "dif",
        "dea",
        "rsi",
        "volume",
        "volume_ma5",
    ]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"指标数据缺少必要字段：{', '.join(missing_columns)}")

    if len(df) < 2:
        raise ValueError("数据条数不足，至少需要 2 条数据才能判断交叉信号。")


def evaluate_conditions(df):
    """对最新数据执行规则判断。"""
    _validate_analysis_data(df)

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    conditions = {
        "MA5 上穿 MA10": previous["ma5"] <= previous["ma10"] and latest["ma5"] > latest["ma10"],
        "MA5 下穿 MA10": previous["ma5"] >= previous["ma10"] and latest["ma5"] < latest["ma10"],
        "MA5 大于 MA10": latest["ma5"] > latest["ma10"],
        "MA10 大于 MA20": latest["ma10"] > latest["ma20"],
        "当前收盘价站上 MA20": latest["close"] > latest["ma20"],
        "MACD 金叉": previous["dif"] <= previous["dea"] and latest["dif"] > latest["dea"],
        "MACD 死叉": previous["dif"] >= previous["dea"] and latest["dif"] < latest["dea"],
        "当前成交量大于 5 日均量 1.5 倍": latest["volume"] > latest["volume_ma5"] * 1.5,
        "RSI 低于 30": latest["rsi"] < 30,
        "RSI 高于 70": latest["rsi"] > 70,
    }

    return conditions, latest, previous
