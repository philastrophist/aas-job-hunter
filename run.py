import scraper
import plot
import pandas as pd
import os
from notifiers import get_notifier
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--overwrite', action='store_true')
args = parser.parse_args()

position_name = 'Post-doctoral Positions & Fellowships'

table, new = scraper.scrape(position_name)

from notifiers import get_notifier
email = get_notifier('mailgun')
email.notify(**{'to': os.environ['EMAIL_ADDRESS'],
             'domain': os.environ['MAILGUN_DOMAIN'],
             'api_key': os.environ['MAILGUN_API_KEY'],
             'from': 'postmaster@'+os.environ['MAILGUN_DOMAIN'],
             'subject': '{} New Jobs available!'.format(new),
             'message': 'There {} new positions available!'.format(new)})