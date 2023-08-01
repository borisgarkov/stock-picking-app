import requests
import bs4 as bs
from logger import log
from dataclasses import dataclass

import threading
import re
from logger import logger
import csv


@dataclass
class Stock:
    ticker: str
    pe_ratio: str
    tradingview_url: str


@log
def get_stock_tickers() -> list[str]:
    response = requests.get(
        'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    )
    soup = bs.BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker.replace('\n', ''))

    return tickers


def get_pe_ratios(ticker: str) -> None:

    url = f'https://www.gurufocus.com/term/pettm/{ticker}/PE-Ratio/'
    response = requests.get(url)

    if response.status_code == 429:  # HTTP 429 Too Many Requests
        tickers_not_processed.append(ticker)
        return

    soup = bs.BeautifulSoup(response.text, 'lxml')

    pe_text = soup.find('h1').nextSibling.text

    extracted_pe = re.findall('[0-9]+[.][0-9]+', pe_text)
    pe = extracted_pe[0] if extracted_pe else 9999

    stock = Stock(
        ticker=ticker,
        pe_ratio=float(pe),
        tradingview_url='https://www.tradingview.com/chart/kHM2rgsK/?symbol=' + ticker
    )

    stocks_container.append(stock)


@log
def start_threads(tickers: list[str]) -> None:

    global tickers_not_processed
    tickers_not_processed = []

    threads = []

    for ticker in tickers:
        thread = threading.Thread(target=get_pe_ratios, args=(ticker,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    logger.critical(tickers_not_processed)


@log
def sort_pe_ratios(stocks_container: list[str]) -> list[str]:
    return sorted(stocks_container, key=lambda x: x.pe_ratio)


@log
def save_results() -> None:
    with open('stocks_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        fields = ['ticker', 'pe_ratio', 'tradingview_url']

        writer.writerow(fields)

        for stock in stocks_container:
            writer.writerow(
                [stock.ticker, stock.pe_ratio, stock.tradingview_url]
            )


stocks_container = []
tickers_not_processed = []

tickers = get_stock_tickers()
start_threads(tickers=tickers)

while tickers_not_processed:
    start_threads(tickers=tickers_not_processed)

stocks_container = sort_pe_ratios(stocks_container)
save_results()
