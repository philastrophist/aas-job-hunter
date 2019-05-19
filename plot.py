import mpld3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker


def plot_times(df, ax=None, column='Application Deadline', engine='matplotlib'):
    ax = None
    date = pd.to_datetime(df[column])
    time_to_application = (date - pd.to_datetime('today')).dt.days
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    nbins = (date.max() - date.min()).days
    count, bins, patches = ax.hist(time_to_application, bins=nbins, alpha=0.5, edgecolor='k')

    ax.xaxis.set_major_locator(ticker.AutoLocator())

    navailable = (time_to_application > 0).sum()
    ax.set_title('Number of jobs with outstanding deadlines: {}/{}'.format(navailable , len(df)))
    ax.set_xlabel('Days from today')

    ax.set_xlim(max([-30, time_to_application.min()]), time_to_application.max())
    ylim = ax.get_ylim()
    ax.axvline(0, color='k', linewidth=2)
    ax.axvspan(-365, 0, color='r', alpha=0.2)
    plt.tight_layout()
    ax.set_ylim(ylim)

    texts = []
    for bin in bins:
        strings = df.loc[(time_to_application >= bin) & (time_to_application < bin + 1), 'Title']
        text = '\n'.join(['*' + v for v in strings.values])
        texts.append(text)

    if engine == 'matplotlib':
        annots = []
        for text in texts:
            annot = ax.annotate(text, xy=(0, 0), xytext=(-20, 20), textcoords="offset points",
                                bbox=dict(boxstyle="round", fc="black", ec="b", lw=2),
                                arrowprops=dict(arrowstyle="->"))
            annot.set_visible(False)
            annots.append(annot)

        def update_annot(bar, annot):
            x = bar.get_x() + bar.get_width() / 2.
            y = bar.get_y() + bar.get_height()
            annot.xy = (x, y)
            # text = "({:.2g},{:.2g})".format(x, y)
            # annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.4)

        def hover(event):
            for annot, bar in zip(annots, patches):
                vis = annot.get_visible()
                if event.inaxes == ax:
                    cont, ind = bar.contains(event)
                    if cont:
                        update_annot(bar, annot)
                        annot.set_visible(True)
                if vis:
                    annot.set_visible(False)
            fig.canvas.draw()

        fig.canvas.mpl_connect("motion_notify_event", hover)

    elif engine == 'html':
        # tooltip = mpld3.plugins.Too PointLabelTooltip(patches, labels=texts)
        # mpld3.plugins.connect(fig, tooltip)
        for i, bar in enumerate(patches):
            tooltip = mpld3.plugins.LineLabelTooltip(bar, label=texts[i])
            mpld3.plugins.connect(fig, tooltip)
    else:
        raise RuntimeError("{} unknown".format(engine))

    return ax