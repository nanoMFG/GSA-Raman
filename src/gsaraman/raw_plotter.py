from __future__ import division
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
import pyqtgraph.exporters
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.sparse import vstack
from scipy.interpolate import griddata
from PIL.ImageQt import ImageQt
from multiprocessing import Pool
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import qimage2ndarray
import tempfile
import shutil
import os
import zipfile
from zipfile import ZipFile
import json

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.mkPen('k')

filelist = []

class RamanWidget(QtWidgets.QWidget):
    def __init__(self, path, parent=None):
        super(RamanWidget, self).__init__(parent=parent)
        self.viewraman = QtWidgets.QGridLayout(self)
        self.viewraman.setAlignment(QtCore.Qt.AlignTop)
        self.data = []
        self.spect_type = ''
        self.errmsg=QtWidgets.QMessageBox()

        filelist.append(path)
        if filelist[-1]!=u'':
            if filelist[-1][-3:]!='txt' and filelist[-1][-3:]!='csv':
                self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
                self.errmsg.setText('Please upload a .txt or .csv file')
                self.errmsg.exec_()

                del filelist[-1]
        else:
            del filelist[-1]

        self.f_list=filelist

        self.viewraman = pg.PlotWidget()
        self.viewraman.doFitting()

    def make_temp_dir(self):
        self.dirpath = tempfile.mkdtemp()
        self.pathmade=True

    def doFitting(self):
        if not self.pathmade:
                self.make_temp_dir()
        sing_i=1
        for flnm in filelist:
            self.checkFileType(flnm)
            if self.spect_type=='single':

                self.newpath=str(self.dirpath)+'/SingleSpect'+str(sing_i)
                if not os.path.exists(self.newpath):
                    os.makedirs(self.newpath)
                    sing_i+=1
                shutil.copy2(flnm,self.newpath)

                self.widget=self.singleSpect
                self.displayWidget.setCurrentWidget(self.widget)

                x=np.array(self.data.iloc[:,0])
                y=np.array(self.data.iloc[:,1])

                self.widget.plotSpect(x,y)
            else:
            	self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
            	self.errmsg.setText('Please use a single spectrum only')
            	self.errmsg.exec_()

    def checkFileType(self, flnm):
        if flnm[-3:]=='csv':
            self.data=pd.read_csv(flnm)
        else:
            self.data=pd.read_table(flnm)

        cols=self.data.shape[1]
        rows=self.data.shape[0]
        if cols == 1:
            self.data=pd.DataFrame(self.data.iloc[0:rows/2,0],self.data.iloc[rows/2:rows,0])
            self.spect_type='single'
        elif cols == 2:
            self.spect_type='single'
            if type(self.data.iloc[0,0]) is str:
                self.data=self.data.iloc[1:rows,:]
            else:
                self.data=self.data

    def plotSpect(self,x,y):
        y_norm=[]
        for i in y:
            y_norm.append((i-np.min(y))/(np.max(y)-np.min(y)))

        self.spect_plot=pg.plot(x,y_norm,pen='k')
        self.spect_plot.setFixedSize(400,500)
        self.spect_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.spect_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.spect_plot.win.hide()