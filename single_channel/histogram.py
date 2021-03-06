import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.scale as mscale
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import matplotlib.ticker as ticker
import argparse as ap


class Histogram:

    def __init__(self, fname, size, fontsize, ticks, xrange, yrange, legend, dat):
        """
        plot handling of HCJFIT event time distribution
        :param fname: HCJFIT ASCII file name
        """

        self.fname = fname
        self.size, self.fontsize, self.ticks, self.xrange, self.yrange, self.legend, self.dat = size, fontsize, ticks, xrange, yrange, legend, dat
        self.data, self.calc, self.mntime, self.mxtime, self.meven, self.dead = self.read()
        if self.dat: self.data = pd.concat([pd.DataFrame([0], index=[self.dead], columns=[1]), self.data, self.last_bin()])

    def read(self):
        """
        read HCJFIT ASCII file
        :return: histogram datafram, fits dataframes, time and event number range, dead time
        """

        with open(self.fname) as f:

            raw = f.readlines()
            dataid, calcid, seriid = [], [], []

            for (id, line) in enumerate(raw):
                if 'raw' in line: dataid.append(id)
                if 'calc' in line: calcid.append(id)
                if len(line.split()) == 1: seriid.append(id)

            # histogram
            if self.dat:
                data = [[float(value) for value in line.split()] for line in raw[seriid[0]+1:seriid[0]+int(raw[seriid[0]])+1]]
                dead = data[0][0]
                data = pd.DataFrame(data).set_index(keys=0)
            else:
                data = False
                dead = False

            # fits
            calc = []

            calclen = len(seriid) - 1 if self.dat else len(seriid)
            shift = 1 if self.dat else 0

            for i in range(calclen):
                calc.append([[float(value) for value in line.split()] for
                             line in raw[seriid[i+shift]+1:seriid[i+shift]+int(raw[seriid[i+shift]])+1]])

            calc = [pd.DataFrame(series).set_index(keys=0) for series in calc]

            # ranges
            meven = max([series.max().iloc[0] for series in calc])
            mxtime = max([series.index[-1] for series in calc])
            mntime = sorted([series.index[0] for series in calc])[1]                                                    # magic sorted, because missed event may be longer (60% of the time, it works every time)

            return data, calc, mntime, mxtime, meven, dead

    def last_bin(self):
        """
        extrapolates last bin width
        :return: last bin width [ms]
        """

        bins = self.data.index.values
        diffs = np.log(np.diff(bins))                                                                                   # linearized bin widths
        xs = range(0, len(diffs))                                                                                       # just x axis

        fit = np.polyfit(xs, diffs, 1)
        fiteq = np.poly1d(fit)
        last_bin = np.exp(fiteq(xs[-1]+1)) + self.data.index.values[-1]

        extrapolated = pd.DataFrame(data=[0], index=[last_bin], columns=[1])

        print('Sanity check: last known bin: {}'.format(self.data.index.values[-1]))
        print('Sanity check: extrapolated bin: {}'.format(last_bin))

        return extrapolated

    def plot(self):

        # general plot settings
        mscale.register_scale(SquareRootScale)
        sns.set_style("white")
        sns.set_style("ticks")

        # figure generation
        fig, ax = plt.subplots(figsize=self.size)
        ax.set_xscale('log', basex=10)
        ax.set_yscale('squareroot')

        ### figure variables ###

        # data
        if self.dat: self.data.plot(ax=ax, drawstyle='steps-post', color='black', lw=3)
        self.calc[0].plot(ax=ax, color='black', lw=3)
        self.calc[-1].plot(ax=ax, color='grey', lw=3, style='--')
        for series in sch_hist.calc[1:-1]:
            series.plot(ax=ax, color='black', lw=1)

        # x-axis
        xmax = int(np.log10(self.mxtime))                                                                               # magic again, 'last before' base 10 log
        xmin = int(np.log10(self.mntime))                                                                               # magic again, first base 10 log

        if self.xrange:
            ax.set_xlim(self.xrange)
        else:
            ax.set_xlim([10 ** xmin, 10 ** (xmax + 1)])

        # y-axis
        ymax = int(self.meven ** 0.5)                                                                                   # magic need 'last before' power function argument
        if ymax % 2 == 1: ymax += 1

        if self.yrange:
            ax.set_ylim(self.yrange)
        else:
            ax.set_ylim([0, (ymax + 2) ** 2])

        ys = [(x * 2) ** 2 for x in range(0, int(ymax / 2 + 2))]                                                        # magick scale if +2 so w need /2 and +2 for additional entry
        yms = [x ** 2 for x in np.arange(0, ymax + 2, 0.5)]                                                             # magick scale is not divided so only +2 for additional entry

        if self.yrange:
            ys = [y for y in ys if y < self.yrange[1]]
            yms = [ym for ym in yms if ym < self.yrange[1]]

        last = ys[-1] if len(ys) % 2 == 1 else 0                                                                        # too many ys? reduce, but preserve last
        lastm = yms[-1] if len(yms) % 2 == 1 else 0

        if len(ys) > 10:
            ys = ys[0:-1:4]
            yms = yms[0:-1:4]

        if len(ys) > 5:
            ys = ys[0:-1:2]
            yms = yms[0:-1:2]

        if last !=0: ys.append(last)
        if lastm !=0: yms.append(lastm)

        ax.set_yticks(ys)
        ax.set_yticks(yms, minor=True)
        if self.ticks:
            plt.locator_params(axis='x', numticks=self.ticks)
        ax.tick_params(labelsize=self.fontsize[0])

        # overwrite labels and legend
        ax.set_xlabel('apparent open time [ms] (log scale)', fontsize=self.fontsize[1])
        ax.set_ylabel('frequency density (square root scale)', fontsize=self.fontsize[1])

        if self.legend:
            ax.legend(['observed', 'fit', 'missed event correction', 'components fits'], loc='best', fontsize=self.fontsize[1])
        else: ax.legend_.remove()

        sns.despine()
        plt.tight_layout()

        plt.show()
        fig.savefig(self.fname.split('.')[0] + ".png")


