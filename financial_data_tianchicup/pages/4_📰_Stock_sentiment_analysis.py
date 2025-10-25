import streamlit as st
import akshare as ak
import jieba
import plotly.graph_objects as go
import pandas as pd
import logging

# 关闭jieba的调试信息
jieba.setLogLevel(logging.INFO)

# 定义积极情感词汇集
positive_words = {
    "好", "棒", "赞", "优秀", "出色", "卓越", "完美", "精彩", "厉害", "牛", "强", "猛", "神", "惊艳",
    "满意", "欣慰", "振奋", "鼓舞", "欣喜", "惊喜", "亮眼", "抢眼", "火爆", "热", "高能", "爆棚",
    "上涨", "拉升", "飙升", "暴涨", "涨停", "翻倍", "突破", "创新高", "走强", "反弹", "回升", "回暖",
    "翻红", "收涨", "飘红", "强劲", "坚挺", "稳中有升", "持续上涨", "加速上涨", "强势", "领涨",
    "高开", "高走", "收高", "上扬", "冲高", "逆袭", "反攻", "收复", "收复失地", "触底反弹",
    "盈利", "增利", "扭亏为盈", "利润增长", "净利增长", "营收增长", "业绩大增", "超预期", "大赚",
    "高增长", "高毛利", "高回报", "分红", "派息", "送股", "高送转", "盈利改善", "成本下降", "效率提升",
    "盈利拐点", "盈利修复", "盈利兑现", "盈利释放", "业绩爆发", "业绩亮眼", "业绩稳健", "盈利能力强",
    "利好", "利好消息", "利好政策", "风口", "蓝海", "朝阳产业", "黄金赛道", "高景气", "高成长",
    "潜力股", "成长股", "龙头", "领军", "霸主", "王者", "独角兽", "明星企业", "行业领先", "市占率提升",
    "需求旺盛", "供不应求", "订单饱满", "产能释放", "技术领先", "创新驱动", "核心竞争力", "护城河",
    "战略清晰", "布局完善", "生态完整", "协同发展", "协同效应", "资源整合", "优势明显",
    "乐观", "看好", "信心", "信心恢复", "信心增强", "预期向好", "预期改善", "预期强劲", "前景光明",
    "未来可期", "值得期待", "蓄势待发", "潜力无限", "爆发在即", "值得投资", "买入良机", "抄底机会",
    "价值洼地", "低估", "低估修复", "估值提升", "重估", "重估潜力", "长期持有", "坚定持有", "增持",
    "买入", "推荐", "强烈推荐", "上调评级", "目标价上调", "买入评级", "增持评级", "买入信号", "金叉",
    "稳定", "稳健", "平稳", "安全", "可靠", "健康", "可持续", "可持续发展", "抗风险能力强", "防御性强",
    "低波动", "低风险", "避险", "避风港", "压舱石", "定海神针", "基本盘稳固", "经营稳健", "现金流充裕",
    "财务健康", "资产负债率低", "无债务压力", "轻资产", "高ROE", "高股息", "高分红", "稳定分红",
    "获批", "通过", "核准", "落地", "签约", "合作", "战略合作", "联手", "联合", "并购成功", "重组完成",
    "技术突破", "研发成功", "专利获批", "国产替代", "自主可控", "卡脖子突破", "技术领先", "智能化",
    "数字化转型", "AI赋能", "绿色转型", "碳中和", "环保", "节能减排", "社会责任", "ESG优秀"
}

