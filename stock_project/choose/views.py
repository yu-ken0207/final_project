from django.shortcuts import render
from choose.forms import efgh
from django.http import HttpResponse
import plotly.express as px
import datetime 
import requests
import pandas
import json
from numpy.core._simd import targets
from bs4 import BeautifulSoup
from transformers import BertTokenizer, TFBertForSequenceClassification
from transformers import InputExample, InputFeatures
import tensorflow as tf
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import time
#下載新聞標題及內容到電腦磁碟
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import requests
import numpy as np
import matplotlib
import matplotlib.pyplot as plt   
import yfinance as yf
from pandas_datareader import data as pdr
import datetime
import numpy  as np
import plotly.graph_objs as go
import plotly.offline as opy
from urllib.request import urlopen
import pandas as pd
import datetime
import requests
import sched
import math     
    

def choose(request):
    dtime = int(float(time.time())*1000)
    url = 'https://mis.twse.com.tw/stock/data/mis_ohlc_TSE.txt?_='+str(dtime)
    res = requests.get(url)
    jd = res.json()['ohlcArray']
    columns = ['c','s','ts','t']
    df = pd.DataFrame(jd, columns=columns)
    df.columns =['加權指數','成交金額','時間','日期']
    df['加權指數'] = pd.to_numeric(df['加權指數'])
    df['成交金額'] = df['成交金額'].astype(float)
    df['時間']=df['時間'].replace(np.nan,'133000')
    yesterday =res.json()['infoArray']
    df2=pd.DataFrame([yesterday[0]['y'], 0 , '0900' ,np.nan]).T
    #df.loc[0]=[yesterday[0]['y'], 0 , '0900' ,np.nan]
    df2.columns =df.columns
    df=pd.concat([df2,df],axis=0,ignore_index=True)
    allMoney=0
    for i in range(len(df['加權指數'])):#注意
            df['時間'][i]=df['時間'][i][0:2]+':'+df['時間'][i][2:4] 
            df['成交金額'][i]=df['成交金額'][i]/100 
            allMoney+=df['成交金額'][i]
            allMoney=round(allMoney,2)
    abc=str(df['加權指數'][len(df['加權指數'])-1])
    
    trace1 = go.Bar(
        name='成交金額(億)',
        x=df['時間'],
        y=df['成交金額'],
    )
    trace2 = go.Scatter(
        name='加權指數',
        x=df['時間'],
        y=df['加權指數'],
        yaxis="y2"
    )
    
    data = [trace1, trace2,]
    layout = go.Layout(
        yaxis=dict(
            domain=[0, 0.5]
        ),
        legend=dict(
            traceorder="reversed"
        ),
        yaxis2=dict(
            domain=[0.5, 1]
        ),
        title='加權指數:'+abc,
    )
    fig =go.Figure(data=data, layout=layout)
    fig.update_xaxes(tick0='0900',dtick=5)
    fig.update_yaxes(exponentformat="none")
    fig.update_layout(hovermode="x unified",width=1000,height=600)
    div = opy.plot(fig, auto_open=False, output_type='div')
    url='https://tw.stock.yahoo.com/tw-market'
    list_req = requests.get(url)
    soup = BeautifulSoup(list_req.content, "html.parser")
    d=[]
    i=0
    f=0
    for a in soup.find_all('h3',{'class':'Mt(0) Mb(8px)'}):
        d.append([a.text,a.a.get('href')])
        i+=1
        if i == 10:
            break
    for b in soup.find_all('p',{'class':'Fz(16px) Lh(24px) LineClamp(2,48px) C($c-secondary-text) M(0)'}):
        d[f].append(b.text)
        f+=1
        if f == 10:
            break
    return render(request,'choose/choose.html',{'fig':div,'d':d})
