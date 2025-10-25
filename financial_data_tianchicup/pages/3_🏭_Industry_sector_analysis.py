# Import packages
import streamlit as st
import akshare as ak
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc


# get data
@st.cache_data(ttl=300, show_spinner=False)
def get_industry_data():
    try:
        df = ak.stock_board_industry_summary_ths()
        # 清洗
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'].astype(str).str.replace('%', ''), errors='coerce')
        df['总成交量'] = pd.to_numeric(df['总成交量'], errors='coerce')
        df['净流入'] = pd.to_numeric(df['净流入'], errors='coerce')
        df['总成交额'] = pd.to_numeric(df['总成交额'], errors='coerce')
        df['资金强度'] = (df['净流入'] / df['总成交量']).round(4)
        return df
    except Exception as e:
        st.error(f"数据获取失败: {e}")
        return None


#create charts（涨跌幅与成交量）
def create_performance_chart(df, n):
    sorted_df = df.sort_values('涨跌幅', ascending=False).head(n)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sorted_df['板块'], y=sorted_df['涨跌幅'],
        name='涨跌幅(%)',
        marker_color=sorted_df['涨跌幅'].apply(lambda x: '#B5CE4E' if x < 0 else '#EC6E66')
    ))
    fig.add_trace(go.Scatter(
        x=sorted_df['板块'], y=sorted_df['总成交额'],
        mode='markers+lines', name='总成交额(元)',
        line=dict(color='orange', width=2), yaxis='y2'
    ))
    fig.update_layout(
        title=f"行业涨跌幅与总成交额 (前{n}名)",
        xaxis_tickangle=45, yaxis_title='涨跌幅(%)',
        yaxis2=dict(title='总成交额(元)', overlaying='y', side='right'),
        height=350, showlegend=True, margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


# create bar chart2(资金强度)
def create_strength_chart(df, n):
    sorted_df = df.sort_values('资金强度', ascending=False).head(n)
    fig = px.bar(sorted_df, x='资金强度', y='板块', orientation='h', height=350,
                 title=f"行业资金强度排名 (前{n}名)",
                 color='资金强度',
                 color_continuous_scale='Pinkyl')
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    return fig


#create pie chart（主力资金）
#只显示前6的原因是只有前6板块的净流入是正的，从第7个板块开始的净流入是负的
#外圈是blue颜色的净流出，内圈是orange颜色的净流入
def create_capital_flow_chart(df, n):
    # 取前n个板块（无论正负）
    sorted_df = df.sort_values('净流入', ascending=False).head(n)  # 从大到小排序（正→负）

    if sorted_df.empty:
        return px.pie(title="无数据可用")

    # 分离净流入（正）和净流出（负）
    inflow_df = sorted_df[sorted_df['净流入'] > 0].copy()  # 净流入
    outflow_df = sorted_df[sorted_df['净流入'] < 0].copy()  # 净流出
    outflow_df['净流入绝对值'] = -outflow_df['净流入']  # 取绝对值，用于饼图values

    # 准备颜色（净流入用暖色，净流出用冷色）
    inflow_colors = px.colors.sequential.Oranges[:len(inflow_df)]  #顺序色板：实现渐变色
    outflow_colors = px.colors.sequential.Blues[:len(outflow_df)]

    # 创建双环饼图（内层：净流入，外层：净流出）
    fig = go.Figure()

    # 添加净流入内层
    if not inflow_df.empty:
        fig.add_trace(go.Pie(
            labels=inflow_df['板块'],
            values=inflow_df['净流入'],
            hole=0.6,  # 内层空心，留空间给外层
            domain=dict(x=[0.2, 0.8], y=[0.2, 0.8]),
            name="资金净流入",
            textinfo='label+percent',
            textfont=dict(size=8),
            marker=dict(colors=inflow_colors, line=dict(color='white', width=2)),
            sort=False
        ))

    # 添加净流出外层
    if not outflow_df.empty:
        fig.add_trace(go.Pie(
            labels=outflow_df['板块'],
            values=outflow_df['净流入绝对值'],
            hole=0.7,  # 与内层半径匹配
            domain=dict(x=[0, 1], y=[0, 1]),
            name="资金净流出",
            textinfo='label+percent',
            textfont=dict(size=8),
            marker=dict(colors=outflow_colors, line=dict(color='white', width=2)),
            sort=False
        ))

    # 更新布局
    fig.update_layout(
        title=f"资金流向 TOP{n} 行业分布（内圈：净流入，外圈：净流出）",
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title="资金流向类型"
    )

    return fig

# streamlit
def main():
    st.set_page_config(page_title="行业板块分析", layout="wide")
    st.title("行业板块综合分析")
    display_count = st.slider("显示数量", 5, 30, 15)

    df = get_industry_data()
    if df is None:
        st.warning("无法获取数据")
        return

    # 第1行：一列（涨跌幅，横跨两列）
    row1_col = st.columns(1)[0]
    # 第2行：两列（资金强度 + 主力资金）
    row2_col1, row2_col2 = st.columns(2, gap="medium")

    # 第1行：涨跌幅分析（高度520，宽屏展示）
    with row1_col:
        with st.container(border=1, height=520):
            st.markdown("##### 📈 涨跌幅分析", unsafe_allow_html=True)
            fig1 = create_performance_chart(df, display_count)
            st.plotly_chart(fig1)

    # 第2行左：资金强度分析（高度520）
    with row2_col1:
        with st.container(border=1, height=520):
            st.markdown("##### 🔋 资金强度分析", unsafe_allow_html=True)
            fig2 = create_strength_chart(df, display_count)
            st.plotly_chart(fig2)

    # 第2行右：主力资金流向（高度520，与左侧等高）
    with row2_col2:
        with st.container(border=1, height=520):
            st.markdown("##### 💧 主力资金流向", unsafe_allow_html=True)
            fig3 = create_capital_flow_chart(df, display_count)
            st.plotly_chart(fig3)


if __name__ == "__main__":
    main()


