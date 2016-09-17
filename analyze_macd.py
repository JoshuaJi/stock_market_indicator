#coding=utf-8
import tushare as ts
import talib as ta
import numpy as np
import pandas as pd
import os,time,sys,re,datetime
import csv
import scipy
import smtplib
from sklearn import svm
from email.mime.text import MIMEText
from email.MIMEMultipart import MIMEMultipart
 
#首先是获取沪深两市的股票列表
#这里得到是对应的dataframe数据结构，它是类似于excel中一片数据的数据结构，有这些列：code,代码 name,名称 industry,所属行业 area,地区 pe,市盈率 outstanding,流通股本 totals,总股本(万) totalAssets,总资产(万)liquidAssets,流动资产 fixedAssets,固定资产 reserved,公积金 reservedPerShare,每股公积金 eps,每股收益 bvps,每股净资 pb,市净率 timeToMarket,上市日期
def Get_Stock_List():
    df = ts.get_stock_basics()
    return df

def Get_Csv_Data(code):
    try:
        print code, " retrieved successfully"
        return pd.read_csv('/Users/xuji/Desktop/home_automation/stock_market_indicator/data/'+code+'.csv')
    except:
        price_list = ts.get_hist_data(code)
        price_list.to_csv('/Users/xuji/Desktop/home_automation/stock_market_indicator/data/'+code+'.csv')
        print code, " retrieved successfully"
        return pd.read_csv('/Users/xuji/Desktop/home_automation/stock_market_indicator/data/'+code+'.csv')


def Cast_Date(date):
    temp_date = [int(i) for i in date.split('-')]
    return datetime.date(temp_date[0], temp_date[1], temp_date[2])

def Validate_Dates(date):
    last_data_date = Cast_Date(date)
    today = datetime.date.today()
    tolerant_start_date = today - datetime.timedelta(3)
    if last_data_date > tolerant_start_date and last_data_date <= today:
        return True
    else:
        return False
 
def sk_predict(df_data):
    df = df_data
    features = []
    targets = []
    for x in xrange(0,df.shape[0]-21):
        features.append(np.array(df['close'][::-1][x:x+20]))
        if df['close'][::-1][x+21] > df['close'][::-1][x+20]:
            targets.append(1)
        else:
            targets.append(-1)
        

    features = np.array(features)
    targets = np.array(targets)

    clf = svm.SVC()
    clf.fit(features, targets)
    correct_prediction = (df['close'][::-1][-1:] > df['close'][::-1][-2:-1])
    sk_prediction = clf.predict(np.array(df['close'][::-1][-21:-1]))
    print "predicting"
    print correct_prediction[0]
    print sk_prediction[0]
    if sk_prediction[0] == 1:
        if correct_prediction[0]:
            return True
        else:
            return False
    elif (sk_prediction[0] == -1):
        if correct_prediction[0]:
            return False
        else:
            return True


#然后定义通过MACD判断买入卖出
def Get_MACD(df_Code):
    operate_array=[]
    for code in df_Code.index:

# 获取每只股票的历史价格和成交量 对应的列有index列,0 - 6列是 date：日期 open：开盘价 high：最高价 close：收盘价 low：最低价 volume：成交量 price_change：价格变动 p_change：涨跌幅
# 7-12列是 ma5：5日均价 ma10：10日均价 ma20:20日均价 v_ma5:5日均量v_ma10:10日均量 v_ma20:20日均量
        if df_Code.loc[code].timeToMarket == 0:
            continue
        df = Get_Csv_Data(code)
        try:
            dflen = df.shape[0]
        except:
            dflen = 0
        operate = 0
        if dflen>35 and Validate_Dates(df.head(1).date[0]):
            macd, macdsignal, macdhist = ta.MACD(np.array(df['close'][::-1]), fastperiod=12, slowperiod=26, signalperiod=9)
            
            SignalMA5 = ta.MA(macdsignal, timeperiod=5, matype=0)
            SignalMA10 = ta.MA(macdsignal, timeperiod=10, matype=0)
            SignalMA20 = ta.MA(macdsignal, timeperiod=20, matype=0)
