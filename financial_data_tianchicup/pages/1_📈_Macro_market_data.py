from pymongo import MongoClient
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

#从mongodb atlas上取数据

# 1. 连接 MongoDB + 定位所有用到的集合
client = MongoClient("mongodb+srv://cjiayi025:Cjy2004Zoey@cluster0.cjcb1yz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Macro_data"]
collections = {
    "央行动向": db["央行动向"],
    "企业景气": db["企业景气"],
    "A股数据": db["A股数据"],
    "夜盘数据": db["夜盘数据"]
}

# 2. 定义“指标名-所属集合”映射表（所有指标统一管理）
indicator_collection_map = [
    # 格式：(目标变量名, 集合名, 指标名)
    ("LPR1Y", "央行动向", "LPR1Y"),
    ("LPR5Y", "央行动向", "LPR5Y"),
    ("RATE_1", "央行动向", "RATE_1"),
    ("RATE_2", "央行动向", "RATE_2"),
    ("gold", "央行动向", "gold"),
    ("foreign_exchange", "央行动向", "foreign_exchange"),
    ("boom_index", "企业景气", "boom_index"),
    ("boom_index_YoY", "企业景气", "boom_index_YoY"),
    ("confidence_index", "企业景气", "confidence_index"),
    ("confidence_index_YoY", "企业景气", "confidence_index_YoY"),
    ("SH_INDEX", "A股数据", "SH_INDEX"),
    ("VIX", "夜盘数据", "VIX"),
    ("TREASURY_SPREAD", "夜盘数据", "TREASURY_SPREAD")
]

# 3. 循环批量生成所有指标的 DataFrame（1套逻辑处理所有指标）
indicator_dfs={}#这个字典的key是var_name,value是对应的dataframe
for var_name, coll_name, indicator in indicator_collection_map:
    # 从映射表中获取对应的集合
    coll = collections[coll_name]
    # 生成 DataFrame:字典列表转化为dataframe,key是列名，value是行数据
    df = pd.DataFrame([
        {"indicator": doc["indicator"], "date": item["date"], "value": item["value"]}
        for doc in coll.find({"indicator": indicator})  # 精准查询该指标
        for item in doc["data"]  # 展开 data 列表
    ])
    indicator_dfs[var_name] = df
# 4. 关闭连接
client.close()
print('2')



#streamlit画图


# ---------------------- 整体布局：左上+右上（第1行） +   左下+右下（第2行）----------------------
#tab页网页
st.set_page_config(page_title="宏观数据可视化", layout="wide")
#tab页标题
st.title("宏观数据可视化")
# 第1行：2列布局（左上=夜盘图，右上=央行动向图）
top_left_col, top_right_col = st.columns(2, gap="medium")
# 第2行：2列布局（左下=A股上证指数图，右下：企业景气图）
bottom_left_col, bottom_right_col = st.columns(2, gap="medium")



# ---------------------- 左上：第1幅图-夜盘数据图 ----------------------
with top_left_col:
    night_container = st.container(border=1, height=520)
    with night_container:
        st.markdown("##### 📊 夜盘数据趋势图", unsafe_allow_html=True)

        # 1. 数据准备
        vix_df = indicator_dfs['VIX']
        treasury_df = indicator_dfs['TREASURY_SPREAD']
        night_means = {
            "VIX": vix_df['value'].mean(),
            "TREASURY_SPREAD": treasury_df['value'].mean()
        }

        # 2. 下拉框
        night_selected = st.selectbox(
            label="选择夜盘指标",
            options=["VIX", "TREASURY_SPREAD"],
            index=0,
            key="night_select"
        )

        # 3. 动态参数+日期处理（颜色：VIX用紫罗兰色，利差用浅粉色）
        if night_selected == "VIX":
            df = vix_df
            mean_val = night_means["VIX"]
            line_color = '#9370DB'
            mean_label = f"VIX均值: {mean_val:.2f}"
        else:
            df = treasury_df
            mean_val = night_means["TREASURY_SPREAD"]
            line_color = "#FFB6C1"
            mean_label = f"利差均值: {mean_val:.4f}"
        df["date"] = pd.to_datetime(df["date"])

        # 4. 生成+显示图表
        night_fig = go.Figure()
        night_fig.add_trace(go.Scatter(
            x=df["date"], y=df["value"], mode="lines", name=night_selected,
            line=dict(color=line_color)
        ))
        night_fig.add_hline(y=mean_val, name=mean_label,
                            line=dict(color=line_color, dash="dash"))
        night_fig.add_annotation(
            x=df["date"].max(), y=mean_val, text=mean_label,
            xanchor="left", yanchor="bottom", font=dict(size=10, color=line_color), showarrow=False
        )
        night_fig.update_layout(
            title=f"{night_selected} 趋势图", xaxis_title="日期", yaxis_title="数值",
            legend=dict(x=1, y=0), height=350
        )
        st.plotly_chart(night_fig, use_container_width=True)


