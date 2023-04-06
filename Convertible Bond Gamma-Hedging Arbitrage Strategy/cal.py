import numpy as np
import datetime,math
from scipy import stats
import pandas as pd

# 日期转换
def strToDate(data):
    date=datetime.date(year=int(data[0:4]),month=int(data[5:7]),day=int(data[8:10]))
    return date

def listDictToDf(alist):
    key_list=alist[0].keys()
    rt_df=pd.DataFrame({key:[v[key] for v in alist] for key in key_list})
    return rt_df

# 波动率
def sigma(data):
    trade_num=250   # 年交易日
    date_years=len(data)/trade_num
    seq=np.array(data)
    seq=seq[1:]/seq[0:-1]-1
    e_seq=sum(seq)/len(seq)
    var_seq=(seq-e_seq) ** 2
    var_seq=sum(var_seq)/len(var_seq)
    vola_value=(var_seq ** (1/2))*(trade_num ** (1/2))
    return vola_value

# 夏普比率
def sharpe(data,rf=0):   # rf-无风险年利率
    trade_num=250   # 年交易日
    date_years=len(data)/trade_num
    seq=np.array(data)
    seq_return=seq[-1]/seq[0]
    seq_return_year=seq_return**(1/date_years)-1
    seq=seq[1:]/seq[0:-1]-1
    e_seq=sum(seq)/len(seq)
    var_seq=(seq-e_seq) ** 2
    var_seq=sum(var_seq)/len(var_seq)
    vola_value=(var_seq ** (1/2))*(trade_num ** (1/2))
    sharpe_value=(seq_return_year-rf)/vola_value
    return sharpe_value

# delta
def delta(st,k,r,T,sigma):
    d1=(math.log(st/k)+(r+1/2*sigma**2)*T)/(sigma*math.sqrt(T))
    delta=stats.norm.cdf(d1)
    return delta

def gamma(st,k,r,T,sigma):
    d1=(math.log(st/k)+(r+1/2*sigma**2)*T)/(sigma*math.sqrt(T))
    gamma=stats.norm.pdf(d1)/(st*sigma*math.sqrt(T))
    return gamma

# 最大回撤
def maxDrawDown(data):
    seq=np.array(data)
    seq_max=np.maximum.accumulate(seq)
    max_down=max((seq_max-seq)/seq_max)
    return max_down

# 年化收益
def annualReturn(data):
    data_len=len(data)
    return (data[-1]/data[0])**(250/data_len)-1

#收益
def ret (data):
    data_len=len(data)
    return (data[-1]/data[0])-1


# 超额收益率
def caar(data1,data2):
    return data1[-1]/data1[0]-data2[-1]/data1[0]

