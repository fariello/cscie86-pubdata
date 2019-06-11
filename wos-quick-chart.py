#!/usr/bin/python3
from matplotlib import pyplot as plt
import csv
import matplotlib
import matplotlib.dates as mdates
import numpy as np
import argparse
import os
import sys

class WoSPlot:
    def __init__(self,filename,args):
        self.input_filename = filename
        self.args = args
        if self.args.verbosity > 0:
            print("Loading data from '%s'" % filename)
            pass
        years = []
        count = []
        with  open(self.input_filename,'r') as csv_fh:
            rdr = csv.reader(csv_fh, dialect=csv.Sniffer().sniff(csv_fh.read(1000)))
            csv_fh.seek(0)
            self.headers = None
            self.data = []
            for row in rdr:
                if self.headers is None:
                    self.headers = row
                    continue
                try:
                    years.append(int(row[0]))
                    count.append(int(row[1]))
                except ValueError as e:
                    continue
                pass
            pass
        years = np.array(years)
        if self.args.start_year is None:
            start = years.min()
        else:
            start = self.args.start_year
            pass
        if self.args.end_year is None:
            end = years.max()
        else:
            end = self.args.end_year
            pass
        all_years = [year for year in range(start,end+1)]
        input_data = {k:v for k,v in zip(years,count)}
        years_data = {}
        all_count = []
        self.data_dict = {}
        for year in all_years:
            if year in input_data:
                all_count.append(input_data[year])
                self.data_dict[year] = input_data[year]
            else:
                all_count.append(0)
                self.data_dict[year] = 0
                pass
            pass
        self.years = np.array(all_years)
        self.count = np.array(all_count)
        if self.args.verbosity > 1:
            print("Loaded years: %s" %self.years)
            print("Loaded count: %s" %self.count)
            pass
        pass

    def save_csv(self):
        pass

    def plot(self):
        self.fig, self.ax1 = plt.subplots(1,1)
        plt.tight_layout()
        self.fig.set_size_inches(self.args.plot_width, self.args.plot_height)
        self.ax1.grid(color='white',linestyle='solid')
        self.ax1.set_facecolor(color='#F4F4F4')
        self.ax1.set_xlim(self.years.min(),self.years.max())
        self.ax1.set_ylim(0,self.count.max())
        if self.args.title is not None:
            self.title = "Number of Publications for \"%s\" %d-%d\n(Web of Science Search)" %(self.args.title,self.years.min(),self.years.max())
            self.save_basename = "%s Publications %d-%d According to Web of Science" %(self.args.title,self.years.min(),self.years.max())
        else:
            self.title = "Number of Publications %d-%d\n(Web of Science Search)" %(self.years.min(),self.years.max())
            self.save_basename = "Publications %d-%d According to Web of Science" %(self.years.min(),self.years.max())
            pass
        self.fig.suptitle(self.title, backgroundcolor='w', bbox=dict(boxstyle='round', fc="w", ec="k"))
        self.ax1.plot(self.years, self.count, linestyle=self.args.linestyle, alpha=self.args.alpha, marker=self.args.marker,label="%s Publications" %(self.args.title))
        if self.args.fill:
            self.ax1.fill_between(self.years, self.count, 0, alpha=0.33)
            pass
        legend = False
        for fit_range in self.args.fit_ranges:
            errs = False
            [start,end] = fit_range
            if start < self.years.min():
                print ("ERROR: %s is before the first year in the data set (%s)" %(start, self.years.min()))
                errs = True
                pass
            if start > self.years.max():
                print ("ERROR: %s is after the last year in the data set (%s)" %(start, self.years.min()))
                errs = True
                pass
            if end < self.years.min():
                print ("ERROR: %s is before the first year in the data set (%s)" %(end, self.years.min()))
                errs = True
                pass
            if end > self.years.max():
                print ("ERROR: %s is after the last year in the data set (%s)" %(end, self.years.min()))
                errs = True
                pass
            if errs:
                continue
            if self.args.verbosity > 1:
                print("Drawing a regression line from %d to %s" %(start,end))
                pass
            x = np.array([ i for i in range(start,end+1)])
            y = np.array([self.data_dict[year] for year in x])
            m,b = np.polyfit(x, y, 1)
            xi = np.array([x.min(),x.max()])
            yi = np.array([m*x.min()+b,m*x.max()+b])
            if self.args.verbosity > 2:
                print(" - Line x=%s, y=%s" %(xi,yi))
                pass
            self.ax1.plot(xi,yi, alpha=0.50, label="Regression Line %s-%s" %(start,end))
            legend = True
            pass
        if legend:
            legend = self.ax1.legend(loc=2)
            legend.get_frame().set_alpha(0.33)
            pass
        self.ax1.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        self.ax1.get_xaxis().set_tick_params(rotation=60)
        return self

    def save(self,filename=None):
        if filename is not None:
            self.save_filename = filename
            full_path = filename
        elif self.args.save_filename is not None:
            self.save_filename = self.args.save_filename
            full_path = self.save_filename
            pass
        else:
            full_path = os.path.join("output", "%s.svg" % self.save_basename)
            pass
        if self.args.verbosity > 0:
            print("Saving %s" % full_path)
            pass
        self.fig.savefig(full_path, dpi=300)
        plt.close(self.fig)
        return self

