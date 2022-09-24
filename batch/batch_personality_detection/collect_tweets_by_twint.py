#!/usr/bin/env python

import twint
import pytz
from datetime import datetime, timedelta
from time import time
import nest_asyncio
nest_asyncio.apply()

def find_dates(time_zone:str="", delta_days:int=-90):
    """Return the current and target dates

    Parameters
    ----------
    time_zone: str
        The timezone for the requested dates. (defaults to None)
    delta_days: int
        Number of days as the difference of the target date and the current date

    Returns
    -------
    current_date: str
        Current date in string format
    target_date: str
        Target date in string format
    """
    if time_zone != "":
        tz = pytz.timezone(time_zone)
    else:
        tz = None

    dt = datetime.now(tz=tz)
    current_date = datetime.date(dt)    # current date

    delta = timedelta(days=delta_days)
    target_date = current_date + delta

    return str(current_date), str(target_date)

def scrape_user(username:str, since:str="", until:str="", **params) -> None:
    file_path = "data/search_all/" + username + "_" + since + "_" + until + "_" + ".csv"

    c = twint.Config()      # initialize empty config
    c.Search = username       # set what to search for in tweets
    c.Limit = 500
    c.Store_csv = True      # store output as csv
    c.Output = file_path    # relative path to output file
    c.Since = since         # time limit for search (tweets since when?)
    c.Until = until         # set the upper limit for time of tweet
    c.Count = True          # in the end, count the tweets fetched
    twint.run.Search(c)

def main():
    """main body"""
    # if len(argv) != 2:
    #     raise ValueError("Please only enter the username of the target")

    # username = str(argv[1])
    start = time()

    # brands = ["Amazon", "Alibaba", "The Home Depot", "Walmart", "JD", "Costco",
    #         "Pinduoduo", "IKEA", "Lowe's", "ALDI", "Target", "Ebay",
    #         "Dollar General", "Whole Foods", "Lidl", "Tesco", "Woolworths",
    #         "CVS", "Sam's club", "TJ MAXX", "افق کوروش", "فروشگاه شهروند",
#             "هایپر استار", "رفاه", "دیجیکالا", "اسنپ مارکت", "جانبو"]
    brands = ["Amazon"]
    for username in brands:
        for i in range(1, 10):
            _, since = find_dates(delta_days= -i * 10)
            _, until = find_dates(delta_days= (-i + 1) * 10)
            scrape_user(username, since=since, until=until)
            print(i)
            # print(since, until)

    print(f"Runtime = ")

if __name__ == "__main__":
    main()
