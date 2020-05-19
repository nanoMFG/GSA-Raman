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


# These values come from the fitting in the previous code
G_param=[1.182,60,1493.9977]
Gp_param=[0.7029,60,2697.5451]
D_param=[1.0,50,1350.1404]

filelist=[]

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.mkPen('k')

class GSARaman(QtWidgets.QWidget):
    def __init__(self, mode='local',parent=None):
        super(GSARaman,self).__init__(parent=parent)
        self.singleSpect=SingleSpect()
        self.resize(1440,600)
        self.spect_type=''
        self.data=[]
        self.mode=mode

        self.layout=QtWidgets.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        self.displayWidget=QtWidgets.QStackedWidget()
        self.displayWidget.addWidget(self.singleSpect)
        self.layout.addWidget(self.displayWidget,2,0,1,3)

        self.flbut=QtWidgets.QPushButton('Upload File')
        self.flbut.clicked.connect(self.openFileName)
        self.flbut.setFixedSize(400,50)
        self.layout.addWidget(self.flbut,0,0)

        self.fitbut=QtWidgets.QPushButton('Plot')
        self.fitbut.clicked.connect(self.doFitting)
        self.fitbut.setEnabled(False)
        self.fitbut.setFixedSize(400,50)
        self.layout.addWidget(self.fitbut,0,1)

        self.errmsg=QtWidgets.QMessageBox()
        self.downloadMsg=QtWidgets.QMessageBox()
        self.cnfmdnld=False

        self.pathmade=False

    def openFileName(self):

        if self.mode == 'local':
            try:
                fpath = QtGui.QFileDialog.getOpenFileName()
                if isinstance(fpath,tuple):
                   fpath = fpath[0]
            except Exception as e:
                print(e)
        elif self.mode == 'nanohub':
            try:
                fpath = subprocess.check_output('importfile',shell=True).strip().decode("utf-8")
            except Exception as e:
                print(e)

        filelist.append(fpath)
        if filelist[-1]!=u'':
            if filelist[-1][-3:]!='txt' and filelist[-1][-3:]!='csv':
                self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
                self.errmsg.setText('Please upload a .txt or .csv')
                self.errmsg.exec_()

                del filelist[-1]
            else:
                self.fitbut.setEnabled(True)
        else:
            del filelist[-1]

        self.f_list=filelist

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
                self.fitbut.setEnabled(False)
            else:
            	self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
            	self.errmsg.setText('Please use a single spectrum only')
            	self.errmsg.exec_()


    def make_temp_dir(self):
        self.dirpath = tempfile.mkdtemp()
        self.pathmade=True


class SingleSpect(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SingleSpect,self).__init__(parent=parent)
        self.layout=QtWidgets.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

    def Single_Lorentz(self, x,a,w,b):
        return a*(((w/2)**2)/(((x-b)**2)+((w/2)**2)))

    def fitToPlot(self,x,y):

        G_fit=self.Single_Lorentz(x,G_param[0],G_param[1],G_param[2])

        Gp_fit=self.Single_Lorentz(x,Gp_param[0],Gp_param[1],Gp_param[2])

        D_fit=self.Single_Lorentz(x,D_param[0],D_param[1],D_param[2])

        param_dict={'G':{'a':G_param[0],'w':G_param[1],'b':G_param[2]},'Gp':{'a':Gp_param[0],'w':Gp_param[1],'b':Gp_param[2]},'D':{'a':D_param[0],'w':D_param[1],'b':D_param[2]}}
        with open(raman.newpath+'/spectParams.json','w') as f:
            data=json.dump(param_dict, f, sort_keys=True, indent=4)

        y_fit=G_fit+Gp_fit+D_fit

        self.fit_plot=pg.plot(x,y_fit,pen='k')
        self.fit_plot.setRange(yRange=[0,1])
        self.fit_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.fit_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.fit_plot.win.hide()

        self.overlay_plot=pg.plot()
        self.overlay_plot.addLegend(offset=(-1,1))
        self.overlay_plot.plot(x,y,pen='g',name='Raw Data')
        self.overlay_plot.plot(x,y_fit,pen='r',name='Fitted Data')
        self.overlay_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.overlay_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.overlay_plot.win.hide()
        exporter2=pg.exporters.ImageExporter(self.overlay_plot.plotItem)
        exporter2.params.param('width').setValue(1024, blockSignal=exporter2.widthChanged)
        exporter2.params.param('height').setValue(860, blockSignal=exporter2.heightChanged)
        exporter2.export(raman.newpath+'/overlayplot.png')

        self.layers=' '

        self.fitting_params=QtWidgets.QLabel(
            """Fitting Parameters:
            G Peak:
                """u'\u03b1'"""="""+str(round(G_param[0],4))+"""
                """u'\u0393'"""="""+str(round(G_param[1],4))+"""
                """u'\u03c9'"""="""+str(round(G_param[2],4))+"""
            G' Peak:
                """u'\u03b1'"""="""+str(round(Gp_param[0],4))+"""
                """u'\u0393'"""="""+str(round(Gp_param[1],4))+"""
                """u'\u03c9'"""="""+str(round(Gp_param[2],4))+"""
            D Peak:
                """u'\u03b1'"""="""+str(round(D_param[0],4))+"""
                """u'\u0393'"""="""+str(round(D_param[1],4))+"""
                """u'\u03c9'"""="""+str(round(D_param[2],4))+"""
            Quality="""+str(round(1-(D_param[0]/G_param[0]),4))+"""(Ratio of D to G)"""+self.layers)

        self.fitting_params.setFixedSize(500,500)
        self.layout.addWidget(self.fitting_params,2,2)

    def plotSpect(self,x,y):
        y_norm=[]
        for i in y:
            y_norm.append((i-np.min(y))/(np.max(y)-np.min(y)))

        self.spect_plot=pg.plot(x,y_norm,pen='k')
        self.spect_plot.setFixedSize(400,500)
        self.spect_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.spect_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.spect_plot.win.hide()

        self.fitToPlot(x,y_norm)

        self.TabWidget=QtWidgets.QTabWidget()
        self.TabWidget.addTab(self.fit_plot,"Fit")
        self.TabWidget.addTab(self.overlay_plot,"Overlay")
        self.TabWidget.setFixedSize(500,500)

        self.layout.addWidget(self.TabWidget,2,1)
        self.layout.addWidget(self.spect_plot,2,0)


if __name__=='__main__':
    app=QtWidgets.QApplication([])
    raman=GSARaman()
    raman.show()
    app.exec_()