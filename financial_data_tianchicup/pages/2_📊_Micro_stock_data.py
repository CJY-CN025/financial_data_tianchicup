import akshare as ak
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from dtaidistance import dtw
import warnings
warnings.filterwarnings('ignore')

# """
# akshare的API函数：
# ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20170301", end_date='20240528', adjust="")✔
# 返回 日期    股票代码   开盘   收盘  ... 振幅  涨跌幅  涨跌额 换手率
#
# ak.stock_individual_info_em(symbol="000001")✔
# 返回结果是item和value
#
# hs300 = ak.index_stock_cons(symbol="000300")✔
# 返回结果 品种代码  品种名称        纳入日期
#
# ak.stock_zh_a_spot_em 特慢
#
# """


def get_full_code(code):
    """根据股票代码自动添加市场前缀"""
    if code.startswith(('sh', 'sz')):
        return code
    if code.startswith('6'):
        return 'sh' + code
    else:
        return 'sz' + code



def find_similar_stocks(target_stock, start_date, end_date, top_n):
    try:
        target_stock_with_prefix = get_full_code(target_stock)
        display_target_stock = target_stock if not target_stock.startswith(('sh', 'sz')) else target_stock[2:]

        # 获取目标股票数据
        target_code = target_stock_with_prefix[2:]
        target_data = ak.stock_zh_a_hist(symbol=target_code, period="daily",
                                         start_date=start_date, end_date=end_date, adjust="qfq")

        if target_data.empty:
            print("未能获取目标股票数据，请检查股票代码和日期范围")
            return None, None, None, None

        # 获取目标股票名称
        try:
            stock_info = ak.stock_individual_info_em(symbol=target_code)
            target_name = stock_info[stock_info['item'] == '股票简称']['value'].iloc[0]
        except:
            target_name = f"股票({display_target_stock})"

        # 归一化
        target_close = target_data['收盘'].values
        target_dates = target_data['日期'].values
        if np.max(target_close) == np.min(target_close):
            target_close_normalized = np.zeros_like(target_close)
        else:
            target_close_normalized = (target_close - np.min(target_close)) / (np.max(target_close) - np.min(target_close))

        # 获取股票池（沪深300）
        try:
            stock_pool = ak.index_stock_cons_csindex(symbol="000300")
            stock_codes = [get_full_code(code) for code in stock_pool['成分券代码'].tolist()]
            stock_names = {get_full_code(row['成分券代码']): row['成分券名称'] for _, row in stock_pool.iterrows()}
        except Exception as e:
            print(f"获取股票池失败: {str(e)}")
            return None, None, None, None

        if target_stock_with_prefix not in stock_codes:
            stock_codes.insert(0, target_stock_with_prefix)
            if target_stock_with_prefix not in stock_names:
                stock_names[target_stock_with_prefix] = target_name

        stock_data = {}
        similarities = []

        for code in stock_codes:
            if code == target_stock_with_prefix:
                continue

            try:
                stock_code = code[2:]
                stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                                start_date=start_date, end_date=end_date, adjust="qfq")

                if not stock_hist.empty and len(stock_hist) >= len(target_data) * 0.8:
                    close_prices = stock_hist['收盘'].values
                    if np.max(close_prices) == np.min(close_prices):
                        normalized_prices = np.zeros_like(close_prices)
                    else:
                        normalized_prices = (close_prices - np.min(close_prices)) / (
                                    np.max(close_prices) - np.min(close_prices))

                    distance = dtw.distance(target_close_normalized, normalized_prices)
                    stock_data[code] = {
                        'normalized_prices': normalized_prices,
                        'distance': distance,
                        'dates': stock_hist['日期'].values,
                        'name': stock_names.get(code, f"未知({code[2:]})")
                    }
                    similarities.append((code, distance))

            except Exception as e:
                print(f"处理股票 {code} 时出错: {str(e)}")
                continue

        similarities.sort(key=lambda x: x[1])
        top_similar = similarities[:top_n]

        figs = []
        similar_stocks_info = []
        colors = ['#8B0000','#CD5C5C','#F08080','#FFB6C1']

        for i, (code, distance) in enumerate(top_similar):
            stock_info = stock_data[code]
            stock_name = stock_info['name']
            display_code = code[2:]
            similar_stocks_info.append(f"{stock_name}({display_code}) - DTW距离: {distance:.2f}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=target_dates,
                y=target_close_normalized,
                mode='lines',
                name=f"{target_name} (目标)",
                line=dict(color='black', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=stock_info['dates'],
                y=stock_info['normalized_prices'],
                mode='lines',
                name=f"{stock_name} (距离: {distance:.2f})",
                line=dict(color=colors[i % len(colors)], width=2)
            ))
            fig.update_layout(
                height=350,
                showlegend=True,
                xaxis_title="时间",
                yaxis_title="归一化价格",
                title=f"{target_name} vs {stock_name} - DTW距离: {distance:.2f}",
                xaxis=dict(tickangle=45)
            )
            figs.append(fig)

        return figs, similar_stocks_info, target_name, display_target_stock

    except Exception as e:
        # 只返回用户能理解的提示，不抛出错误
        error_msg = "股票数据获取失败（可能是网络问题或数据源暂时不可用）"
        return None, [error_msg], None, None  # 返回安全值，避免页面报错


