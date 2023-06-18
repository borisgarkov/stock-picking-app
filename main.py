import requests
import bs4 as bs
from typing import List
from logger import log
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ['API_KEY']


@dataclass
class Stock:
    ticker: str
    pe_ratio: float or None


@log
def get_stock_tickers() -> List[str]:
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


@log
def get_pe_rations(tickers: List) -> List[Stock]:

    pe_ratios = []

    for ticker in tickers:
        url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey=${API_KEY}'
        r = requests.get(url)
        data = r.json()

        pe_ratios.append(
            Stock(
                ticker=ticker,
                pe_ratio=data['PERatio']
            )
        )

    return pe_ratios


def sorting_pe_ratios(stock):
    return stock.pe_ratio if stock.pe_ratio is not None else 999


tickers = get_stock_tickers()
pe_ratios = get_pe_rations(tickers=tickers)

pe_ratios.sort(key=sorting_pe_ratios)
print()
