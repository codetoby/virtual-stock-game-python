import requests
import json
import datetime
from cs50 import SQL

db = SQL("sqlite:///users.db")
API_KEY = "pk_51d4c11c76f5449fa9515637d290e770"


def buy(ticker, shares, id):

    portfolio = db.execute("select cash from portfolio where id = ?", id)

    data = get_data(ticker)
    price = data[0]["latestPrice"]
    if price * shares > portfolio[0]["cash"]:
        return {"success": False, "reason": "not enough cash"}

    time = datetime.datetime.now()
    total = shares * price
    stocks = db.execute("select count(*) as count, * from stocks where id = ? and ticker = ?", id, ticker)
    if stocks[0]["count"] == 0:
        db.execute("insert into stocks (id, ticker, price, shares, date) VALUES(?, ?, ?, ?, ?)",
                   id, ticker, price, shares, time)
    else:

        stockShares = stocks[0]["shares"]
        stockPrice = stocks[0]["price"]
        stockTotal = int(stockShares) * float(stockPrice)
        averagePrice = (stockTotal + total) / (shares + stockShares)

        db.execute("update stocks set price = ?, shares = ?, date = ? where id = ? and ticker=?",
                   averagePrice, (stockShares + shares), time, id, ticker)

    db.execute("update portfolio set cash = cash + ? where id = ?", total, id)
    insertHistory(id, ticker, price, shares, time, "buy")
    return {"success": True}


def sell(ticker, shares, id):
    
    stocks = db.execute("select count(*) as count, * from stocks where id = ? and ticker = ?", id, ticker)
    if stocks[0]["count"] == 0:
        return {"success": False, "reason": "stock not found in portfolio"}
    elif stocks[0]["shares"] < shares:
        return {"success": False, "reason": "you do not have these many shares"}
    
    time = datetime.datetime.now()
    
    data = get_data(ticker)
    price = data[0]["latestPrice"]
    total = price * shares
    
    db.execute("update stocks set shares = ?, date = ? where id = ? and ticker = ?", (stocks[0]["shares"] - shares), time,  id, ticker)
    insertHistory(id, ticker, price, shares, time, "sell")
    return {"success": True}
    
        
def get_data(ticker):

    url = f"https://api.iex.cloud/v1/data/core/quote/{ticker}?token={API_KEY}"

    resp = requests.get(url)
    return json.loads(resp.content)


def insertHistory(id, ticker, price, shares, time, orderType):
    
    return db.execute("insert into history VALUES(?, ?, ?, ?, ?, ?)", id, orderType, ticker, shares, time, price)


def userportfolio(id):
    
    userStocks = []
    stocks = db.execute("select * from stocks where id = ?", id)
    for stock in stocks:
        
        ticker = stock["ticker"]
        data = get_data(ticker)[0]
        
        append = {
            "symbol": ticker.upper(),
            "name": data["companyName"],
            "shares": stock["shares"],
            "price": data["latestPrice"],
            "profit": (data["latestPrice"] - stock["price"]) * stock["shares"]
        }
        userStocks.append(append)
        
    return userStocks