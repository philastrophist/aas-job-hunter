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
email = get_notifier('email')
email.notify(to=os.environ['EMAIL_ADDRESS'], message='There {} new positions available!'.format(new))