class SquareRootScale(mscale.ScaleBase):
    """
    ScaleBase class for generating square root scale.
    """

    name = 'squareroot'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self, axis)                                                                           # axis was added here in 2020 for compatibility

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(ticker.AutoLocator())
        axis.set_major_formatter(ticker.ScalarFormatter())
        axis.set_minor_locator(ticker.NullLocator())
        axis.set_minor_formatter(ticker.NullFormatter())

    def limit_range_for_scale(self, vmin, vmax, minpos):
        return  max(0., vmin), vmax

    class SquareRootTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def transform_non_affine(self, a):
            return np.array(a)**0.5

        def inverted(self):
            return SquareRootScale.InvertedSquareRootTransform()

    class InvertedSquareRootTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def transform(self, a):
            return np.array(a)**2

        def inverted(self):
            return SquareRootScale.SquareRootTransform()

    def get_transform(self):
        return self.SquareRootTransform()


parser = ap.ArgumentParser()
parser.add_argument("-f", "--files", nargs='+', help="hcjfit ASCII files")
parser.add_argument("-s", "--size", nargs='+', type=float, help="figure x and y size [inch]")
parser.add_argument("-fs", "--font_size", nargs='+', type=float, help="tick fontisze")
parser.add_argument("-x", "--xrange", nargs='+', type=float, help="plot x range")
parser.add_argument("-y", "--yrange", nargs='+', type=float, help="plot y range")
parser.add_argument("-t", "--ticks", type=float, help="x axis ticks")
parser.add_argument("-l", "--legend", dest='leg', action='store_true', help="add legend")
parser.add_argument("-nl", "--no_legend", dest='leg', action='store_false', help="don't add legend")
parser.add_argument("-d", "--data", dest='dat', action='store_true', help="add histogram")
parser.add_argument("-nd", "--no_data", dest='dat', action='store_false', help="don't add histogram")

parser.set_defaults(leg=True)
parser.set_defaults(dat=True)

args = parser.parse_args()

for file in args.files:
    sch_hist = Histogram(file, args.size, args.font_size, args.ticks, args.xrange, args.yrange, args.leg, args.dat)
    sch_hist.plot()