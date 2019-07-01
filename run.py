import scraper
import plot
import pandas as pd
import os
from notifiers import get_notifier
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)


position_name = 'Post-doctoral Positions & Fellowships'

table, new = scraper.scrape(position_name)
assert new >= 0, "somethings wrong here"
from notifiers import get_notifier
email = get_notifier('mailgun')

if new > 0:
    email.notify(**{'to': os.environ['EMAIL_ADDRESS'],
                 'domain': os.environ['MAILGUN_DOMAIN'],
                 'api_key': os.environ['MAILGUN_API_KEY'],
                 'from': 'postmaster@'+os.environ['MAILGUN_DOMAIN'],
                 'subject': '{} New Jobs available!'.format(new),
                 'message': 'There {} new positions available!'.format(new)})
