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
if new is None:
    exit(0)

assert len(new) > 0, "something has gone badly wrong..."

from notifiers import get_notifier
email = get_notifier('mailgun')

headers = new['Title'] + ' at ' + new['Institution/Organization'] + ' in ' + new['Location']
line = '='*20
bullets = headers + '\n' + line + '\n' + new['Job Announcement Text']
email.notify(**{'to': os.environ['EMAIL_ADDRESS'],
                'domain': os.environ['MAILGUN_DOMAIN'],
                'api_key': os.environ['MAILGUN_API_KEY'],
                'from': 'postmaster@'+os.environ['MAILGUN_DOMAIN'],
                'subject': '{} New Jobs available!'.format(len(new)),
                'message': '\n\n\n\n'.join(map(str, bullets))})