# 定义消极情感词汇
negative_words = {
    "坏", "差", "烂", "糟", "劣", "弱", "低", "惨", "悲", "坑", "雷", "炸", "崩", "爆雷", "暴雷",
    "失望", "担忧", "焦虑", "恐慌", "悲观", "阴霾", "沉重", "压抑", "低迷", "疲软", "疲态",
    "跌", "下跌", "暴跌", "重挫", "大跌", "跳水", "闪崩", "破位", "破净", "破发", "阴跌", "持续下跌",
    "单边下行", "加速下跌", "断崖式下跌", "千股跌停", "收跌", "收绿", "低开", "低走", "收低", "下挫",
    "回落", "下滑", "走弱", "疲软", "承压", "震荡下行", "探底", "寻底", "底部未明", "杀估值",
    "亏损", "巨亏", "大亏", "连亏", "持续亏损", "业绩下滑", "业绩暴雷", "业绩变脸", "不及预期",
    "利润下滑", "营收下滑", "营收萎缩", "毛利率下降", "净利率下降", "成本上升", "费用失控",
    "资不抵债", "债务违约", "债务危机", "高负债", "高杠杆", "现金流紧张", "资金链断裂",
    "商誉减值", "资产减值", "计提损失", "坏账", "坏账计提", "财务造假", "虚增利润", "虚增收入",
    "问题", "隐患", "漏洞", "缺陷", "风险", "高风险", "重大风险", "系统性风险", "黑天鹅", "灰犀牛",
    "危机", "困境", "困局", "泥潭", "泥足深陷", "退市风险", "ST风险", "戴帽", "被ST", "被*ST",
    "违规", "违法", "欺诈", "造假", "信披违规", "内幕交易", "操纵市场", "被立案", "被调查",
    "处罚", "罚款", "监管处罚", "警告", "通报批评", "纪律处分", "诉讼", "仲裁", "纠纷", "官司",
    "利空", "利空消息", "利空政策", "寒冬", "夕阳产业", "红海", "内卷", "恶性竞争", "产能过剩",
    "需求萎缩", "订单减少", "库存积压", "去库存", "价格战", "市场份额下降", "客户流失", "客户投诉",
    "技术落后", "落后产能", "淘汰", "被替代", "边缘化", "掉队", "掉出赛道", "失去先机",
    "悲观", "看空", "谨慎", "警惕", "回避", "减持", "抛售", "清仓", "卖出", "卖出评级", "减持评级",
    "下调评级", "目标价下调", "看跌", "空头", "做空", "爆仓", "踩踏", "恐慌性抛售", "流动性枯竭",
    "估值泡沫", "高估", "估值过高", "杀估值", "估值回归", "戴维斯双杀", "戴维斯双击（反向）",
    "高管离职", "核心人员流失", "管理层动荡", "内斗", "控制权争夺", "股权纠纷", "质押爆仓",
    "实控人被查", "实控人失联", "实控人被捕", "大股东减持", "高管减持", "限售股解禁", "减持潮",
    "业绩承诺未完成", "对赌失败", "并购失败", "重组失败", "项目终止", "项目延期", "项目搁浅",
    "疫情影响", "供应链中断", "原材料涨价", "汇率波动", "地缘政治风险", "贸易摩擦", "关税",
    "制裁", "出口受限", "进口受限", "环保限产", "停产", "停工", "限电", "安全事故", "质量事故"
}


def analyze_sentiment_jieba(text):
    # 使用jieba分词库对输入文本进行分词处理
    words = jieba.lcut(text.strip())
    # 初始化积极词计数器
    pos_count = 0
    # 初始化消极词计数器
    neg_count = 0
    # 遍历分词结果
    for word in words:
        # 如果词汇在积极词典中，增加积极词计数
        if word in positive_words:
            pos_count += 1
        # 如果词汇在消极词典中，增加消极词计数
        elif word in negative_words:
            neg_count += 1
    # 比较积极词和消极词数量，返回情感类别
    if pos_count > neg_count:
        return 'positive'  # 积极情感
    elif neg_count > pos_count:
        return 'negative'  # 消极情感
    else:
        return 'neutral'  # 中性情感


# 定义获取并分析新闻的函数
def fetch_and_analyze_news(stock_code, source_name, fetch_function, title_column='新闻标题'):
    """
    参数说明：
        stock_code (str): 股票代码
        source_name (str): 数据来源名称
        fetch_function (callable): 获取新闻数据的函数
        title_column (str): 新闻标题所在的列名
    """
    # 尝试执行新闻获取和分析
    try:
        # 调用传入的函数获取新闻DataFrame
        news_df = fetch_function(symbol=stock_code)

        # 检查获取的新闻数据是否为空
        if news_df is None or news_df.empty:
            # 如果数据为空，显示警告信息
            st.warning(f"警告: 从 {source_name} 获取新闻失败或无数据。")
            # 返回默认结果
            return {"source": source_name, "positive": 0, "negative": 0, "neutral": 0, "total": 0}

        # 确认标题列是否存在
        if title_column not in news_df.columns:
            # 如果指定列不存在，尝试使用'标题'列
            if '标题' in news_df.columns:
                title_column = '标题'
            else:
                # 如果都不存在，使用第一列
                st.warning(f"警告: 在 {source_name} 的数据中未找到 '{title_column}' 或 '标题' 列，将使用第一列。")
                title_column = news_df.columns[0]

        # 提取新闻标题列表
        titles = news_df[title_column].tolist()
        # 初始化各类情感计数器
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_analyzed = 0

        # 遍历所有新闻标题进行情感分析
        for title in titles:
            # 清理标题文本
            title_text = str(title).strip()
            # 如果标题为空则跳过
            if not title_text:
                continue
            try:
                # 分析标题情感
                sentiment = analyze_sentiment_jieba(title_text)
                # 增加已分析总数
                total_analyzed += 1
                # 根据情感类别增加相应计数
                if sentiment == 'positive':
                    positive_count += 1
                elif sentiment == 'negative':
                    negative_count += 1
                else:
                    neutral_count += 1
            except Exception:
                # 如果分析出错，跳过该标题
                pass

        # 返回分析结果
        return {
            "source": source_name,
            "positive": positive_count,
            "negative": negative_count,
            "neutral": neutral_count,
            "total": total_analyzed
        }
    # 捕获异常情况
    except Exception as e:
        # 显示错误信息
        st.error(f"在从 {source_name} 获取或处理新闻时发生错误: {e}")
        # 返回默认结果
        return {"source": source_name, "positive": 0, "negative": 0, "neutral": 0, "total": 0}


