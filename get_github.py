import requests
import pandas as pd
import ast

from pandas import DataFrame as df

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Authorization': 'Bearer null',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://hellogithub.com',
    'Referer': 'https://hellogithub.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'sort_by': 'featured',
    'page': '1',
    'rank_by': 'newest',
    'tid': 'all',
}

response = requests.get('https://api.hellogithub.com/v1/', params=params, headers=headers)
json_data = response.json()

# 解析data字段（字符串字典），提取目标字段
result = []
cols = ['title', 'name', 'summary', 'is_hot', 'is_claimed', 'clicks_total']

for item in json_data['data']:
    if isinstance(item, str):
        data_dict = ast.literal_eval(item)
    else:
        data_dict = item
    row = {col: data_dict.get(col, None) for col in cols}
    result.append(row)

# 转为DataFrame并保存
out_df = pd.DataFrame(result)
out_df.to_csv('github_extract.csv', index=False, encoding='utf-8-sig')
print(out_df.head())