def get_filename(search_dirs,filename):
    for current in search_dirs:
        full_path = os.path.join(current,filename)
        if os.path.isfile(full_path):
            return full_path
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description='Take a tab-delimited Web of Science download data file and make a pretty graph.')
    parser.add_argument('files', type=str, nargs='+')
    parser.add_argument('--alpha', '-c', default=0.50, type=float, dest='alpha', help="Set the alpha for the plot line(s)")
    parser.add_argument('--debug', '-D', default=False, action='store_true', dest='debug', help="Turn debugging on.")
    parser.add_argument('--end-year', default=None, type=int, dest='end_year', help="End with this year, not the first year in the data set.")
    parser.add_argument('--fill', '-F', default=False, action='store_true', dest='fill', help="Fill under the line.")
    parser.add_argument('--height', '-H', default=7.5, type=float, dest='plot_height',help="Height in inches of the plot. ")
    parser.add_argument('--linestyle', '-L', default='-', type=str, dest='linestyle', help="Set the linestyle format for plot. Default is '-'. Use the matplotlib syntax. Some examples: '' for none,'-',':','--','-.'.")
    parser.add_argument('--marker', '-m', default='.', type=str, dest='marker', help="Set the marker for values. Default is '' which means no mark. Use the matplotlib syntax. Some examples: '.','o','*'.")
    parser.add_argument('--quiet', '-q', default=0, dest='quiet', action='count',help="Decrease verbosity. Can have multiple.")
    parser.add_argument('--save', '-s', default=None, type=str, dest='save_filename', help="Save to image file. Recommend file names ending in .svg for high quality or .png for other needs.")
    parser.add_argument('--start-year', default=None, type=int, dest='start_year', help="Start with this year, not the first year in the data set.")
    parser.add_argument('--title', default=None, type=str, dest='title', help="Title for the figure.")
    parser.add_argument('--fit', default=[], type=str, action='append', dest='fit_ranges', help="Provide a range of dates to plot a simple (regression) fit line. Example: --fit 2010,2015")
    parser.add_argument('--verbose', '-v', default=0, dest='verbosity', action='count',help="Increase verbosity. Can have multiple.")
    parser.add_argument('--width', '-W', default=11.0, type=float, dest='plot_width',help="Width in inches of the plot. ")

    args = parser.parse_args()
    args.verbosity = 1 + args.verbosity - args.quiet


    fitters = []
    for range_str in args.fit_ranges:
        new_range = [int(x) for x in range_str.split(',')]
        fitters.append(new_range)
        pass
    # print(fitters)
    args.fit_ranges = fitters

    for inputfile in args.files:
        wf = WoSPlot(inputfile,args)
        wf.plot().save()
        pass
    pass

if __name__ == "__main__":
    main()
    sys.exit(0)