#在后面增加3列，分别是13-15列，对应的是 DIFF  DEA  DIFF-DEA       
            df['macd']=pd.Series(macd[::-1],index=df.index) #DIFF
            df['macdsignal']=pd.Series(macdsignal[::-1],index=df.index)#DEA
            df['macdhist']=pd.Series(macdhist[::-1],index=df.index)#DIFF-DEA
            MAlen = len(SignalMA5)

            #2个数组 1.DIFF、DEA均为正，DIFF向上突破DEA，买入信号。 2.DIFF、DEA均为负，DIFF向下跌破DEA，卖出信号。
            if df.iat[0,13]>0:
                if df.iat[0,14]>0:
                    if df.iat[0,13]>df.iat[0,14]:
                        operate = operate + 1#买入
            else:
                if df.iat[0,14]<0:
                    if df.iat[0,13]:
                        operate = operate - 1#卖出
       
            #3.DEA线与K线发生背离，行情反转信号。
            if df.iat[0,7]>=df.iat[0,8] and df.iat[0,8]>=df.iat[0,9]:#K线上涨
                if SignalMA5[MAlen-1]<=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]<=SignalMA20[MAlen-1]: #DEA下降
                    operate = operate - 1
            elif df.iat[0,7]<=df.iat[0,8] and df.iat[0,8]<=df.iat[0,9]:#K线下降
                if SignalMA5[MAlen-1]>=SignalMA10[MAlen-1] and SignalMA10[MAlen-1]>=SignalMA20[MAlen-1]: #DEA上涨
                    operate = operate + 1
               
       
            #4.分析MACD柱状线，由负变正，买入信号。
            if df.iat[0,15]>0 and dflen >30 :
                for i in range(1,26):
                    if df.iat[i+1,15]<=0:#
                        operate = operate + 1
                        break
            #由正变负，卖出信号   
            if df.iat[0,15]<0 and dflen >30 :
                for i in range(1,26):
                    if df.iat[i+1,15]>=0:#
                        operate = operate - 1
                        break
               
        operate_array.append(operate)        
    df_Code['MACD']=pd.Series(operate_array,index=df_Code.index)   
    return df_Code



def cal_KDJ(df_Code):
    fav_stocks = pd.DataFrame(columns=df_Code.columns)
    for code in df_Code.index:
        if df_Code.loc[code].timeToMarket == 0:
            continue
        df = Get_Csv_Data(code)
        try:
            dflen = df.shape[0]
        except:
            dflen = 0
        operate = 0
        if dflen>35 and Validate_Dates(df.head(1).date[0]):
            slowk, slowd = ta.STOCH(np.array(df['high'][::-1]), np.array(df['low'][::-1]), np.array(df['close'][::-1]),
                                   fastk_period=9,
                                   slowk_period=3,
                                   slowk_matype=0,
                                   slowd_period=3,
                                   slowd_matype=0)
            slowk = slowk[-1]
            slowd = slowd[-1]
            slowj = 3*slowd - 2*slowk

            if slowk > slowd and slowk < 20:
                fav_stocks.loc[code] = df_Code.loc[code]
    return fav_stocks


 
#输出CSV文件，其中要进行转码，不然会乱码
def Output_Csv(df,Dist):
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    reload(sys)
    sys.setdefaultencoding( "gbk" )
    df.to_csv(Dist+CURRENTDAY+'stock.csv',encoding='gbk')#选择保存   
 
def Close_machine():
    o="c:\\windows\\system32\\shutdown -s"#########
    os.system(o)#########
   
#发送邮件
def Send_Mail (Message,Dist):
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    msg = MIMEMultipart()
   
    TODAY = datetime.date.today()
    CURRENTDAY=TODAY.strftime('%Y-%m-%d')
    att = MIMEText(open(Dist+CURRENTDAY+'stock.csv', 'rb').read(), 'base64', 'gb2312') #设置附件的目录
    att['content-type'] = 'application/octet-stream'
    att['content-disposition'] = 'attachment;filename="stock.csv"' #设置附件的名称
    msg.attach(att)
   
    content = str(Message) #正文内容
    body = MIMEText(content,'plain','GBK') #设置字符编码
    msg.attach(body)
    msgto = ['xx@126.com'] # 收件人地址多个联系人，格式['aa@163.com'; 'bb@163.com']
    msgfrom = 'xx@126.com' # 寄信人地址 ,
    msg['subject'] = 'Finish at '+CURRENTDAY  #主题
    msg['date']=time.ctime() #时间
    #msg['Cc']='bb@junbao.net' #抄送人地址 多个地址不起作用

    mailuser = 'xx'  # 用户名
    mailpwd = 'xx' #密码
    try:
        smtp = smtplib.SMTP()
        smtp.connect(r'smtp.126.com')# smtp设置
        smtp.login(mailuser, mailpwd) #登录
        smtp.sendmail(msgfrom, msgto, msg.as_string()) #发送
        smtp.close()
        print "success mail"
    except Exception, e:
        print e


time1 = time.time()       
df_Code = Get_Stock_List()
correct = 0
incorrect = 0
for code in df_Code.index:
    if df_Code.loc[code].timeToMarket == 0:
        continue
    df = Get_Csv_Data(code)
    try:
        dflen = df.shape[0]
    except:
        dflen = 0
    if dflen>35:
        try:
            TorF = sk_predict(df)
            if TorF:
                correct = correct+1
            else:
                incorrect = incorrect+1
        except:
            pass

print "correct: ", correct
print "incorrect: ", incorrect

#df = cal_KDJ(df)
#df = Get_MACD(df)
#print df.sort_values(['MACD'], ascending=[0])
print "took ", time.time() - time1, " seconds"



#-------------------------------todo-------------------------------
#大盘 j > kd, close > MA5 时交易
#本地csv，按需获取

# Dist = 'E:\\08 python\\Output\\'
# Output_Csv(df,Dist)
# #生成的csv文件中，macd列大于0的就是可以买入的，小于0的就是卖出的
# Send_Mail ('Finish TA',Dist)
# Close_machine()