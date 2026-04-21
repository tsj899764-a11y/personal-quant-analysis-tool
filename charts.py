import plotly.graph_objects as go


def _validate_chart_data(df, required_columns):
    """校验图表绘制所需数据。"""
    if df is None:
        raise ValueError("图表数据不能为空。")

    if df.empty:
        raise ValueError("图表数据为空，无法绘制。")

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"图表数据缺少必要字段：{', '.join(missing_columns)}")


def _apply_dark_layout(fig, title_text, yaxis_title):
    """统一设置深色科技风图表样式。"""
    fig.update_layout(
        title={
            "text": title_text,
            "x": 0.02,
            "xanchor": "left",
            "font": {"size": 18, "color": "#eef9ff"},
        },
        template="plotly_dark",
        paper_bgcolor="#07101c",
        plot_bgcolor="#07101c",
        font={"color": "#d8eeff", "size": 12},
        margin={"l": 24, "r": 24, "t": 58, "b": 32},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "bgcolor": "rgba(0, 0, 0, 0)",
            "font": {"color": "#bfdfff"},
        },
        hovermode="x unified",
        xaxis={
            "title": "日期",
            "showgrid": True,
            "gridcolor": "rgba(120, 150, 180, 0.12)",
            "zeroline": False,
            "linecolor": "rgba(120, 150, 180, 0.22)",
            "tickfont": {"color": "#b7d3e8"},
        },
        yaxis={
            "title": yaxis_title,
            "showgrid": True,
            "gridcolor": "rgba(120, 150, 180, 0.12)",
            "zeroline": False,
            "linecolor": "rgba(120, 150, 180, 0.22)",
            "tickfont": {"color": "#b7d3e8"},
        },
    )
    return fig


def build_close_chart(analysis_df, stock_name, stock_code):
    """绘制收盘价走势图。"""
    required_columns = ["date", "close"]
    _validate_chart_data(analysis_df, required_columns)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["close"],
            mode="lines",
            name="收盘价",
            line={"color": "#39d6ff", "width": 2.5},
        )
    )

    title_text = f"{stock_name}（{stock_code}）收盘价走势图"
    return _apply_dark_layout(fig, title_text, "价格")


def build_ma_chart(analysis_df, stock_name, stock_code):
    """绘制均线分析图。"""
    required_columns = ["date", "close", "ma5", "ma10", "ma20", "ma60"]
    _validate_chart_data(analysis_df, required_columns)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["close"],
            mode="lines",
            name="收盘价",
            line={"color": "#eaf8ff", "width": 1.8},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["ma5"],
            mode="lines",
            name="MA5",
            line={"color": "#00e0ff", "width": 1.8},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["ma10"],
            mode="lines",
            name="MA10",
            line={"color": "#2cffb0", "width": 1.8},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["ma20"],
            mode="lines",
            name="MA20",
            line={"color": "#ffd166", "width": 1.8},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["ma60"],
            mode="lines",
            name="MA60",
            line={"color": "#ff7b9c", "width": 1.8},
        )
    )

    title_text = f"{stock_name}（{stock_code}）均线分析图"
    return _apply_dark_layout(fig, title_text, "价格")


def build_volume_chart(analysis_df, stock_name, stock_code):
    """绘制成交量图。"""
    required_columns = ["date", "open", "close", "volume", "volume_ma5"]
    _validate_chart_data(analysis_df, required_columns)

    bar_colors = []
    for open_price, close_price in zip(analysis_df["open"], analysis_df["close"]):
        if close_price >= open_price:
            bar_colors.append("#20d7a8")
        else:
            bar_colors.append("#ff6b88")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=analysis_df["date"],
            y=analysis_df["volume"],
            name="成交量",
            marker={"color": bar_colors},
            opacity=0.78,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["volume_ma5"],
            mode="lines",
            name="5日均量",
            line={"color": "#39d6ff", "width": 2},
        )
    )

    title_text = f"{stock_name}（{stock_code}）成交量图"
    return _apply_dark_layout(fig, title_text, "成交量")


def build_macd_chart(analysis_df, stock_name, stock_code):
    """绘制 MACD 图。"""
    required_columns = ["date", "dif", "dea", "macd_hist"]
    _validate_chart_data(analysis_df, required_columns)

    hist_colors = []
    for value in analysis_df["macd_hist"]:
        if value >= 0:
            hist_colors.append("#20d7a8")
        else:
            hist_colors.append("#ff6b88")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=analysis_df["date"],
            y=analysis_df["macd_hist"],
            name="MACD 柱",
            marker={"color": hist_colors},
            opacity=0.82,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["dif"],
            mode="lines",
            name="DIF",
            line={"color": "#39d6ff", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=analysis_df["date"],
            y=analysis_df["dea"],
            mode="lines",
            name="DEA",
            line={"color": "#ffd166", "width": 2},
        )
    )

    title_text = f"{stock_name}（{stock_code}）MACD 图"
    return _apply_dark_layout(fig, title_text, "MACD")
