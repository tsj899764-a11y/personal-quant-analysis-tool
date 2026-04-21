from rules import evaluate_conditions


def generate_signal(conditions):
    """根据信号规则生成最终结论。"""
    buy_score = 0
    sell_score = 0
    watch_score = 0
    reasons = []

    if conditions["MA5 上穿 MA10"]:
        buy_score += 2
        reasons.append("短期均线形成上穿，趋势有转强迹象")
    if conditions["MACD 金叉"]:
        buy_score += 2
        reasons.append("MACD 出现金叉，动能开始改善")
    if conditions["MA5 大于 MA10"] and conditions["MA10 大于 MA20"]:
        buy_score += 2
        reasons.append("均线结构呈多头排列特征")
    if conditions["当前收盘价站上 MA20"]:
        buy_score += 1
        reasons.append("收盘价位于 MA20 上方，价格强于中期均线")
    if conditions["当前成交量大于 5 日均量 1.5 倍"]:
        buy_score += 1
        reasons.append("成交量明显放大，说明资金关注度提升")
    if conditions["RSI 低于 30"]:
        watch_score += 2
        reasons.append("RSI 处于低位，存在超卖后的修复观察价值")

    if conditions["MA5 下穿 MA10"]:
        sell_score += 2
        reasons.append("短期均线下穿，走势转弱")
    if conditions["MACD 死叉"]:
        sell_score += 2
        reasons.append("MACD 出现死叉，短线回落风险增加")
    if not conditions["当前收盘价站上 MA20"]:
        sell_score += 1
        reasons.append("收盘价未站稳 MA20，中期支撑偏弱")
    if conditions["RSI 高于 70"]:
        sell_score += 2
        reasons.append("RSI 偏高，存在短线过热风险")

    if buy_score >= 5 and sell_score <= 2:
        return "买入信号", "；".join(reasons[:4]) or "多个趋势条件同步转强。"
    if sell_score >= 4:
        return "卖出信号", "；".join(reasons[:4]) or "多个转弱条件同时出现。"
    if watch_score >= 2 or buy_score >= 2:
        return "观察信号", "；".join(reasons[:4]) or "部分条件改善，建议继续观察。"
    return "无信号", "当前关键条件未形成明显共振，建议继续等待。"


def analyze_stock(df, stock_code, stock_name):
    """对股票进行完整分析并输出结构化结果。"""
    conditions, latest, _ = evaluate_conditions(df)
    signal, reason = generate_signal(conditions)

    matched_conditions = [name for name, matched in conditions.items() if matched]
    unmatched_conditions = [name for name, matched in conditions.items() if not matched]

    if not matched_conditions:
        matched_conditions = ["当前暂无明显满足条件"]

    return {
        "stock_name": stock_name,
        "stock_code": stock_code,
        "current_price": float(latest["close"]),
        "signal": signal,
        "reason": reason,
        "matched_conditions": matched_conditions,
        "unmatched_conditions": unmatched_conditions,
    }
