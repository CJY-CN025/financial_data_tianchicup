import streamlit as st

st.set_page_config(
    page_title='阿里云天池杯金融数据平台',#浏览器标签显示标题
    page_icon='📊'#浏览器标签显示图标
)

# 自定义样式
st.markdown("""
<style>
    .main-header {font-size: 2.2rem; color: #1a365d; text-align: center; margin-bottom: 1rem;}
    .sub-header {font-size: 1.4rem; color: #2c5282; margin-top: 1.5rem;}
    .card {background: white; border-radius: 10px; padding: 1.2rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.2rem;}
    .stat-card {background: #edf2f7; border-radius: 8px; padding: 0.8rem; text-align: center;}
    .stat-value {font-size: 1.8rem; font-weight: bold; color: #2b6cb0;}
    .stat-label {color: #4a5568;}
</style>
""", unsafe_allow_html=True)

# main-header
st.markdown('<h1 class="main-header">📊阿里云天池杯金融数据分析平台</h1>', unsafe_allow_html=True)
st.write("---")

# sub-header 项目概述 ：分两栏3：1左栏文字右栏图片
with st.container():
    st.markdown('<h2 class="sub-header">🔍项目概述</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write("""
        平台依托 akshare 与 yfinance 双数据源获取全域金融信息，通过 MongoDB Atlas 云端存储构建标准化数据集，最终以直观的可视化形式 📊 呈现分析结果。
        无论是宏观经济指标、企业经营数据，还是市场舆情动态，都能在这里实现多维度整合，为用户提供清晰的金融市场洞察，精准辅助决策制定 💡。
        """)

    with col2:
        st.image("https://img1.baidu.com/it/u=1445499538,1518390247&fm=253&fmt=auto&app=138&f=JPEG?w=750&h=500",
                 width='stretch')

# sub-header数据概览 :均分4栏，每栏是数据统计卡片.4个主题分别为金融数据记录，宏观经济指标，企业数据，舆情分析样本
st.markdown('<h2 class="sub-header">📋数据概览</h2>', unsafe_allow_html=True)

# 数据统计卡片：stat-card,stat-value,stat-label
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        '<div class="stat-card"><div class="stat-value">10+</div><div class="stat-label">📈 宏观经济指标</div></div>',
        unsafe_allow_html=True)
with col2:
    st.markdown(
        '<div class="stat-card"><div class="stat-value">5K+</div><div class="stat-label">📊 微观企业数据</div></div>',
        unsafe_allow_html=True)
with col3:
    st.markdown(
        '<div class="stat-card"><div class="stat-value">30+</div><div class="stat-label">🏢 板块/行业数据</div></div>',
        unsafe_allow_html=True)
with col4:
    st.markdown(
        '<div class="stat-card"><div class="stat-value">600K+</div><div class="stat-label">💬 舆情分析样本</div></div>',
        unsafe_allow_html=True)
