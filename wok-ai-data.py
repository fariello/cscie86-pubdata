#!/usr/bin/python3

# coding: utf-8

# In[3]:


#!/usr/bin/python3
from matplotlib import pyplot as plt
import datetime
import csv
import dateutil.parser
import math
import matplotlib
import matplotlib.dates as mdates
import numpy as np
import argparse
import os
import sys


# In[110]:


class PubData:
    def __init__(self,csv_filename):
        self.csv_filename = csv_filename
        with  open(self.csv_filename,'r') as csv_fh:
            rdr = csv.reader(csv_fh)
            self.headers = None
            self.data = []
            for row in rdr:
                if self.headers is None:
                    self.headers = row
                    continue
                row = [int(i) for i in row]
                self.data.append(row)
                pass
            pass
        self.data = np.array(self.data)
        self.header_idx = dict(zip(self.headers,range(len(self.headers))))
        self.years = self.get_col('Year')
        self.year_min = self.years[0]
        self.year_max = self.years[-1]
        self.width = 11.0
        self.height = 7.5
        pass

    def new_fig(self):
        self.fig, self.ax1 = plt.subplots(1,1)
        plt.tight_layout()
        return self

    def get_col(self,what):
        return self.data[:,self.header_idx[what]]

    def _get_slice(self,min_year=None,max_year=None):
        if min_year is None:
            min_year = self.year_min
            pass
        if max_year is None:
            max_year = self.year_max
            pass
        start = min_year - self.year_min
        end = start + 1 + (max_year - min_year)
        self.min_year = self.years[start]
        self.max_year = self.years[end -1]
        return start,end,self.years[start:end]

    def _start(self):
        self.new_fig()
        self.fig.set_size_inches(self.width, self.height)
        self.ax1.grid(color='white',linestyle='solid')
        self.ax1.set_facecolor(color='#F4F4F4')
        return self

    def _add_one(self,what,years,data, alpha=0.75, fill_alpha=0.25):
        # print("_add_one(): years=%s, data=%s"% (years,data))
        self.ax1.plot(years, data, linestyle='-', alpha=alpha, marker='.',label=what)
        if fill_alpha is not None and fill_alpha >= 0.0:
            self.ax1.fill_between(years, data, 0, alpha=fill_alpha)
            pass
        return self

    def _era_line(self,name,start_year,end_year):
        after_start = self.min_year < start_year and self.max_year > start_year
        before_end = self.min_year < end_year and self.max_year > end_year
        if before_end:
            self.ax1.axvline(x=end_year,color='k',linestyle='--',alpha=0.5)
        if before_end or after_start:
            if start_year < self.min_year:
                start_year = self.min_year
                pass
            if end_year > self.max_year:
                end_year = self.max_year
                pass
            x = (end_year+start_year)/2.0
            y = self.y_max * 0.1
            self.ax1.annotate(name, xy=(x,y), xycoords='data', textcoords='data', ha='center', va='center', rotation=45.0)
            pass
        pass
    def _eras(self):
        self._era_line('Golden Years',0,1974)
        self._era_line('First AI Winter',1974,1980)
        self._era_line('Boom',1980,1987)
        self._era_line('Bust',1987,1993)
        pass

    def plot_one(self,what,min_year=None,max_year=None):
        self._start()
        this_data = self.get_col(what)
        start,end,years = self._get_slice(min_year,max_year)
        #self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        self.ax1.set_xlim(years.min(),years.max())
        this_data = this_data[start:end]
        # print("plot_one(): start_idx = %s, end_idx=%s, years=%s, data=%s"% (start,end,years,this_data))
        self.y_min = this_data.min()
        self.y_max = this_data.max()
        self.ax1.set_ylim(this_data.min(),this_data.max())
        self._eras()
        self.title = "Number of Publications for \"%s\" %d-%d\nAccording to Web of Knowledge" %(what,years.min(),years.max())
        self.filename = "%s Publications %d-%d According to Web of Knowledge" %(what,years.min(),years.max())
        self.fig.suptitle(self.title, backgroundcolor='w', bbox=dict(boxstyle='round', fc="w", ec="k"))
        self._add_one(what,years,this_data)
        #legend = self.ax1.legend(loc=2)
        #legend.get_frame().set_alpha(0.33)
        self.ax1.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        self.ax1.get_xaxis().set_tick_params(rotation=60)
        print("Saving %s" %self.filename)
        self.fig.savefig("%s.svg" % self.filename, dpi=300)
        plt.close(self.fig)
        return self

    def plot_all(self,min_year=None,max_year=None,fill_alpha=0.25):
        self._start()
        start,end,years = self._get_slice(min_year,max_year)
        #self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        self.ax1.set_xlim(years.min(),years.max())
        all_data = self.data[start:end,1:]
        self.y_min = all_data.min()
        self.y_max = all_data.max()
        self.ax1.set_ylim(all_data.min(),all_data.max())
        self._eras()
        self.title = "Number of Publications %d-%d\nAccording to Web of Knowledge" %(years.min(),years.max())
        self.filename = "All Publications %d-%d According to Web of Knowledge" %(years.min(),years.max())
        self.fig.suptitle(self.title, backgroundcolor='w', bbox=dict(boxstyle='round', fc="w", ec="k"))
        for what in self.headers[1:]:
            this_data = self.get_col(what)[start:end]
            self._add_one(what,years,this_data,alpha=1.0, fill_alpha=fill_alpha)
            pass
        legend = self.ax1.legend(loc=2)
        legend.get_frame().set_alpha(0.33)
        self.ax1.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        self.ax1.get_xaxis().set_tick_params(rotation=60)
        print("Saving %s" %self.filename)
        self.fig.savefig("%s.svg" % self.filename, dpi=300)
        plt.close(self.fig)
        return self

    def plot_stack(self,min_year=None,max_year=None,edgecolor='b'):
        self._start()
        start,end,years = self._get_slice(min_year,max_year)
        #self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        self.ax1.set_xlim(years.min(),years.max())
        y1 = self.get_col('Neural Network')[start:end]
        l1 = 'Neural Network'
        y2 = self.get_col('Data Science')[start:end]
        l2 = 'Data Science'
        y3 = self.get_col('Expert Systems')[start:end]
        l3 = 'Expert Systems'
        y4 = self.get_col('Machine Learning')[start:end]
        l4 = 'Machine Learning'
        y5 = self.get_col('Artificial Intelligence')[start:end]
        l5 = 'Artificial Intelligence'
        sums = y1 + y2 + y3 + y4 + y5
        # print("plot_stack(): start_idx = %s, end_idx=%s, years=%s, data=%s"% (start,end,years,sums))
        self.y_min = sums.min()
        self.y_max = sums.max()
        self.ax1.set_ylim(sums.min(),sums.max())
        self._eras()
        self.title = "Number of Publications %d-%d\nAccording to Web of Knowledge" %(years.min(),years.max())
        self.filename = "All Publications Stacked %d-%d According to Web of Knowledge" %(years.min(),years.max())
        self.fig.suptitle(self.title, backgroundcolor='w', bbox=dict(boxstyle='round', fc="w", ec="k"))
        self.ax1.stackplot(years,y1,y2,y3,y4,y5,labels=[l1,l2,l3,l4,l5],alpha=0.25,edgecolor=edgecolor)
        legend = self.ax1.legend(loc=2)
        legend.get_frame().set_alpha(0.33)
        self.ax1.get_xaxis().set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        self.ax1.get_xaxis().set_tick_params(rotation=60)
        print("Saving %s" %self.filename)
        self.fig.savefig("%s.svg" % self.filename, dpi=300)
        plt.close(self.fig)
        return self

    pass

pd = PubData('Web of Knowledge 1960-2018.csv')
for what in pd.headers[1:]:
    pd.plot_one(what,min_year=None,max_year=1980)
    pd.plot_one(what,min_year=None,max_year=1990)
    pd.plot_one(what,min_year=1990,max_year=None)
    pd.plot_one(what,min_year=None,max_year=None)
    pass
pd.plot_stack()
pd.plot_stack(min_year=1960,max_year=1980)
pd.plot_stack(min_year=1960,max_year=1990)
pd.plot_stack(min_year=1990,max_year=None)
pd.plot_all()
pd.plot_all(min_year=1960,max_year=1980)
pd.plot_all(min_year=1960,max_year=1990)
pd.plot_all(min_year=1990,max_year=None)


#plt.show()
