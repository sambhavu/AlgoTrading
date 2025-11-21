import yfinance as yf
import robin_stocks
from robin_stocks import *
import robin_stocks.robinhood as r
import os
import pandas
from easygui import passwordbox

class RobinHood:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        try:
            login = r.login(self.username, self.password)
            print("Login Successful")

        except:
            print("Login Failed...")

    def GetStockPrice(self, ticker):
        Data = yf.Ticker(ticker).history(period = '5y', frequency = '1d')
        Close = Data['Close'].values
        return Close[-1]

    def BuyFractionalMarket(self, ticker, numdollars):
        try:
            LastClose = self.GetStockPrice(ticker)
            numshares = self.GetPartialShare(LastClose, numdollars)
            r.order_buy_fractional_by_quantity(ticker, numshares)
            print("Order Successful for ", ticker)
        except:
            print("Failed to Buy Shares of ", ticker)


    def GetCurrentPositions(self):

        stocks = r.markets.get_all_stocks_from_market_tag('technology')


        print(len(stocks))
        for stock in stocks:
            print(stock['symbol'], " ", stock['last_trade_price'])

    def GetPartialShare(self, stock_price, capital_deposit):
        return capital_deposit/stock_price





def main():

    print("Enter Robinhood Credentials & Two Factor Identification")
    #robinhood_email = input("EMAIL: ")
    #robinhood_password = passwordbox("PASSWORD: ")



    u = ""
    p = ""
    rh = RobinHood(u,p)




    rh.login()

    rh.GetCurrentPositions()


main()