def timely_stock(request):
    get_text=request.GET.get("stock")
    request.session['stock']=get_text
    today = datetime.datetime.now() 
    nowtime=" 更新時間:" + today.strftime('%X')[0:5]
    #nowtime=" 更新時間:" + str(time.hour)+":"+str(time.minute)+'///'+str(time.time)
    with open('test3.json',encoding="utf_8") as f:
            data = json.load(f)
    for i in range(len(data)-1):
        if get_text == data[i]['name']:
            targets=data[i]['stock']
            title_text=targets+' '+get_text
        elif get_text ==data[i]['stock']:
            targets=get_text
            stock_name=data[i]['name']
            title_text=targets+' '+stock_name
    res = requests.get('https://tw.stock.yahoo.com/_td-stock/api/resource/FinanceChartService.ApacLibraCharts;autoRefresh=1653627795519;symbols=%5B%22'+targets+'.TW%22%5D;type=tick?bkt=&device=desktop&ecma=modern&feature=ecmaModern%2CuseVersionSwitch%2CuseNewQuoteTabColor&intl=tw&lang=zh-Hant-TW&partner=none&prid=a3olkn1h90moe&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1295&returnMeta=true')
    jd = res.json()['data']
    close = jd[0]['chart']['indicators']['quote'][0]['close']
    volume = jd[0]['chart']['indicators']['quote'][0]['volume']
    timestamp = jd[0]['chart']['timestamp']
    df = pandas.DataFrame({'timestamp':timestamp, '價':close, 'volume':volume,},)
    df['日期']=(pandas.to_datetime(df['timestamp'] + 3600 * 8, unit='s'))
    df['日期']=pandas.to_datetime(df['日期'],format ='%Y-%m-%d%H:%M')
    df['時間']=df['日期'].dt.strftime("%H:%M")
    
    fig = px.line(df,x='時間',y ='價',title=title_text+nowtime,line_shape='linear',hover_data={'量':df.volume},width=1000)
    fig.update_xaxes(title_text='時間')
    fig.update_yaxes(title_text='價格')
    fig.update_layout(hovermode="x")
    fig.update_traces(connectgaps=True)
    #newfig="<div>"+fig.to_html()+"</div>"
    
    res = requests.get('https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.stockList;autoRefresh=1653805943474;fields=avgPrice%2Corderbook;symbols='+targets+'.TW;version=v1?bkt=Test-P13N-author-V2&device=desktop&ecma=modern&feature=ecmaModern%2CuseVersionSwitch%2CuseNewQuoteTabColor%2CuseFinanceP13NStreamV2&intl=tw&lang=zh-Hant-TW&partner=none&prid=ago6ti1h964nt&region=TW&site=finance&tz=Asia%2FTaipei&ver=1.2.1295&returnMeta=true')
    jd = res.json()['data']
    
    one = jd[0]['orderbook'][0]
    two = jd[0]['orderbook'][1]
    three = jd[0]['orderbook'][2]
    four = jd[0]['orderbook'][3]
    five = jd[0]['orderbook'][4]
    
    cd = pandas.DataFrame({'one':one, 'two':two, 'three':three,'four':four,'five':five,},)
    cd =cd.T
    cd.columns=['委賣價','委賣量1','委買價','委買量1','委賣量','委買量']

    
    
    fig2 = px.bar(cd,
                 title="委買",
                 x="委買量",
                 y="委買價",
                 hover_data = ['委買量','委買價'],   # 懸停參數
                 width=250,
                 height=300,
                 orientation='h',
                )
    x_maxs = []
    for trace_data in fig2.data:
        x_maxs.append(max(trace_data.x))
    x_max = max(x_maxs)
    fig2.update_layout(yaxis={"mirror" : "allticks", 'side': 'right'},xaxis={'range': [1.05*x_max, 0], 'side': 'bottom'} ,title_text='委買',title_x=0.5 )
    
    #newfig+="<div>"+fig2.to_html()+"</div>"
    fig3 = px.bar(cd,
                 title="委賣",
                 x="委賣量",
                 y="委賣價",
                 hover_data = ['委賣量','委賣價'],   # 懸停參數
                 width=250,
                 height=300,
                 orientation='h',
                )
    fig3.update_layout(title_text='委賣', title_x=0.5)
    #newfig+="<div id='five'>"+"<div>"+fig2.to_html()+"</div>"+"<div>"+fig3.to_html()+"</div>"+"</div>"
    
    
    res = requests.get("https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_"+targets+".tw&json=1&delay=0&_=1552123547443")
    data2 = res.json()['msgArray']
    # 過濾出有用到的欄位
    columns = ['c','n','z','tv','v','o','h','l','y']
    gh = pandas.DataFrame(data2, columns=columns)
    gh.columns = ['股票代號','公司簡稱','當盤成交價','當盤成交量','累積成交量','開盤價','最高價','最低價','昨收價']
    gh.insert(9, "漲跌百分比", 0.0) 
    # 新增漲跌百分比
    if gh['當盤成交價'].iloc[0] != "-":
        gh.iloc[0, [2,8]] = gh.iloc[0, [2,8]].astype(float)
        gh['漲跌百分比'].iloc[0] = (gh['當盤成交價'].iloc[0] - gh['昨收價'].iloc[0])/gh['昨收價'].iloc[0] * 100
       
    #三大法人
    ef = pd.DataFrame()
    today = datetime.date.today()
    strToday=str(today)
    day = strToday[:4]+strToday[5:7]+strToday[8:]
    
    while True:
        url = 'https://www.twse.com.tw/fund/T86?response=json&date=' + day + '&selectType=ALL'
        res = requests.get(url)
        inv_json = res.json()
        if res.json()['stat'] == '很抱歉，沒有符合條件的資料!':
            end_time= str(today-datetime.timedelta(days=1))
            day= end_time[:4]+end_time[5:7]+end_time[8:]
        elif res.json()['stat'] == 'OK':
            ef_inv = pd.DataFrame.from_dict(inv_json['data'])
            ef_inv.insert(0, '日期', datetime.datetime(int(day[:4]), int(day[4:6]), int(day[6:])))
            ef = ef.append(ef_inv, ignore_index = True)
            break
    ef.columns = ['日期', '證券代號', '證券名稱', '外陸資買進股數(不含外資自營商)', '外陸資賣出股數(不含外資自營商)', '外陸資買賣超股數(不含外資自營商)', '外資自營商買進股數', '外資自營商賣出股數', '外資自營商買賣超股數', '投信買進股數', '投信賣出股數', '投信買賣超股數', '自營商買賣超股數', '自營商買進股數(自行買賣)', '自營商賣出股數(自行買賣)', '自營商買賣超股數(自行買賣)', '自營商買進股數(避險)', '自營商賣出股數(避險)', '自營商買賣超股數(避險)', '三大法人買賣超股數']
    ef=ef.drop(columns= ['外陸資買進股數(不含外資自營商)', '外陸資賣出股數(不含外資自營商)', '外資自營商買進股數', '外資自營商賣出股數', '外資自營商買賣超股數', '投信買進股數', '投信賣出股數', '自營商買進股數(自行買賣)', '自營商賣出股數(自行買賣)', '自營商買賣超股數(自行買賣)', '自營商買進股數(避險)', '自營商賣出股數(避險)', '自營商買賣超股數(避險)', '三大法人買賣超股數'])
    
    # 加入股票代碼篩選
    if targets == None:
        pass
    else:
        ef = ef[ef['證券代號'] == str(targets)]
    
    
    for col in range(3, 6):
        for row in range(ef.shape[0]):
                ef.iloc[row, col] = float(ef.iloc[row,col].replace(',', ''))
                ef.iloc[row, col] = round(math.floor(ef.iloc[row,col])/1000)
    
            
    headers = {
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'  
    }
    
    res3 = requests.get('https://goodinfo.tw/tw/StockDirectorSharehold.asp?STOCK_ID='+targets+'', headers = headers)
    
    res3.encoding = 'utf-8'
    
    soup = BeautifulSoup(res3.text, 'lxml')
    data3 = soup.select_one('#divDetail')
    dfs = pandas.read_html(data3.prettify())
    
    dfs = dfs[0]
    dfs.columns = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','董監持股比例(%)','18','19','20','外資持股比例(%)']
    
    
    dfs2 =  dfs.drop(['2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','18','19','20'],axis = 1)
    #print(dfs2)
    
    gh.insert(10, '董監持股比例(%)', dfs2['董監持股比例(%)'][1]) 
    gh.insert(11, '外資持股比例(%)', dfs2['外資持股比例(%)'][1]) 
    
    
    newfig="<div id='five'>"+"<div>"+fig.to_html()+"</div>"+"<div>"+fig2.to_html()+"</div>"+"<div>"+fig3.to_html()+"</div>"+"</div>"+"<div>"+gh.to_html(index=False)+"</div>"+"<div>"+ef.to_html(index=False)+"</div>"
    output_dir = './model_save1/'
    
    os.chdir(r'C:\Users\sleep\Desktop') 
    
    model =TFBertForSequenceClassification.from_pretrained(output_dir )
    tokenizer = BertTokenizer.from_pretrained(output_dir)
    
    
    res = requests.get("http://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    
    
    
    df = pandas.read_html(res.text)[0]
    #print(df[0])
    
    stock_code=targets
    code = []  #數字代碼
    for i in range(2,len(df)):
        if df[5][i] =='ESVUFR':
            code.append(df[0][i][0:4])
        #print(df[0][i][0:4])
        
    code_1 = []  #中文名稱
    for i in range(2,len(df)):
        if df[5][i] =='ESVUFR':
            code_1.append(df[0][i][5:])
        #print(df[0][i][0:4])
    stock=[]
    for i in range(1,len(code)):
        if stock_code == code[i]:
            stock.append(stock_code)
            stock.append(code_1[i]) 
    #print(code)
    #print(code_1)
    #print(stock)
    
    #主程式主程式主程式主程式主程式主程式主程式主程式主程式主程式主程式主程式主程式主程式
     # 要抓取的網址
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
    url="https://tw.stock.yahoo.com/quote/"+stock_code+"/news"
    #print(url)
    
      #請求網站
    list_req = requests.get(url, headers=headers)
      #將整個網站的程式碼爬下來
    soup = BeautifulSoup(list_req.content, "html.parser")
      #找到b這個標籤
        
    now =time.localtime()  #當日時間
    now = str(now.tm_year)+'年'+str(now.tm_mon)+'月'+ str(now.tm_mday)+'日' 
    num=now.find('日')
    for a in soup.find_all('h3',{'class':'Mt(0) Mb(8px)'},limit=5):
          if stock[1] in a.text:#中文代碼
            url = a.a.get('href')
            list_req = requests.get(url)
            soup1 = BeautifulSoup(list_req.content, "html.parser")
            getAllNew= soup1.find('div',{'class':'caas-body'}) 
            gettime= soup1.find('time',{'class':'caas-attr-meta-time'})
            
    response = requests.get("https://tw.stock.yahoo.com/quote/"+stock_code+"/news")
    soup = BeautifulSoup(response.text, "html.parser")            
    stock_name=stock[1]
    b=0
    newData=[]
    
    for a in soup.find_all('h3',{'class':'Mt(0) Mb(8px)'}):
        if stock_name in a.text:
            #print(a.a.get('href'))
            #print(a.text)
            url = a.a.get('href')
            list_req = requests.get(url)
            soup1 = BeautifulSoup(list_req.content, "html.parser")
            getAllNew= soup1.find('div',{'class':'caas-body'}) 
            gettime= soup1.find('time',{'class':'caas-attr-meta-time'}) #抓日期
            #print(getAllNew.text+'\n')
            #f.write(a.text+'\n')             #標題
            newData.append([a.text,gettime.get_text('datetime')[0:10],getAllNew.text,(url)])  
            b+=1
            if b>=5:
                break
    for f in range(5):
        pre_text= [newData[f][2]]
        tf_batch = tokenizer(pre_text[0][11:], max_length=128, padding=True, truncation=True, return_tensors='tf')
        tf_outputs = model(tf_batch)
        tf_predictions = tf.nn.softmax(tf_outputs[0], axis=-1)
        labels = ['5','4','3','2','1']  #5最好 1最差
        label = tf.argmax(tf_predictions, axis=1)
        label = label.numpy()
        for i in range(5):
            newData[f].append(labels[label[i]])
            break
    return render(request,'choose/asd.html',{'newfig':newfig,'newData':newData})#,content_type='html',content_type='text'

def choose2(request):
    return render(request,'choose/choose2.html',{'who':efgh(),'stock':request.session['stock']})
def choose2_submit(request):
    start_time = request.GET["start_time"]
    end_time = request.GET["end_time"]
    stock=request.session['stock']
    stock_name = stock+'.TW'
    start = start_time
    end = end_time
    
    title=start_time+'~'+end_time
    # 下載股價資訊
    try:
        df_full = pdr.get_data_yahoo(stock_name, start=start, end=end).reset_index()
        df_full.to_csv(stock_name+'股價'+'.csv',index=False)
    except:
        print("no")
    
    
    df = pandas.read_csv(stock_name+'股價.csv')
    
    
    #2
    df['MA5']  = df['Close'].rolling(5).mean()
    df['MA10'] = df['Close'].rolling(10).mean()
    
    
    stock_without_nan = df.copy()
    stock_without_nan = stock_without_nan.dropna()
    
    stock_without_nan['cross'] = np.where(stock_without_nan['MA5'] > stock_without_nan['MA10'], 1, 0)
    stock_without_nan['DIRECTION'] = stock_without_nan['cross'].diff()
    
    stock_without_nan = stock_without_nan.reset_index(drop=True)
    #3
    gold = pandas.DataFrame()
    dead = pandas.DataFrame()
    
    for i in range(len(stock_without_nan)):
        if    stock_without_nan.at[i,'DIRECTION'] == 1.0 :
                gold.loc[i-1,'Date'] = stock_without_nan.at[i-1,'Date']
                gold.loc[i-1,'MA5']  = stock_without_nan.at[i-1,'MA5']
        elif  stock_without_nan.at[i,'DIRECTION'] == -1.0 :
                dead.loc[i-1,'Date'] = stock_without_nan.at[i-1,'Date']
                dead.loc[i-1,'MA5']  = stock_without_nan.at[i-1,'MA5']
    #4
    candlestick = go.Candlestick(x=df['Date'],
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close'],
                                 increasing_line_color='red',
                                 decreasing_line_color='green',
                                 name = 'k線圖')
    
    ma5_scatter = go.Scatter(x=df['Date'], 
                             y=df['MA5'],
                             line=dict(color='orange', width=1),
                             mode='lines',
                             name = 'MA5')
    
    ma20_scatter = go.Scatter(x=df['Date'],
                              y=df['MA10'],
                              line=dict(color='blue', width=1),
                              mode='lines',
                              name = 'MA10')
    
    if gold.empty or dead.empty:
        print ('no')
        fig = go.Figure(data=[candlestick, ma5_scatter, ma20_scatter])
    else:
        graph_gold = go.Scatter(x= gold['Date'], 
                                y= gold['MA5'] , 
                                mode='markers', 
                                marker_symbol="x", 
                                marker_color="gold", 
                                marker_size=15, 
                                name='黃金交叉')
    
        graph_dead = go.Scatter(x= dead['Date'], 
                                y= dead['MA5'] , 
                                mode='markers', 
                                marker_symbol="x", 
                                marker_color="black", 
                                marker_size=15, 
                                name='死亡交叉')
        fig = go.Figure(data=[candlestick, ma5_scatter, ma20_scatter,graph_gold,graph_dead])
    
    fig.update_layout(xaxis_rangeslider_visible=False)
    div = opy.plot(fig, auto_open=False, output_type='div')
    return render(request,'choose/choose2.html',{'who':efgh(),'stock':stock,'title':title,'fig':div})