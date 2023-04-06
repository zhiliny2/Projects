import requests
import datetime
import csv
import os
import time
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
# 对wind.xslx预处理，送到get_daily中 #Wind.xlsx包含A股所有上市公司名称+股票代码
def get_info(filename):
    df = pd.read_excel('wind.xlsx')
    code_list_raw = list(df.iloc[:, 0])
    code_list = []
    for code_raw in code_list_raw:
        flag = code_raw.split('.')[1]
        if flag == 'SZ':
            code_list.append('1' + code_raw.split('.')[0])
        else:
            code_list.append('0' + code_raw.split('.')[0])

    # 文件不存在则创建，并写入表头
    if not os.path.exists(filename):
        csv_head = ['#', '日期', '股票代码', '名称', '收盘价', '最高价', '最低价', '开盘价', '前收盘', '涨跌额', '涨跌幅', '换手率', '成交量', '成交金额',
                    '总市值', '流通市',
                    '成交笔数']

        with open(filename, 'a+', encoding='utf-8-sig', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(csv_head)
    # 计算当前日期的前一天
    current_date = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    before_current_date = current_date - delta
    before_current_date = before_current_date.strftime('%Y%m%d')
    # get_daily函数第一个参数是股票代码，第二个参数是起始日期，第三个参数是结束日期，空的话表示最新，最后一个参数为存在本地的文件名
    for code in code_list:
        get_daily(code, before_current_date, '', filename)
        print(code, 'done')


    # 沪市前面加0，深市前面加1，比如0000001，是上证指数，1000001是中国平安
def get_daily(code, start, end,filename):

    url_mod = "http://quotes.money.163.com/service/chddata.html?code=%s&start=%s&end=%s"
    url = url_mod % (code, start, end)
    i=0
    while i<5:
        try:
            df = pd.read_csv(url, encoding='GB18030')
            df.to_csv(filename,mode='a+', encoding='utf-8-sig',header=None)
            break
        except:
            time.sleep(i)
            i+=1

    # print(df)


def my_plot(filename):
    plt.rcParams['font.sans-serif'] = ['simsun']  # 用宋体显示中文
    # 读入数据
    df = pd.read_csv(filename)
    #    2021-09到2022-02换手率平均值的折线图(by 月) 所有公司平均
    month_list=['09','10','11','12','01','02']
    aver_turnover_rate_list = []
    # 按行遍历
    for month in month_list:
        print(f'正在计算{month}月所有股票的平均换手率均值')
        turnover_rate_list=[df.iloc[i, 11] for i in range(len(df)) if str(df.iloc[i, 1]).split('-')[1] == month]
        aver_turnover_rate_list.append(np.mean(turnover_rate_list))
    plt.plot(month_list, aver_turnover_rate_list, label='Frist line', linewidth=3, color='r', marker='o',
             markerfacecolor='blue', markersize=12)

    plt.title(f'每月换手率平均{month_list}')
    plt.xlabel("月份")
    plt.ylabel("换手率")
    plt.figure(1)
    plt.show()
    plt.savefig("fig.1每月换手率平均.png")
    # 2月总成交金额(第13列)前5的公司, 换手率每日对比图(折线图)
    month='02'
    print("正在统计2月份的成交金额")
    # 先把2月份的所有数据拿到
    df_month2=df.loc[[i for i in range(len(df)) if str(df.iloc[i, 1]).split('-')[1] == month]]
    count = Counter(df_month2.iloc[:, 3])  # 统计
    # 拿到2月份的公司名称列表
    firm_name_list = list(count.keys())
    volume_firm_list = []
    for firm in firm_name_list:
        firm_volume_sum = np.sum((df_month2[df_month2['名称'] == firm]).iloc[:, 13])
        volume_firm_list.append([firm_volume_sum, firm])
    # 获取前五成交额最大的
    volume_firm_list.sort(key=lambda x: x[0], reverse=True)
    color_list = ['r', 'g', 'c', 'm', 'y']
    volume_firm_top5 = volume_firm_list[0:5]
    for index in range(5):
        y1 = [df_month2.iloc[i, 11] for i in range(len(df_month2)) if
              df_month2.iloc[i, 3] == volume_firm_top5[index][1]]
        y1 = y1[::-1]
        plt.plot(range(len(y1)), y1, label='Frist line', linewidth=3, color=color_list[index], marker='o',markerfacecolor='blue',
                 markersize=3)
    plt.title(f'2月总成交金额(第13列)前5的公司的每日换手率')
    plt.xlabel("交易日期")
    plt.ylabel("换手率")
    plt.legend([volume_firm_top5[0][1], volume_firm_top5[1][1], volume_firm_top5[2][1], volume_firm_top5[3][1],
                volume_firm_top5[4][1]])
    plt.figure(2)
    plt.show()

    # 2月总成交金额(第13列)前5的公司, 成交金额每日对比图(折线图)
    color_list = ['r', 'g', 'c', 'm', 'y']
    volume_firm_top5 = volume_firm_list[0:5]
    for index in range(5):
        y1 = [df_month2.iloc[i, 13] for i in range(len(df_month2)) if
              df_month2.iloc[i, 3] == volume_firm_top5[index][1]]
        y1 = y1[::-1]
        plt.plot(range(len(y1)), y1, label='Frist line', linewidth=3, color=color_list[index], marker='o',
                 markerfacecolor='blue',
                 markersize=3)
    plt.title(f'2月总成交金额(第13列)前5的公司的每日成交金额')
    plt.xlabel("交易日期")
    plt.ylabel("成交金额")
    plt.legend([volume_firm_top5[0][1], volume_firm_top5[1][1], volume_firm_top5[2][1], volume_firm_top5[3][1],
                volume_firm_top5[4][1]])
    plt.figure(3)
    plt.show()

    # 2月成交笔数前5的公司 对应的每日收盘价格变化(折线图)
    # 获取前五成交笔数
    deal_number_firm_list=[]
    for firm in firm_name_list:
        temp_list=list((df_month2[df_month2['名称'] == firm]).iloc[:, 16])
        while 'None' in temp_list:
            temp_list.remove('None')
        temp_list = [int(x) for x in temp_list]
        deal_number_firm_list.append([np.sum(temp_list), firm])

    deal_number_firm_list.sort(key=lambda x: x[0], reverse=True)
    color_list = ['r', 'g', 'c', 'm', 'y']
    deal_number_top5 = deal_number_firm_list[0:5]

    for index in range(5):
        y1 = [df_month2.iloc[i, 4] for i in range(len(df_month2)) if
              df_month2.iloc[i, 3] == deal_number_top5[index][1]]
        y1 = y1[::-1]
        plt.plot(range(len(y1)),y1, label='Frist line', linewidth=3, color=color_list[index], marker='o',
                 markerfacecolor='blue',
                 markersize=3)

    plt.title(f'2月成交笔数前5的公司 对应的每日收盘价格变化(折线图)')
    plt.xlabel("交易日期")
    plt.ylabel("收盘价格")
    plt.legend([deal_number_top5[0][1], deal_number_top5[1][1], deal_number_top5[2][1], deal_number_top5[3][1],
                deal_number_top5[4][1]])
    plt.figure(4)
    plt.show()



def main():
    filename = '2021-2022.csv'
    # get_info(filename)
    # 读取本地保存的文件，并作图
    my_plot(filename)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

