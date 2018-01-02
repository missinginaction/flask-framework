from flask import Flask, render_template, request, redirect
import pandas as pd
import datetime as dt
import os
import requests
from bokeh.plotting import figure, show, output_file, save
#from bokeh.io import output_file
from bokeh.models import DatetimeTickFormatter

output_file("templates/stock.html")

app = Flask(__name__)



@app.route('/index',methods=['GET','POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html')
  else:
    #request was a POST
    tickerstr = request.form['ticker']
    
    #api key=vbQvHK9QHerxvz75i_RT
    apikeystr = 'vbQvHK9QHerxvz75i_RT'

    #get date today
    today=dt.date.today()
    todaystr = today.strftime('%Y%m%d')

    #get date month before
    monthago = today - dt.timedelta(days=30)
    monthagostr = monthago.strftime('%Y%m%d')

    stockparams = {'date.lt':todaystr, 
                   'date.gte':monthagostr,
                   'ticker':tickerstr,
                   'api_key':apikeystr,
                   #'qopts.columns':"ticker,date,open,close,adj_open,adj_close"
                  }

    r = requests.get('https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json', params=stockparams)

    #put json data in a pandas dataframe
    df = pd.read_json(r.url+'&qopts.columns=ticker,date,open,close,adj_open,adj_close')

    #get column headers from dataframe
    coldicts = df.loc['columns','datatable']
    stockcolumns = [dict['name'] for dict in coldicts]

    stockdf = pd.DataFrame(df.loc['data','datatable'],columns = stockcolumns)
    stockdf.date = pd.to_datetime(stockdf.date,infer_datetime_format=True)
    
    p = figure(title="Closing Prices for %s" %tickerstr)
    p.xaxis.formatter=DatetimeTickFormatter(
                                            hours=["%Y %m %d"],
                                            days=["%Y %m %d"],
                                            months=["%Y %m %d"],
                                            years=["%Y %m %d"]
                                           )
    p.line(stockdf.date, stockdf.close, line_width=4)
    p.xaxis[0].axis_label = 'Date'
    p.yaxis[0].axis_label = 'Stock price at close (USD)'

    save(p)


    return render_template('stock.html')
    
    
if __name__ == '__main__':
  #app.run(port=33507)
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)
