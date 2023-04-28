import requests
import bs4 as bs
import yahoo_fin.stock_info as si
from typing import List
from logger import log
from dataclasses import dataclass


@dataclass
class Stock:
    ticker: str
    pe_ratio: float or None


@log
def get_stock_tickers() -> List[str]:
    response = requests.get(
        'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker.replace('\n', ''))

    return tickers


@log
def get_pe_rations(tickers: List) -> List[Stock]:
    pe_ratios = [
        Stock(ticker=ticker, pe_ratio=si.get_quote_data(
            ticker=ticker).get('trailingPE'))
        for ticker in tickers
    ]

    return pe_ratios


def sorting_pe_ratios(stock):
    return stock.pe_ratio if stock.pe_ratio is not None else 999


tickers = get_stock_tickers()
pe_ratios = get_pe_rations(tickers=tickers)

pe_ratios.sort(key=sorting_pe_ratios)
print()
