import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
dir=r'C:\Users\olivercb\Documents\WeChat Files\wxid_rvbcf0bxky3h22\FileStorage\File\2022-08'
##1 对齐时间，生成csv文件

file_dir=r'C:\Users\olivercb\Documents\WeChat Files\wxid_rvbcf0bxky3h22\FileStorage\File\2022-08\all_data\output'
csv_out_dir=r'C:\Users\olivercb\Documents\WeChat Files\wxid_rvbcf0bxky3h22\FileStorage\File\2022-08\all_data\resultdata'

data_iv = pd.read_excel(dir+"\\"+'IV.xlsx', skiprows=1,sheet_name='IV(一年定存)1')
data_pr = pd.read_excel(dir+"\\"+'IV.xlsx',skiprows=1,sheet_name='转股溢价率')
len_date=len(data_pr['Date'])
filestocklist = os.listdir(file_dir)
for tmpstock in data_iv.columns[1:]:
    arr = np.zeros((len_date, 3))
    df1=pd.DataFrame(arr,columns=['date','premium_rate','iv'])
    #df1.set_index(data_pr['Date'])
    df1['premium_rate']=data_pr[tmpstock]
    df1['iv'] = data_iv[tmpstock]
    df1['date']=data_pr['Date']
    #print(df1)
    csv_file = tmpstock.split('.')[0] + ".csv"
    if csv_file not in filestocklist:
        print("not find %s",csv_file)
        continue
    tmp_data2 = pd.read_csv(str(file_dir) + '\\' + csv_file)
    #tmp_data2 = tmp_data2[tmp_data2['date'] >= '2018-01-02']
    #print(tmp_data2)
    tmp_data2 = tmp_data2.dropna()
    arr2 = np.zeros((len(tmp_data2['date']), 2))
    df2 = pd.DataFrame(arr2, columns=['date', 'net'])
    df2['date'] = tmp_data2['date']
    df2['net'] = tmp_data2['net_value']
    df2 = df2.dropna()
    #print(df2)
    df1.set_index(df1['date'],inplace=True)
    df2.set_index(df2['date'],inplace=True)
    df_sus = pd.merge(df1, df2, how='outer', on=None, left_on=None, right_on=None, left_index=True, right_index=True,
                    sort=False)
    df_sus=df_sus.drop(columns=['date_x'])
    df_sus=df_sus.drop(columns=['date_y'])
    df_sus=df_sus.dropna()
    if tmpstock.split('.')[0]=='128015':
        print(csv_file)
        print(df1,df2,df_sus)
    df_sus.to_csv(csv_out_dir+"\\"+csv_file)



##2 遍历文件计算相关系数
dictpr_corr={}
dictiv_corr={}
#df1=pd.DataFrame(columns=['stock','pr_corr','iv_corr'])
filelist = os.listdir(csv_out_dir)  # 列出文件夹下所有的目录与文件
print(list)
for csvfile in filelist:
    pf=pd.read_csv(csv_out_dir+"\\"+csvfile)
    if(len(pf.index.values)==0):
        continue
    corr=pf.corr()
    print(corr)
    stock=csvfile.split('.')[0]
    if(len(corr['premium_rate'].values.tolist())==0):
        continue
    print(stock,corr['premium_rate'].values.tolist()[2], corr['iv'].values.tolist()[2])
    dictpr_corr[stock] = corr['premium_rate'].values.tolist()[2]
    dictiv_corr[stock] = corr['iv'].values.tolist()[2]
dfcorr=pd.DataFrame( {'pr_corr':dictpr_corr, 'iv_corr':dictiv_corr})
print(dfcorr)


dfcorr = dfcorr.sort_values(by="iv_corr",ascending=False)  # by指定按哪列排序。ascending表示是否升序
top10=dfcorr.head(11)
print(top10)

#for code in stocks:


#画图
for stock in top10.index.values:
    tmp_data2 = pd.read_csv(str(csv_out_dir) + '\\' + stock+'.csv')
    tmp_data2.set_index(tmp_data2['date'], inplace=True)
    tmp_data2=tmp_data2.drop(columns=['date'])
    tmp_data2=tmp_data2.dropna()
    #print(tmp_data2)

    tmp_data2.plot()
    #plt.title("相关性分析"+tmp_data2)
    plt.show()

print("end")

