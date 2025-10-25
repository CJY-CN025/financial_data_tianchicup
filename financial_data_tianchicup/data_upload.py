from pymongo import MongoClient
from utils import fetch_china_lpr,fetch_china_foreign_exchange_gold,fetch_china_enterprise_boom_index

#将数据上传到mongodb atlas

#连接到mongodb atlas
# 正确格式（假设密码是 Cjy2004Zoey，无特殊字符）
connection_string = "mongodb+srv://cjiayi025:Cjy2004Zoey@cluster0.cjcb1yz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
#在Macro_data database下创建2个collection
db=client['Macro_data']
collections_to_create = ["央行动向", "企业景气"]
for coll_name in collections_to_create:
    # 关键修复：先检查集合是否存在，不存在才创建
    if coll_name not in db.list_collection_names():
        db.create_collection(coll_name)
        print(f"✅ 成功创建集合：{coll_name}")
    else:
        print(f"ℹ️ 集合 '{coll_name}' 已存在，跳过创建")


# 1. 数据获取
data_map = {
    'LPR1Y': fetch_china_lpr('LPR1Y'),
    'LPR5Y': fetch_china_lpr('LPR5Y'),
    'RATE_1': fetch_china_lpr('RATE_1'),
    'RATE_2': fetch_china_lpr('RATE_2'),
    'gold': fetch_china_foreign_exchange_gold('黄金储备'),
    'foreign_exchange': fetch_china_foreign_exchange_gold('国家外汇储备'),
    'boom_index': fetch_china_enterprise_boom_index('企业景气指数-指数'),
    'boom_index_YoY': fetch_china_enterprise_boom_index('企业景气指数-同比'),
    'confidence_index': fetch_china_enterprise_boom_index('企业家信心指数-指数'),
    'confidence_index_YoY': fetch_china_enterprise_boom_index('企业家信心指数-同比')
}

# 2. 检查每个指标的数据类型（定位 None/空DataFrame问题）
print("=== 检查每个指标的数据类型 ===")
for indicator_name, df in data_map.items():
    if df is None:
        print(f"❌ 指标 '{indicator_name}'：返回 None（获取数据失败）")
    elif df.empty:
        print(f"⚠️ 指标 '{indicator_name}'：返回空 DataFrame（数据为空）")
    else:
        print(f"✅ 指标 '{indicator_name}'：返回有效 DataFrame（列：{df.columns.tolist()}）")

# 3. 数据转换（生成 MongoDB 文档格式）
# 先定义指标与集合的对应关系（用于后续查询/写入）
indicator_to_collection = {
    'LPR1Y': '央行动向',
    'LPR5Y': '央行动向',
    'RATE_1': '央行动向',
    'RATE_2': '央行动向',
    'gold': '央行动向',
    'foreign_exchange': '央行动向',
    'boom_index': '企业景气',
    'boom_index_YoY': '企业景气',
    'confidence_index': '企业景气',
    'confidence_index_YoY': '企业景气'
}

# 转换有效数据为 MongoDB 文档，并记录每个文档对应的集合
valid_documents = []  # 格式：[(文档, 目标集合名), ...]
for indicator_name, df in data_map.items():
    try:
        # 转换 DataFrame 为 [{date:..., value:...}, ...]
        data_array = df.apply(
            lambda row: {"date": str(row['date']), "value": row['value']},
            axis=1
        ).tolist()

        # 生成 MongoDB 文档
        doc = {"indicator": indicator_name, "data": data_array}
        # 获取该指标对应的目标集合（从映射关系中取）
        target_collection = indicator_to_collection[indicator_name]
        valid_documents.append((doc, target_collection))

        print(f"\n✅ 指标 '{indicator_name}'：文档转换完成（数据条数：{len(data_array)}，目标集合：{target_collection}）")

    except Exception as e:
        print(f"❌ 指标 '{indicator_name}'：文档转换失败：{str(e)}（跳过）")


#  4. 避免重复写入（查询+插入）
print("\n=== 开始写入 MongoDB（避免重复） ===")
inserted_count = 0  # 记录本次实际插入的文档数
skipped_count = 0   # 记录本次跳过的重复文档数

for doc, target_collection in valid_documents:
    indicator_name = doc["indicator"]
    # 关键：查询目标集合中是否已存在该 indicator 的文档
    # 使用 "indicator": indicator_name 作为唯一标识（每个指标只存1个文档）
    existing_doc = db[target_collection].find_one({"indicator": indicator_name})

    if existing_doc:
        # 已存在：跳过写入，打印提示
        print(f"ℹ️ 指标 '{indicator_name}'（集合：{target_collection}）：已存在（_id: {existing_doc['_id']}），跳过写入")
        skipped_count += 1
    else:
        # 不存在：执行插入
        try:
            insert_result = db[target_collection].insert_one(doc)
            print(f"✅ 指标 '{indicator_name}'（集合：{target_collection}）：写入成功（_id: {insert_result.inserted_id}）")
            inserted_count += 1
        except Exception as e:
            print(f"❌ 指标 '{indicator_name}'（集合：{target_collection}）：写入失败：{str(e)}（跳过）")


#  5. 写入结果汇总与连接关闭
print(f"\n=== 写入结果汇总 ===")
print(f"📊 本次处理有效指标数：{len(valid_documents)}")
print(f"✅ 成功插入文档数：{inserted_count}")
print(f"⏭️  跳过重复文档数：{skipped_count}")
print(f"❌ 写入失败文档数：{len(valid_documents) - inserted_count - skipped_count}")

# 关闭 MongoDB 连接
client.close()
print(f"\n🔌 MongoDB 连接已关闭")





