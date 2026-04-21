import streamlit as st

from charts import (
    build_close_chart,
    build_macd_chart,
    build_ma_chart,
    build_volume_chart,
)
from data_fetcher import get_stock_history
from indicators import calculate_indicators
from signal_engine import analyze_stock
from utils import format_price, validate_stock_code


st.set_page_config(
    page_title="个人量化分析工具",
    page_icon="📈",
    layout="wide",
)


def apply_custom_style():
    """注入自定义页面样式。"""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(0, 210, 255, 0.12), transparent 28%),
                radial-gradient(circle at top right, rgba(30, 255, 180, 0.08), transparent 22%),
                linear-gradient(180deg, #07111f 0%, #091523 45%, #060b13 100%);
            color: #e7f4ff;
        }
        .main .block-container {
            max-width: 1360px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        .hero-panel {
            background: linear-gradient(135deg, rgba(8, 22, 41, 0.95), rgba(10, 29, 53, 0.88));
            border: 1px solid rgba(86, 196, 255, 0.28);
            border-radius: 18px;
            padding: 24px 28px;
            box-shadow: 0 0 30px rgba(0, 162, 255, 0.12);
            margin-bottom: 18px;
        }
        .hero-title {
            font-size: 30px;
            font-weight: 700;
            color: #ecf9ff;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }
        .hero-subtitle {
            color: #8fb7d1;
            font-size: 14px;
            line-height: 1.7;
        }
        .metric-card {
            background: linear-gradient(180deg, rgba(11, 24, 43, 0.96), rgba(8, 18, 33, 0.92));
            border: 1px solid rgba(90, 197, 255, 0.18);
            border-radius: 16px;
            padding: 18px 20px;
            min-height: 124px;
            box-shadow: inset 0 0 18px rgba(0, 183, 255, 0.04);
        }
        .metric-label {
            color: #7ea3bc;
            font-size: 13px;
            margin-bottom: 10px;
        }
        .metric-value {
            color: #edfaff;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .metric-desc {
            color: #8cb8c8;
            font-size: 13px;
        }
        .signal-buy {
            color: #1df2a1;
            text-shadow: 0 0 12px rgba(29, 242, 161, 0.25);
        }
        .signal-sell {
            color: #ff6b88;
            text-shadow: 0 0 12px rgba(255, 107, 136, 0.22);
        }
        .signal-watch {
            color: #5fd7ff;
            text-shadow: 0 0 12px rgba(95, 215, 255, 0.22);
        }
        .signal-none {
            color: #b7c5d3;
        }
        .section-card {
            background: linear-gradient(180deg, rgba(8, 19, 35, 0.96), rgba(6, 14, 26, 0.94));
            border: 1px solid rgba(82, 174, 255, 0.16);
            border-radius: 16px;
            padding: 18px 20px;
            margin-bottom: 18px;
        }
        .section-title {
            font-size: 17px;
            font-weight: 700;
            color: #ecf7ff;
            margin-bottom: 12px;
        }
        .reason-text {
            color: #d8ebf6;
            line-height: 1.8;
            font-size: 14px;
        }
        .tag-success {
            background: rgba(29, 242, 161, 0.12);
            border: 1px solid rgba(29, 242, 161, 0.28);
            color: #8ef5cb;
            border-radius: 999px;
            padding: 7px 12px;
            display: inline-block;
            margin: 0 8px 8px 0;
            font-size: 13px;
        }
        .tag-muted {
            background: rgba(102, 129, 153, 0.14);
            border: 1px solid rgba(124, 153, 179, 0.22);
            color: #b8c8d6;
            border-radius: 999px;
            padding: 7px 12px;
            display: inline-block;
            margin: 0 8px 8px 0;
            font-size: 13px;
        }
        .stTextInput > div > div > input {
            background-color: rgba(8, 18, 33, 0.96);
            color: #eef9ff;
            border: 1px solid rgba(99, 196, 255, 0.3);
            border-radius: 10px;
        }
        .stButton > button {
            background: linear-gradient(135deg, #00a9ff, #12d8ff);
            color: #03111d;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            height: 44px;
            width: 100%;
            box-shadow: 0 8px 24px rgba(0, 183, 255, 0.18);
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #18b5ff, #6fe7ff);
            color: #02111d;
        }
        div[data-testid="stMetric"] {
            background: transparent;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    """渲染页面头部。"""
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-title">个人量化分析工具</div>
            <div class="hero-subtitle">
                输入 A 股股票代码，系统将自动拉取最近 250 个交易日历史行情，计算常见技术指标，
                完成规则判断，并给出买入、卖出、观察或无信号结论。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signal_card(result):
    """渲染信号结果卡片。"""
    signal_class_map = {
        "买入信号": "signal-buy",
        "卖出信号": "signal-sell",
        "观察信号": "signal-watch",
        "无信号": "signal-none",
    }
    signal_class = signal_class_map.get(result["signal"], "signal-none")
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">当前信号</div>
            <div class="metric-value {signal_class}">{result["signal"]}</div>
            <div class="metric-desc">系统已根据均线、MACD、RSI 与成交量条件综合判断</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title, value, desc):
    """渲染通用信息卡片。"""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tag_group(title, items, css_class):
    """渲染条件标签列表。"""
    content = "".join([f'<span class="{css_class}">{item}</span>' for item in items])
    if not content:
        content = f'<span class="{css_class}">暂无</span>'

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <div>{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reason(reason_text):
    """渲染信号原因说明。"""
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">信号原因说明</div>
            <div class="reason-text">{reason_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    """应用主函数。"""
    apply_custom_style()
    render_header()

    input_col, button_col = st.columns([3, 1])
    with input_col:
        stock_code = st.text_input(
            "请输入 A 股股票代码",
            value="000001",
            max_chars=6,
            placeholder="例如：600853、000001、002594",
        )
    with button_col:
        st.write("")
        st.write("")
        start_button = st.button("开始分析")

    if start_button:
        normalized_code = validate_stock_code(stock_code)
        if not normalized_code:
            st.error("股票代码格式不正确，请输入 6 位 A 股代码。")
            return

        with st.spinner("正在获取行情数据并计算指标，请稍候..."):
            try:
                raw_df, stock_name = get_stock_history(normalized_code, period_days=250)
                analysis_df = calculate_indicators(raw_df)
                result = analyze_stock(analysis_df, normalized_code, stock_name)
            except Exception as exc:
                st.error(f"分析失败：{exc}")
                return

        overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)
        with overview_col1:
            render_info_card("股票名称", result["stock_name"], "已完成基础信息识别")
        with overview_col2:
            render_info_card("股票代码", result["stock_code"], "当前分析标的")
        with overview_col3:
            render_info_card("当前价格", format_price(result["current_price"]), "最新收盘价")
        with overview_col4:
            render_signal_card(result)

        render_reason(result["reason"])

        conditions_col1, conditions_col2 = st.columns(2)
        with conditions_col1:
            render_tag_group("满足条件列表", result["matched_conditions"], "tag-success")
        with conditions_col2:
            render_tag_group("不满足条件列表", result["unmatched_conditions"], "tag-muted")

        st.markdown('<div class="section-title">行情分析图表</div>', unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(build_close_chart(analysis_df, result["stock_name"], result["stock_code"]), use_container_width=True)
        with chart_col2:
            st.plotly_chart(build_ma_chart(analysis_df, result["stock_name"], result["stock_code"]), use_container_width=True)

        chart_col3, chart_col4 = st.columns(2)
        with chart_col3:
            st.plotly_chart(build_volume_chart(analysis_df, result["stock_name"], result["stock_code"]), use_container_width=True)
        with chart_col4:
            st.plotly_chart(build_macd_chart(analysis_df, result["stock_name"], result["stock_code"]), use_container_width=True)


if __name__ == "__main__":
    main()