def main():
    # 设置页面标题
    st.title("股票新闻情感分析工具")

    # 输入股票代码的文本框
    stock_code = st.text_input("请输入你想分析的股票代码 (例如: 600381): ", value="600381")

    # 创建分析按钮
    if st.button("开始分析"):
        # 检查是否有输入股票代码
        if not stock_code:
            # 如果没有输入，显示警告
            st.warning("请先输入股票代码")
            return

        # 显示正在分析的信息
        st.write(f"正在分析股票代码: {stock_code}")

        # 定义数据源配置 - 包含数据源名称、获取函数和标题列名
        data_sources = [
            ("东方财富(em)", ak.stock_news_em, '新闻标题'),
            ("财联社(cls)", ak.stock_info_global_cls, '标题'),
        ]
        # 初始化结果列表
        results = []
        # 初始化有效数据标志
        all_results_valid = True

        # 循环处理每个数据源
        for source_name, fetch_func, title_col in data_sources:
            # 对每个数据源进行情感分析
            result = fetch_and_analyze_news(stock_code, source_name, fetch_func, title_col)
            # 将结果添加到列表
            results.append(result)

            # 检查该数据源是否有有效数据
            if result['total'] == 0:
                # 如果没有数据，显示警告
                st.warning(f"警告: 来源 {source_name} 没有可用于分析的新闻。")
                # 设置有效数据标志为False
                all_results_valid = False

        # 准备绘图数据
        # 初始化有效结果列表
        valid_results = []
        # 遍历所有结果
        for res in results:
            # 只处理有数据的结果
            if res['total'] > 0:
                # 添加到有效结果列表
                valid_results.append({
                    'source': res['source'],
                    'total': res['total'],
                    'sentiment_counts': {
                        '积极': res['positive'],
                        '消极': res['negative'],
                        '中性': res['neutral']
                    },
                    'titles': []  # 初始化标题列表
                })

        if valid_results:
            # 创建第一个板块：饼图板块，使用container实现边框效果
            with st.container(border=1,height=500):
                st.markdown("##### 情感分析饼图", unsafe_allow_html=True)

                # 创建两列布局用于显示两个饼图
                cols = st.columns(2)

                # 生成饼图
                for i, res in enumerate(valid_results):
                    with cols[i % 2]:  # 在两列中交替显示饼图
                        # 生成饼图的数据
                        labels = list(res['sentiment_counts'].keys())
                        values = list(res['sentiment_counts'].values())

                        # 定义颜色映射
                        color_map = {'积极': '#F7B7D2', '消极': '#F7A6AC', '中性': '#5A56A6'}
                        colors = [color_map.get(label, '#CCCCCC') for label in labels]

                        # 创建Plotly饼图
                        fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
                        fig.update_layout(title_text=f"{res['source']}情感分析", height=420)

                        # 在容器中显示图表
                        st.plotly_chart(fig, use_container_width=True)

            # 创建第二个板块：新闻标题板块，使用expander实现边框效果
            with st.expander("新闻标题展示", expanded=True):
                # 显示新闻标题部分
                for i, res in enumerate(valid_results):
                    source_name = res['source']
                    try:
                        # 获取新闻数据
                        news_df = next(
                            (fetch_func for src_name, fetch_func, _ in data_sources if src_name == source_name), None)(
                            symbol=stock_code)
                        # 检查数据是否为空
                        if news_df is None or news_df.empty:
                            # 如果数据为空，显示信息
                            st.info(f"{source_name}: 暂无新闻数据。")
                        else:
                            # 确定标题列
                            title_col = '新闻标题' if '新闻标题' in news_df.columns else '标题' if '标题' in news_df.columns else \
                                news_df.columns[0]
                            # 提取标题
                            titles = news_df[title_col].dropna().astype(str).tolist()

                            # 显示前10条新闻标题
                            st.write(f"**{source_name}**")
                            for j, title in enumerate(titles[:10], 1):
                                st.write(f"  {j}. {title.strip()}")
                            # 如果还有更多标题，显示提示
                            if len(titles) > 10:
                                st.write(f"  ... 还有 {len(titles) - 10} 条新闻未显示")
                    except Exception as e:
                        # 如果获取标题出错，显示错误信息
                        st.error(f"  获取{source_name}标题时出错: {e}")
        else:
            # 如果没有有效数据，显示警告
            st.warning("没有有效的数据用于生成图表。")


if __name__ == "__main__":
    main()



