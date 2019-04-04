import scraper
import plot
import pandas as pd
import os

position_name = 'Post-doctoral Positions & Fellowships'
# position_name = 'Faculty Positions (visiting & non-tenure)'
fname = '{}-{}.cache'.format(position_name, pd.to_datetime('today').date())
if os.path.exists(fname):
    table = pd.read_csv(fname)
else:
    table = scraper.scrape(position_name)
    table.to_csv(fname)

ax = plot.plot_times(table, engine='html')
plot.mpld3.fig_to_html(ax.figure)
plot.mpld3.show(ax.figure, open_browser=False)