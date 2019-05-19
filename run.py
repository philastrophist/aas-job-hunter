import scraper
import plot
import pandas as pd
import os
import matplotlib.pyplot as plt

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--overwrite', action='store_true')
args = parser.parse_args()

position_name = 'Post-doctoral Positions & Fellowships'
# position_name = 'Faculty Positions (visiting & non-tenure)'
fname = '{}-{}.cache'.format(position_name, pd.to_datetime('today').date())
if os.path.exists(fname) and (not args.overwrite):
    table = pd.read_csv(fname)
else:
    table = scraper.scrape(position_name)
    table.to_csv(fname)

ax = plot.plot_times(table)
plt.show()
# plot.mpld3.fig_to_html(ax.figure)
# plot.mpld3.show(ax.figure, open_browser=False)