# ---------------------- 右上：第2幅图-央行动向数据图 ----------------------
with top_right_col:
    central_container = st.container(border=1, height=520)
    with central_container:
        st.markdown("##### 🏦 央行动向数据趋势图", unsafe_allow_html=True)

        # 1. 数据准备
        lpr1y = indicator_dfs['LPR1Y'].assign(date=pd.to_datetime(indicator_dfs['LPR1Y']['date']))
        lpr5y = indicator_dfs['LPR5Y'].assign(date=pd.to_datetime(indicator_dfs['LPR5Y']['date']))
        rate1 = indicator_dfs['RATE_1'].assign(date=pd.to_datetime(indicator_dfs['RATE_1']['date']))
        rate2 = indicator_dfs['RATE_2'].assign(date=pd.to_datetime(indicator_dfs['RATE_2']['date']))
        lpr_data = [lpr1y, lpr5y, rate1, rate2]
        gold_df = indicator_dfs['gold'].assign(date=pd.to_datetime(indicator_dfs['gold']['date']))
        fx_df = indicator_dfs['foreign_exchange'].assign(date=pd.to_datetime(indicator_dfs['foreign_exchange']['date']))

        # 2. 下拉框
        central_selected = st.selectbox(
            label="选择央行动向指标",
            options=["LPR_data", "gold", "foreign_exchange"],
            index=0,
            key="central_select"
        )

        # 3. 生成+显示图表（颜色修改：多指标用日落色阶，单一指标用橙色/粉紫）
        if central_selected == "LPR_data":
            central_fig = go.Figure()
            # 日落色阶（从黄到红）区分4个LPR指标，颜色差异明显
            line_info = [
                ("LPR 1年期", "#FF9F1C"),  # 亮橙色
                ("LPR 5年期", "#E76F51"),  # 砖红色
                ("利率1", "#E76F51"),      # 金黄色
                ("利率2", "#9E2A2B")       # 深棕色
            ]
            for df, (name, color) in zip(lpr_data, line_info):
                central_fig.add_trace(
                    go.Scatter(x=df["date"], y=df["value"], mode="lines", name=name,
                               line=dict(color=color)))
            central_fig.update_layout(title="LPR相关利率趋势图")
        elif central_selected == 'gold':
            central_fig = go.Figure()
            central_fig.add_trace(go.Scatter(x=gold_df["date"], y=gold_df["value"], mode="lines", name="黄金价格",
                                             line=dict(color="#FFA500")))  # 单一指标用橙色
            central_fig.update_layout(title="黄金价格趋势图")
        elif central_selected == 'foreign_exchange':
            central_fig = go.Figure()
            central_fig.add_trace(go.Scatter(x=fx_df["date"], y=fx_df["value"], mode="lines", name="外汇储备",
                                             line=dict(color="#DDA0DD")))  #pinkly色系
            central_fig.update_layout(title="外汇储备趋势图")

        central_fig.update_layout(
            xaxis_title="日期", yaxis_title="数值", legend=dict(x=1, y=0), height=350
        )
        st.plotly_chart(central_fig, use_container_width=True)


# ---------------------- 下方长条：第3幅图-A股上证指数图 ----------------------
with bottom_left_col:
    a_stock_container = st.container(border=1, height=520)
    with a_stock_container:
        st.markdown("##### 📈 A股-上证指数趋势图", unsafe_allow_html=True)

        # 1. 数据准备
        sh_index_df = indicator_dfs['SH_INDEX'].assign(
            date=pd.to_datetime(indicator_dfs['SH_INDEX']['date'])
        )

        # 2. 生成图表（颜色：上证指数用红色）
        a_stock_fig = go.Figure()
        a_stock_fig.add_trace(go.Scatter(
            x=sh_index_df["date"], y=sh_index_df["value"],
            mode="lines", name="上证指数",
            line=dict(color="#EC6E66", width=1.5)
        ))

        # 3. 图表样式
        a_stock_fig.update_layout(
            title="上证指数历史趋势",
            xaxis_title="日期", yaxis_title="指数点位",
            legend=dict(x=0.95, y=0.95),
            height=350,
            title_x=0
        )

        # 4. 显示图表
        st.plotly_chart(a_stock_fig, use_container_width=True)


