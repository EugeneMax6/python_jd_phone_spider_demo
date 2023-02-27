import jieba
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wordcloud import WordCloud

# 原始数据
data = pd.read_csv("information.csv", header=0, encoding="gbk", usecols=[1, 2, 3, 4, 5])  # 读取csv数据文件
data = pd.DataFrame(data)
print('源数据数量：' + str(len(data)))
data = data.drop_duplicates()  # 清除重复的数据
print('去重复后的数量：' + str(len(data)))
print("样本数据: %d" % len(data))
data.fillna(0)  # 用0填充空白的部分


# 对数据进行分类,避免手机配件类搜索结果影响
def itemType(item):
    words1 = ['移动电源', '充电宝', '数据线', '音箱', '麦克风', '耳机', '手机壳', '钢化膜', '保护', '支架']
    for element in words1:
        if item.find(element) != -1:
            return '配件-' + element
        elif item.find('二手') != -1:
            return '二手手机'
    else:
        return '全新手机'


# 将字符串型的评论数转换为整数
def trans(num):
    if isinstance(num, int):
        return str(num)
    if num.find('+') != -1:
        num = num.replace('+', '')
    if num.find('万') != -1:
        num = num.replace('万', '')
        # 以万为单位的评论数可能为小数，比如3.4万，因此强制转换为float类型存储
        num = float(num) * 10000
    num = str(int(num))
    return num


data["商品类型"] = data["info_name"].apply(itemType)
data["info_commit"] = data["info_commit"].apply(trans)
data["info_commit"] = data["info_commit"].apply(pd.to_numeric)
data.fillna(0)
# 对数据进行数据类型的转换以及数据筛选
data['info_money'] = data['info_money'].astype(int)
data['info_commit'] = data['info_commit'].astype(int)
data1 = data[(data['商品类型'] == '全新手机')]
data2 = data[(data['商品类型'] == '二手手机')]

# 不同品牌的评论量占比
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.figsize'] = (20.0, 20.0)
gb1 = data1.groupby(
    by=['info_store'],
    as_index=False
)['info_commit'].agg({
    'info_commit': np.sum
})
print(gb1['info_commit'] > 50)
x = gb1['info_commit'].argsort()[::-1]
z = x.values[0:8]
g1 = gb1.iloc[z, :]
plt.pie(g1['info_commit'], labels=g1['info_store'], textprops={}, autopct="""%0.1f%%""")
plt.title('不同店铺销量分析', fontsize=40)
plt.legend(loc='lower right', fontsize=40)
plt.savefig('1.jpg')
plt.show()

# 不同店铺平均售价分析
gb1 = data1.groupby(
    by=['info_store'],
    as_index=False
)['info_money'].agg({
    'info_money': np.average
})
g1 = gb1[(gb1['info_money'] > 5000)]
index = np.arange(g1['info_store'].size)
plt.barh(index, g1['info_money'], height=0.5, color='maroon')
plt.yticks(index, g1['info_store'])
plt.xlabel('售价5000元以上店铺平均售价分析', fontsize=20)
plt.ylabel('商品售价', loc='top', fontsize=20)
plt.savefig('2.jpg')
plt.show()

# 不同价格区间购买人数
data1['info_money'] = data1['info_money'].astype(int)
bins = [0, 500, 1000, 3000, 5000, 20000]
labels = ['500及以下', '500到1000', '1000到3000', '3000到5000', '5000以上']
data1['info_money'] = pd.cut(data1['info_money'], bins, labels=labels)
gb1 = data1.groupby(
    by=['info_money'],
    as_index=False
)['info_commit'].agg({
    'info_commit': np.sum
})
plt.pie(gb1['info_commit'], labels=gb1['info_money'], autopct='%.2f%%')
plt.title('不同价格区间购买人数百分比')
plt.savefig('3.jpg')
plt.show()
# 均价3000元以上手机品牌平均售价
data1 = data[(data['商品类型'] == '全新手机')]
gb1 = data1.groupby(
    by=['info_brand'],
    as_index=False
)['info_money'].agg({
    'info_money': np.average
})
g1 = gb1[gb1['info_money'] > 3000]
g1 = g1.sort_values('info_money', ascending=False)
index = np.arange(g1['info_brand'].size)
plt.bar(index, g1['info_money'], width=0.35, color='maroon')
plt.plot(index, g1['info_money'], '-o', linewidth=2)
plt.xticks(index, g1['info_brand'])
plt.xlabel('均价3000元以上手机品牌')
plt.ylabel('商品售价')
plt.savefig('4.jpg')
plt.show()

# 均价1000-3000元以上手机品牌平均售价
g2 = gb1[(gb1['info_money'] > 1000) & (gb1['info_money'] < 3000)]
index = np.arange(g2['info_brand'].size)
plt.bar(index, g2['info_money'], width=0.35, color='maroon')
plt.xticks(index, g2['info_brand'])
plt.xlabel('均价1000-3000元手机品牌')
plt.ylabel('商品售价')
plt.savefig('5.jpg')
plt.show()

# 散点图———————商品价格和购买人数关系
data3 = data[(data['商品类型'] == '全新手机') & (data['info_money'] < 15000)]
plt.plot(data3['info_money'], data3['info_commit'], '.', color='blue')
plt.xlabel('商品售价')
plt.ylabel('购买人数')
plt.ylim((0, 50000))
plt.title('商品价格和购买人数关系')
plt.grid(True)
plt.savefig('6.jpg')
plt.show()

# 词云图
title_cut = []
for name in data['info_name']:
    j = jieba.lcut(name)
    for i in j:
        title_cut.append(i)

WC = WordCloud(font_path='C:/Windows/Fonts/STKAITI.TTF', background_color='white',
               width=5000, height=3000, margin=2).generate(','.join(title_cut))
plt.figure(figsize=(16, 8))
plt.imshow(WC)
plt.axis('off')
plt.savefig('7.jpg')
