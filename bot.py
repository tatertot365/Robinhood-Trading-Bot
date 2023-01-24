import robin_stocks.robinhood as r
from secrets import username, password
import datetime


def login():
    # This is the LOGIN function that requires a multi-factor authentication code from your phone
    # Login expires in 24 hours
    r.login(username, password, expiresIn=86400, by_sms=True)


def checkPositions():
    # This gets basic user information as a dictionary then 2 dictionary items are subtracted to find out how much money is actually invested
    positionDic = r.account.build_user_profile()
    totalInvested = float(positionDic["equity"]) - float(positionDic["cash"])
    # returns amount of money invested as a float
    return totalInvested


def listSymbols():
    # function to get the ticker symbols for any list of stocks in your account
    currentListSym = []
    # Enter the name of the list you would like to get the ticker symbols for here
    listName = 'My First List'
    # Creates an array with the ticker symbols of all of the stocks in your list
    for i in range(len(r.account.get_watchlist_by_name(name=listName, info="results"))):
        currentListSym.append(r.account.get_watchlist_by_name(name=listName, info="results")[i]["symbol"])
    # Returns the ticker symbols as an array/list of strings
    return currentListSym


def calcAvg(SymbolsList):
    # Creats 2 lists, one that gets the highest weekly price of each stock in the list over a year, and the other get the lowest weekly price of each stock over a year
    stockListHigh = r.stocks.get_stock_historicals(SymbolsList, interval='week', span='year', bounds='regular',
                                                   info='high_price')
    stockListLow = r.stocks.get_stock_historicals(SymbolsList, interval='week', span='year', bounds='regular',
                                                  info='low_price')

    # 3 variables are declared,
    # one is the year high price for each stock
    # the other is the count of how many high prices the loop as gone through
    # Array of the highest price for each stock during the year is created
    yearHighPrice = 0.0
    count = 1
    listHighPrices = []
    # Loop to find the highest price for each stock over a year
    # That price is then appended to the array of highest year price for each stock
    for j in range(len(stockListHigh)):
        if float(stockListHigh[j]) > float(yearHighPrice):
            yearHighPrice = float(stockListHigh[j])
        if count == 52:
            listHighPrices.append(yearHighPrice)
            count = 0
            yearHighPrice = 0.0
        count = count + 1

    # Same thing is done here but with the low prices for each stock over the course of a year
    yearLowPrice = 0.0
    count = 1
    listLowPrices = []
    # lowest stock price for each stock is found over the year and then appended to the lowest year price array
    for k in range(len(stockListLow)):
        if float(stockListLow[k]) > float(yearLowPrice):
            yearLowPrice = float(stockListLow[k])
        if count == 52:
            listLowPrices.append(yearLowPrice)
            count = 0
            yearLowPrice = 0.0
        count = count + 1

    # Average price array is created to hold the rolling average price of the year for each stock
    avgPriceArray = []
    # Average price for each stock is calculated and then appended to an array of average prices
    for l in range(len(listHighPrices)):
        avgPriceArray.append((listHighPrices[l] + listLowPrices[l]) / 2)

    # Array holding the average rolling year price for each stock in the list is returned
    return avgPriceArray


def percentDifPrice(AverageArray, stockList):
    # This function takes the array of average prices and the array containing the ticker symbols for each stock as parameters
    # The function calculates if a stock should be bought based on what percetage of its average year price the stock is trading at
    # Array is created that contains the last traded price of every stock in the stockList
    currentListPrices = r.stocks.get_quotes(stockList, info='last_trade_price')

    # We have an boolean array that will contain say whether or not each stock in the list should be bought
    buyOrNotArray = []

    # We set an upperbound and lowerbound percentage to see if the stock should be bought
    # I.E. If the stock is between 70% and 95% of its year average price then it should be bought
    PercentDifferenceHigh = 95.00
    PercentDifferenceLow = 70.00
    for i in range(len(AverageArray)):
        if PercentDifferenceHigh >= ((float(currentListPrices[i]) * 100) / AverageArray[i]) >= PercentDifferenceLow:
            buyOrNotArray.append(True)
        else:
            buyOrNotArray.append(False)

    # returns a boolean array that says whether each stock should be purchase or not
    return buyOrNotArray


def buyStocks(buyTOrF, symbolsList):
    # This function is where stocks are bought by a dollar amount based on the buy or not boolean array calculated above
    # It takes the buy or not boolean array and the list of the ticker symbols as parameters
    # The amount bought of each stock in dollars is declared and can be charnged below
    amountInDollars = 10

    # This loop goes through and buy each item in the array marked TRUE based on ticker synbol and amountInDollars
    for i in range(len(buyTOrF)):
        if checkPositions() < 1000.00 and buyTOrF[i] == True:
            # Actual buy statement is commented out until you want the bot to actually buy stocks
            # r.orders.order_buy_fractional_by_price(symbolsList[i], amountInDollars, timeInForce='gfd', extendedHours=False, jsonify=True)
            shareAmount = 10 / float(
                r.stocks.get_latest_price(symbolsList[i], priceType=None, includeExtendedHours=True)[0])
            print('bought ' + str(shareAmount) + " for " + str(symbolsList[i]))


