from functools import reduce
from operator import or_

from bs4 import BeautifulSoup
from urllib.request import urlopen
import feedparser
import pandas as pd
import re
import numpy as np
from tqdm import tqdm


BASE_URL = "https://jobregister.aas.org/"
TABLE_HEADER = {'name': 'h1'}
EQUIVALENT_FIELDS = [['Zip/Postal', 'Zip/Postal Code']]


def strip_remaining_days(x):
    try:
        return x[:x.index('To event remaining')]
    except (ValueError, AttributeError):
        return x


def parse_dates(df, filt=('deadline', 'date')):
    for c in df.columns:
        if any(f in c.lower() for f in filt):
            df[c] = df[c].apply(strip_remaining_days)
            df[c] = pd.to_datetime(df[c])
    return df

def scrape(position_name):
    html = urlopen(BASE_URL).read().decode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    names = [i.text for i in soup.find_all(**TABLE_HEADER) if 'class' not in i.attrs]
    html_tables = [i for i in soup.find_all('table')]
    tables = pd.read_html(html)

    assert len(html_tables) == len(tables), "Parsing mismatch!"

    for table, df in zip(html_tables, tables):
        df['href'] = [np.where(tag.has_attr('href'),tag.get('href'),"no link") for tag in table.find_all('a')]

    tables = {n: v for n, v in zip(names, tables)}

    table = tables[position_name]
    infos = []
    urls = []
    for link in tqdm(table['href'].astype(str)):
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
        df[a] = df[a].combine_first(df[b])
    df = parse_dates(df)
    df['urls'] = ['; '.join(u) if len(u) else np.nan for u in urls]
    df = df.rename(columns={'Title': 'Person Title'})
    return pd.concat([table, df], axis=1)


