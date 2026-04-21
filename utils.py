def validate_stock_code(stock_code):
    """校验并标准化 A 股 6 位股票代码。"""
    if stock_code is None:
        return None

    normalized_code = str(stock_code).strip()
    if len(normalized_code) != 6:
        return None

    if not normalized_code.isdigit():
        return None

    if not normalized_code.startswith(("0", "2", "3", "5", "6", "9")):
        return None

    return normalized_code


def format_price(price):
    """将价格格式化为保留两位小数的字符串。"""
    try:
        return f"{float(price):.2f}"
    except (TypeError, ValueError):
        return "--"
