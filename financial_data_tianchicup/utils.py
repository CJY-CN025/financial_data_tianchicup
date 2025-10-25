import akshare as ak
import pandas as pd
from pymongo import MongoClient


#自定义函数1：时间筛选器
'''
获取固定时间范围的数据：start='2015-01-01',end='2025-09-01'
'''
def filter_by_date_range(df, date_col='date', start="2015-01-01", end="2025-09-01")->pd.DataFrame:
    return df[(df[date_col] >= start) & (df[date_col] <= end)].reset_index(drop=True)

#自定义函数2：获取信贷市场基准利率LPR,daily
def fetch_china_lpr(indicator_type:str='LPR1Y')->pd.DataFrame:
    try:
        lpr_raw = ak.macro_china_lpr()
        # 调用AKShare接口获取原始LPR数据，akshare获取的数据格式是dataframe
        # 验证原始数据有效性
        if lpr_raw.empty:
            raise ValueError("未获取到有效LPR数据，可能是接口或网络问题")
        # 转换日期列为datetime类型，确保时间格式统一
        lpr_raw["date"] = pd.to_datetime(lpr_raw["TRADE_DATE"])
        filted_data=filter_by_date_range(lpr_raw)
        if indicator_type=="LPR1Y":
            # 处理1年期LPR数据:rename(),columns字典的key为原值value为新值。rename是修改，[]是插入
            df_1year = filted_data[["LPR1Y",'date']].rename(
                columns={"LPR1Y": "value"})
            return df_1year
        elif indicator_type=='LPR5Y':
            # 处理5年期以上LPR数据
            df_5year = filted_data[["LPR5Y",'date']].rename(
                columns={"LPR5Y": "value"})
            return df_5year
        elif indicator_type=='RATE_1':
            # 处理5年期以上LPR数据
            df_in_1year= filted_data[["RATE_1",'date']].rename(
                columns={"RATE_1": "value"})
            return df_in_1year
        elif indicator_type=='RATE_2':
            # 处理5年期以上LPR数据
            df_up_5year= filted_data[["RATE_2",'date']].rename(
                columns={"RATE_2": "value"})
            return df_up_5year

    except Exception as e:
        print(f"获取LPR数据时发生错误: {str(e)}")
        # 错误时返回空DataFrame（包含必要列），避免后续apply()报错
        return pd.DataFrame(columns=["value", "date"])

#自定义函数3：获取央行黄金和外汇储备数据，monthly
def fetch_china_foreign_exchange_gold(indicator_type:str='黄金储备')->pd.DataFrame:
    try:
        foreign_exchange_gold_raw = ak.macro_china_foreign_exchange_gold()
        if foreign_exchange_gold_raw.empty:
            raise ValueError("未获取到有效央行黄金和外汇储备数据，可能是接口或网络问题")
        # 转换日期列为datetime类型，确保时间格式统一
        foreign_exchange_gold_raw["date"] = foreign_exchange_gold_raw["统计时间"]
        filted_data=filter_by_date_range(foreign_exchange_gold_raw)
        if indicator_type=="黄金储备":
            df_gold = filted_data[["黄金储备",'date']].rename(
                columns={"黄金储备": "value"})
            return df_gold
        elif indicator_type=='国家外汇储备':
            df_foreign_exchange = filted_data[["国家外汇储备",'date']].rename(
                columns={"国家外汇储备": "value"})
            return df_foreign_exchange

    except Exception as e:
        print(f"获取央行黄金和外汇储备数据时发生错误: {str(e)}")
        # 错误时返回空DataFrame（包含必要列），避免后续apply()报错
        return pd.DataFrame(columns=["value", "date"])

#自定义函数4：企业景气及企业家信心指数
def fetch_china_enterprise_boom_index(indicator_type:str='企业景气指数-指数')->pd.DataFrame:
    try:
        enterprise_boom_index_raw = ak.macro_china_enterprise_boom_index()
        if enterprise_boom_index_raw.empty:
            raise ValueError("未获取到有效企业景气及企业家信心指数数据，可能是接口或网络问题")
        enterprise_boom_index_raw['date'] = enterprise_boom_index_raw["季度"]
        filted_data = filter_by_date_range(enterprise_boom_index_raw)
        if indicator_type=="企业景气指数-指数":
            df_enterprise_boom_index= filted_data[["企业景气指数-指数",'date']].rename(
                columns={"企业景气指数-指数": "value"})
            return df_enterprise_boom_index
        elif indicator_type=='企业景气指数-同比':
            df_enterprise_boom_index_YoY = filted_data[["企业景气指数-同比",'date']].rename(
                columns={"企业景气指数-同比": "value"})
            return df_enterprise_boom_index_YoY
        elif indicator_type=="企业家信心指数-指数":
            df_entrepreneur_confidence_index= filted_data[["企业家信心指数-指数",'date']].rename(
                columns={"企业家信心指数-指数": "value"})
            return df_entrepreneur_confidence_index
        elif indicator_type=='企业家信心指数-同比':
            df_eentrepreneur_confidence_YoY = filted_data[["企业家信心指数-同比",'date']].rename(
                columns={"企业家信心指数-同比": "value"})
            return df_eentrepreneur_confidence_YoY

    except Exception as e:
        print(f"获取央行黄金和外汇储备数据时发生错误: {str(e)}")
    # 错误时返回空DataFrame（包含必要列），避免后续apply()报错
        return pd.DataFrame(columns=["value", "date"])