# 获取数据并缓存
@st.cache_data
def get_stock_data():
    try:
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_summary_df = stock_zh_a_spot_em_df[
            ['代码', '名称', '涨跌幅', '成交量', '换手率', '市盈率-动态', '市净率']]
        # 去除空值
        stock_summary_df = stock_summary_df.dropna(subset=['涨跌幅', '成交量', '换手率', '市盈率-动态', '市净率'])
        return stock_summary_df
    except Exception as e:
        print(f"获取数据时出错: {e}")
        return None

# 绘左侧图函数
def plot_stock_chart(df, sort_column):
    """绘制指定列的前20名股票柱状图"""
    if df is None:
        return None

    # 按指定列降序排序并取前20
    sorted_df = df.sort_values(by=sort_column, ascending=False)[
        ['代码', '名称', sort_column]
    ].head(20)

    # 绘制柱状图
    fig = px.bar(
        sorted_df,
        x='名称',
        y=sort_column,
        title=f'{sort_column}前二十股票',
        labels={sort_column: f'{sort_column}'},
        color=sort_column,
        color_continuous_scale='sunset'
    )

    # 更新标题位置和图表布局
    fig.update_layout(
        title={
            'text': f'{sort_column}前二十股票',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        width=600,
        height=600,
        xaxis_title='股票名称',
        yaxis_title=sort_column
    )

    return fig

# 设置页面标题和布局
st.set_page_config(page_title="股票数据可视化", layout="wide")
# 大标题居中显示
st.markdown("<h1>股票微观数据与走势相似性分析</h1>", unsafe_allow_html=True)

# 左右分栏
col_left, col_right = st.columns([2,5])


# 左侧：股票收入前二十柱状图
with col_left:
    with st.container(border=True):
        st.markdown("##### 📊 股票不同指标前二十柱状图", unsafe_allow_html=True)
        # 使用选择框
        selected_index = st.selectbox(
            "请选择要查看的指标",
            ['换手率', '成交量', '涨跌幅', '市盈率-动态', '市净率']
        )
        stock_summary_df = get_stock_data()
        fig_stock = plot_stock_chart(stock_summary_df, selected_index)
        if fig_stock:
            st.plotly_chart(fig_stock,  width='stretch')

# 右侧：相似度对比图
with col_right:
    st.markdown("##### 🔄 股票走势相似度对比图", unsafe_allow_html=True)
    # 用户输入
    col1, col2, col3 = st.columns(3)
    with col1:
        stock_code = st.text_input("请输入股票代码", "600520")
    with col2:
        start_date = st.text_input("开始日期", "20250101")
    with col3:
        end_date = st.text_input("结束日期", "20250825")

    top_n = 4  # 显示4个相似股票，一行2个，共2行

    # 自动调用分析函数
    figs, similar_stocks_info, target_name, display_target_stock = find_similar_stocks(stock_code, start_date, end_date, top_n)

    if figs and similar_stocks_info and target_name and display_target_stock:

        # 一行显示2个图
        cols = st.columns(2)
        for i, fig in enumerate(figs):
            with cols[i % 2]:
                st.plotly_chart(fig, width='stretch')