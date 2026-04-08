
import requests
import datetime
import json
import os

from dotenv import load_dotenv, dotenv_values 

# get your API key here for free: https://fred.stlouisfed.org/docs/api/api_key.html

load_dotenv() 
API_KEY = os.getenv("API_KEY")
EXPECTED_MARKET_RETURN=10

def getRiskFreeRate_ERP(useLatest=None,specificDate=None, startTime=None, endTime=None):
    RFR_value = None
    ERP_value = None
    if (useLatest):
        res = requests.get(f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&sort=asc&api_key={API_KEY}&file_type=json")

        print("We are using latest data")
        period_RFR_dataContainer = json.loads(res.text)
        period_RFR_data = period_RFR_dataContainer["observations"]

        # EXPECTED_MARKET_RETURNis used as a long-term SPY return
        try:
            RFR_value = float(period_RFR_data[len(period_RFR_data) - 1]["value"])
            ERP_value = float(EXPECTED_MARKET_RETURN - RFR_value)
            print(f"Last item in period_RFR_data: {period_RFR_data[len(period_RFR_data) - 1]['date']}")
        except:
            pass
        
        return {
            "type": "latest",
            "RFR": RFR_value,
            "ERP": ERP_value
        }
    elif(startTime and endTime):    
        day = datetime.datetime.now().date()

        res = requests.get(f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&sort=asc&observation_start={startTime}&observation_end={endTime}&api_key={API_KEY}&file_type=json")

        period_RFR_dataContainer = json.loads(res.text)
        period_RFR_data = period_RFR_dataContainer["observations"]
        period_RFR_dataArray = []

        for i in range(0, len(period_RFR_data)):
            value = 0
            try:
                value = float(period_RFR_data[i]["value"])
                period_RFR_dataArray.append(value)
            except:
                pass
        
        medianERP = None
        medianRFR = None

        averageERP = None
        averageRFR = None

        periodLength = len(period_RFR_dataArray)

        # check for middle 
        if (periodLength % 2 == 0):
            # index first - periodLength // 2 & + 1
            medianRFR = (period_RFR_dataArray[periodLength // 2] + period_RFR_dataArray[periodLength // 2 + 1]) / 2
            medianERP = EXPECTED_MARKET_RETURN - medianRFR
        else:
            print(str(periodLength // 2))
            medianRFR = period_RFR_dataArray[periodLength // 2]
            medianERP = EXPECTED_MARKET_RETURN - medianRFR

        total = 0
        for i in range(0, len(period_RFR_dataArray)):
            total += period_RFR_dataArray[i]   
        averageRFR = total / periodLength

        averageERP = EXPECTED_MARKET_RETURN - averageRFR

        return {
            "type": "period",
            "medianERP": medianERP,
            "medianRFR": medianRFR,
            "averageERP": averageERP,
            "averageRFR": averageRFR
        }
    
    elif(specificDate and useLatest is False):
        specificDate_Number = datetime.datetime.strptime(specificDate, "%Y-%m-%d")
        oneDayEarlier = specificDate_Number - datetime.timedelta(days=1)
        oneDayEarlier_str = datetime.date(oneDayEarlier.year, oneDayEarlier.month, oneDayEarlier.day).isoformat()

        oneDayLater = specificDate_Number + datetime.timedelta(days=1)
        oneDayLater_str = datetime.date(oneDayLater.year, oneDayLater.month, oneDayLater.day).isoformat()

        res = requests.get(f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&observation_start={oneDayEarlier_str}&observation_end={specificDate}&sort=asc&api_key={API_KEY}&file_type=json")

        period_RFR_dataContainer = json.loads(res.text)
        
        period_RFR_data = period_RFR_dataContainer["observations"]
        print(f"period_RFR_data: {period_RFR_data}")

        try:
            RFR_value = float(period_RFR_data[1]["value"])
            ERP_value = float(EXPECTED_MARKET_RETURN- RFR_value)
        except:
            pass
        
        return {
            "type": "dateSpecific",
            "RFR": RFR_value,
            "ERP": ERP_value
        }
        
if (API_KEY is not None):
    userChoice = 0
    print("Options:")
    print("0 - latest data")
    print("1 - specific timeframes - enter startTime and endTime")
    print("2 - the data for a year - median & average - enter year")
    print("3 - the data for a specific date")

    try:
        userChoice = int(input("Enter choice: "))
        if (userChoice == 0):
            print(getRiskFreeRate_ERP(True))
        elif(userChoice == 1):
            startTime = input("Enter specific start date YYYY-MM-DD: ")
            endTime = input("Enter specific end date YYYY-MM-DD: ")

            print(getRiskFreeRate_ERP(False, False, startTime, endTime))
        elif(userChoice == 2):
            userYear = int(input("Enter year: "))

            currentYearDate = datetime.datetime.now()
            currentYear = currentYearDate.year

            # if a user enters a year that is right now, the progarm will fetch the median & average leading up to today
            if (userYear < 1900 or userYear > currentYear):
                print("Please choose a year between 1900 and ", currentYear)
            elif(userYear == currentYear):
                print("Using a fallback - data leading up to today, for this year")

                january1 = datetime.datetime(currentYear, 1, 1).strftime("%Y-%m-%d")

                latestDate = datetime.date.today().strftime("%Y-%m-%d")

                print(getRiskFreeRate_ERP(False, False, january1, latestDate))
            else:
                january1 = datetime.datetime(userYear, 1, 1).strftime("%Y-%m-%d")

                december31 = datetime.datetime(userYear, 12, 31).strftime("%Y-%m-%d")

                print(getRiskFreeRate_ERP(False, False, january1, december31))
        elif (userChoice == 3):
            date_choice = input("Enter specific date YYYY-MM-DD: ")
            print(getRiskFreeRate_ERP(False, date_choice))
            
    except ValueError:
        print("Don't provide anything else other than a numebr between 0-2")
else:
    print("Please set your API_KEY as an environment variable to use this program")