def sellStocks(SymbolsList):
    # This functions determines if stocks should be sold based on average buy price and average bid price
    # Takes the list of ticker symbols as a parameter
    for i in range(len(SymbolsList)):
        # Checks to see if ticker symbol is in the list of open psotions held by the user
        if SymbolsList[i] in r.account.build_holdings(with_dividends=False):
            # Quantity of the stock and the average buy price of the stock is retrieved
            quantity = float(r.account.build_holdings(with_dividends=False)[SymbolsList[i]]['quantity'])
            avgBuyPrice = float(r.account.build_holdings(with_dividends=False)[SymbolsList[i]]['average_buy_price'])

            # The list of bid prices for the stock are retrieved
            bidPriceArray = r.stocks.get_latest_price(SymbolsList[i], priceType='bid_price', includeExtendedHours=False)
            askPriceArray = r.stocks.get_latest_price(SymbolsList[i], priceType='ask_price', includeExtendedHours=False)
            totalBidPrice = 0
            totalAskPrice = 0

            # Sum of all the bid prices for the stock
            for j in bidPriceArray:
                totalBidPrice = totalBidPrice + float(j)
            for j in askPriceArray:
                totalAskPrice = totalAskPrice + float(j)

            # average bid price of the stock is calculated
            avgBidPrice = totalBidPrice / len(bidPriceArray)
            avgAskPrice = totalAskPrice / len(askPriceArray)

            # 15% difference in avg buy price is calculated
            priceDifSell = .85 * avgBuyPrice

            # If average buy prie is less than the average bid price a market order is placed for the entire user owned quantity of the stock
            if (avgBuyPrice < avgBidPrice):
                # r.orders.order_sell_fractional_by_quantity(SymbolsList[i], quantity, timeInForce='gfd', extendedHours=False, jsonify=True)
                print('sold ' + str(quantity) + " shares " + str(SymbolsList[i]) + " with avg buy price of " + str(
                    avgBuyPrice) + " and an avg bid price of " + str(avgBidPrice))

            # If there is a 15% difference between the average bid price and the average buy price a market order is places for the entire user owned quantity of the stock to stop losses
            elif (avgAskPrice <= priceDifSell):
                # actual sell order is commented out until user wants to actually sell
                # r.orders.order_sell_fractional_by_quantity(SymbolsList[i], quantity, timeInForce='gfd', extendedHours=False, jsonify=True)
                print('sell to stop loss ' + str(SymbolsList[i]) + " number of shares sold: " + str(
                    quantity) + " with avg buy price of " + str(avgBuyPrice) + " and avg ask price of " + str(
                    avgAskPrice))


def logout():
    # This function logs the user out of robinhood
    r.logout()


# Bot begins
# User must login first
login()

# Buy inherently set to false
Buy = False

# If the amount of money in the stock market is less than 1000 dollars and amount of available cash to invest is enough to iterate through the list of stocks
if checkPositions() < 1000.00 and (float(r.account.build_user_profile()['cash']) > (len(listSymbols()) * 10)):
    Buy = True

if Buy == True:

    # Each iteration of the loop is checked to make sure that there is enough money to invest and not too much is invested
    while (checkPositions() < 1000.00) and (float(r.account.build_user_profile()['cash']) > (len(listSymbols()) * 10)):

        # Time is checked to make sure that the bot doesn't try to invest when stock market is closed
        now = datetime.datetime.now()
        today2pm = now.replace(hour=14, minute=0, second=0, microsecond=0)

        # While time is less than 2 pm MST the bot will keep trying to invest
        if now < today2pm:

            # Bot iterates through all of the functions of buying and selling
            arrayOfSymbolsInList = listSymbols()
            listOfPriceAvg = calcAvg(arrayOfSymbolsInList)
            buyOrNotArray = percentDifPrice(listOfPriceAvg, arrayOfSymbolsInList)
            buyStocks(buyOrNotArray, arrayOfSymbolsInList)
            sellStocks(arrayOfSymbolsInList)

        # If it is 2 pm MST or after 2 om MST than Buy is set to True and the loop stops running
        else:
            Buy = False
            break

# now is redefined and today at 2 pm MST should be the end of investing for the day
now = datetime.datetime.now()
today2pm = now.replace(hour=14, minute=0, second=0, microsecond=0)

# This is the loop that will keep going until it is 2 pm MST
while now < today2pm:
    # Will keep seeing if it should sell the current stock positions until 2 pm MST
    arrayOfSymbolsInList = listSymbols()
    sellStocks(arrayOfSymbolsInList)

    # Now is redefined to keep seeing if it is before 2 pm
    now = datetime.datetime.now()

# logs out the user at the end of trading
logout()

'''def buyBTCsetLimitSellOrder ():
    symbol = "BTC"
    amountInDollars = 10
    r.orders.order_buy_crypto_by_price(symbol, amountInDollars, timeInForce='gtc')
    boughtPrice = round(Decimal(r.orders.get_all_crypto_orders(info=None)[0]('price')), 0)
    limitPrice = boughtPrice + 10
    quantity = r.orders.get_all_crypto_orders(info=None)[0]('quantity')
    print('Bought BTC')
    sleep(5)
    r.orders.order_sell_crypto_limit(symbol, quantity, float(limitPrice), timeInForcce='gtc')
    print('Sold BTC')'''

'''stockListHigh = r.stocks.get_stock_historicals(currentListSym, interval='week', span='year', bounds='regular', info='high_price')
difArray = []
for l in range(len(stockListHigh)):
    difArray.append(float(stockListHigh[l]) - float(stockListLow[l]))

count = 1
avg = 0
avgArray = []
for k in difArray:
    avg = (avg + float(k))
    count = count + 1
    if count == 52:
        avgArray.append(avg/52)
        count = 1
        avg = 0'''
