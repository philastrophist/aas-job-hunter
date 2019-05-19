from functools import reduce, partial
from operator import or_
import datefinder
import re
from urllib.request import urlopen

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm


BASE_URL = "https://jobregister.aas.org/"
TABLE_HEADER = {'name': 'h1'}
EQUIVALENT_FIELDS = [['Zip/Postal', 'Zip/Postal Code']]


def parse_date(string):
    if isinstance(string, str):
        try:
            finish = re.search(r'\d[a-zA-Z]', string).start() + 1
        except AttributeError:
            finish = None
        return next(datefinder.find_dates(string[:finish]))
    return np.nan


def parse_dates(dataframe, filt=('deadline', 'date')):
    df = dataframe.copy()
    for c in df.columns:
        if any(f in c.lower() for f in filt):
            try:
                df[c] = df[c].apply(parse_date)
            except (StopIteration, AttributeError, TypeError):
                raise ValueError("date not found in the text in the '{}' column, where it was expected.".format(c))
    return df

def scrape(position_name):
    html = urlopen(BASE_URL).read().decode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    names = [i.text for i in soup.find_all(**TABLE_HEADER) if 'class' not in i.attrs]
    html_tables = [i for i in soup.find_all('table')]
    tables = pd.read_html(html)

    assert len(html_tables) == len(tables), "Parsing mismatch!, length of main table is not the same as the number detail tables. The job register has likely changed!"

    for table, df in zip(html_tables, tables):
        df['href'] = [np.where(tag.has_attr('href'),tag.get('href'),"no link") for tag in table.find_all('a')]

    tables = {n: v for n, v in zip(names, tables)}

    table = tables[position_name]
    infos = []
    urls = []
    for link in tqdm(table['href'].astype(str), desc='Scraping details'):
        soup = BeautifulSoup(urlopen(BASE_URL+link).read().decode('utf-8'), "lxml")
        sections = soup.find_all(attrs={'class': 'field'})
        info = [u'{}'.format(i.text).replace('\xa0', '') for i in sections]
        url = [[str(np.where(tag.has_attr('href'), tag.get('href'), "no link")) for tag in section.find_all('a')] for
               section in sections]
        url = reduce(or_, map(set, url))
        infos.append(info)
        urls.append(url)

    infos = [dict(entry.split(':', 1) for entry in info) for info in infos]
    df = pd.DataFrame(infos)
    for a, b in EQUIVALENT_FIELDS:
        try:
            df[a] = df[a].combine_first(df[b])
        except KeyError:
            pass
    df = parse_dates(df)
    df['urls'] = ['; '.join(u) if len(u) else np.nan for u in urls]
    df = df.rename(columns={'Title': 'Person Title'})
    return pd.concat([table, df], axis=1)