# ---------------------- 下方长条：第4幅图-企业景气 ----------------------
with bottom_right_col:
    enterprise_container = st.container(border=1, height=520)
    with enterprise_container:
        st.markdown("##### 📈 企业景气趋势图", unsafe_allow_html=True)

        # 1. 数据准备 + 日期格式转换
        def quarter_to_date(quarter_str):
            year = int(quarter_str.split("年第")[0])
            quarter = int(quarter_str.split("年第")[1].split("季度")[0])
            month = (quarter - 1) * 3 + 1
            return f"{year}-{month:02d}-01"

        boom_index = indicator_dfs['boom_index'].copy()
        boom_index['date_parsed'] = boom_index['date'].apply(quarter_to_date)
        boom_index['date_parsed'] = pd.to_datetime(boom_index['date_parsed'])

        boom_index_YoY = indicator_dfs['boom_index_YoY'].copy()
        boom_index_YoY['date_parsed'] = boom_index_YoY['date'].apply(quarter_to_date)
        boom_index_YoY['date_parsed'] = pd.to_datetime(boom_index_YoY['date_parsed'])

        confidence_index = indicator_dfs['confidence_index'].copy()
        confidence_index['date_parsed'] = confidence_index['date'].apply(quarter_to_date)
        confidence_index['date_parsed'] = pd.to_datetime(confidence_index['date_parsed'])

        confidence_index_YoY = indicator_dfs['confidence_index_YoY'].copy()
        confidence_index_YoY['date_parsed'] = confidence_index_YoY['date'].apply(quarter_to_date)
        confidence_index_YoY['date_parsed'] = pd.to_datetime(confidence_index_YoY['date_parsed'])

        # 2. 下拉框
        enterprise_selected = st.selectbox(
            label="选择企业景气指标",
            options=["企业家信心指数", "企业景气指数"],
            index=0,
            key="enterprise_select"
        )

        # 3. 动态参数（颜色：用pinkly色系，浅粉色→深紫色）
        if enterprise_selected == "企业家信心指数":
            index_df = boom_index
            yoy_df = boom_index_YoY
            bar_color = "#DDA0DD"  # Pinkyl色系
            line_color = "#9370DB"
            yoy_label = "同比增长率（%）"
        else:
            index_df = confidence_index
            yoy_df = confidence_index_YoY
            bar_color = "#E6E6FA"  # 粉 Pinkyl色系
            line_color = "#8A2BE2"
            yoy_label = "同比增长率（%）"

        # 4. 生成组合图表
        enterprise_fig = go.Figure()

        # 4.1 第一个trace：指数（柱状图）
        enterprise_fig.add_trace(go.Bar(
            x=index_df["date_parsed"],
            y=index_df["value"],
            name=enterprise_selected,
            marker=dict(color=bar_color),
            yaxis="y1"
        ))

        # 4.2 第二个trace：同比增长率（折线图）
        enterprise_fig.add_trace(go.Scatter(
            x=yoy_df["date_parsed"],
            y=yoy_df["value"],
            mode="lines+markers",
            name=yoy_label,
            line=dict(color=line_color, width=2),
            yaxis="y2"
        ))

        # 5. 图表样式配置（不变）
        enterprise_fig.update_layout(
            title=f"{enterprise_selected} 趋势图（季度）",
            xaxis_title="季度",
            yaxis=dict(
                title=f"{enterprise_selected}（指数）",
                side="left",
                showgrid=False
            ),
            yaxis2=dict(
                title=yoy_label,
                side="right",
                overlaying="y",
                showgrid=False
            ),
            legend=dict(x=1, y=1),
            height=350,
            xaxis=dict(
                tickformat="%Y Q%q",
                dtick="M12"
            )
        )

        # 6. 显示图表
        st.plotly_chart(enterprise_fig, use_container_width=True)