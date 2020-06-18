from __future__ import division
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import pyqtgraph.exporters
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.sparse import vstack
#from scipy.misc import toimage
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

filelist=[]
layer1=[{'a':3.00007920e-01,'w':3.73588869e+01,'b':1.58577373e+03},{'a':1.00000000e+00,'w':3.25172389e+01,'b':2.68203383e+03}]
layer2=[{'a':1.04377489e+00,'w':3.34349819e+01,'b':1.59438802e+03},{'a':7.06298092e-01,'w':6.14683794e+01,'b':2.70286968e+03}]
layer3=[{'a':1.04128278e+00,'w':2.63152833e+01,'b':1.60154940e+03},{'a':6.50155655e-01,'w':5.73486165e+01,'b':2.72324859e+03}]
layer4=[{'a':1.01520762e+00,'w':2.79110458e+01,'b':1.61188139e+03},{'a':5.18657822e-01,'w':6.83826156e+01,'b':2.73099972e+03}]
layer5=[{'a':9.67793017e-01,'w':2.80824430e+01,'b':1.62490732e+03},{'a':4.30042148e-01,'w':6.41600512e+01,'b':2.75285511e+03}]
graphene=[{'a':9.98426340e-01,'w':2.83949973e+01,'b':1.63840546e+03},{'a':4.22730948e-01,'w':7.98338055e+01,'b':2.76274546e+03}]
cdat={'monolayer':layer1,'bilayer':layer2,'trilayer':layer3,'four layers':layer4,'five layers':layer5,'graphene':graphene}

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
        self.flbut.setFixedSize(500,50)
        self.layout.addWidget(self.flbut,0,0)

        self.fitbut=QtWidgets.QPushButton('Do Fitting')
        self.fitbut.clicked.connect(self.doFitting)
        self.fitbut.setEnabled(False)
        self.fitbut.setFixedSize(500,50)
        self.layout.addWidget(self.fitbut,0,1)

        self.download_but=QtWidgets.QPushButton('Download Data')
        self.download_but.clicked.connect(self.downloadData)
        self.download_but.setFixedSize(500,50)
        self.download_but.setEnabled(False)
        self.layout.addWidget(self.download_but,1,1)
        self.download_list=[]

        self.statusBar=QtWidgets.QProgressBar()
        self.layout.addWidget(self.statusBar,0,2)

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
        # else:
        #     self.spect_type='map'

    def doFitting(self):
        if not self.pathmade:
                self.make_temp_dir()
        map_i=1
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
                self.download_but.setEnabled(True)
            # else:

            #     throw error message

    def make_temp_dir(self):
        self.dirpath = tempfile.mkdtemp()
        self.pathmade=True

    def downloadData(self):
        self.downloadMsg.setIcon(QtWidgets.QMessageBox.Question)
        self.downloadMsg.setWindowTitle('Confirm Download')
        self.downloadMsg.setText('The Raman spectrum(s) following files will be downloaded:\n'+'\n'.join('{}'.format(item[0]) for item in self.f_list))
        self.downloadMsg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        # self.downloadMsg.buttonClicked.connect(self.msgbtn)
        self.downloadMsg.exec_()

        # if self.cnfmdnld:
        #     self.zip_files(self.dirpath)
        #     shutil.rmtree(self.dirpath)
        #     self.pathmade=False
        #     self.download_but.setEnabled(False)

    # def msgbtn(self, i):
    #     print(i.text())
    #     if i.text() == 'OK':
    #         self.cnfmdnld=True
    #         print('True')
    #     else:
    #         self.cnfmdnld=False
    #         print('false')

    # def zip_files(self,directory):
    #     zipname=QtWidgets.QFileDialog.getSaveFileName()
    #     shutil.make_archive(zipname[0],'zip',directory)

class SingleSpect(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SingleSpect,self).__init__(parent=parent)
        self.layout=QtWidgets.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

    def Single_Lorentz(self, x,a,w,b):
        return a*(((w/2)**2)/(((x-b)**2)+((w/2)**2)))

    def backgroundFit(self,x,y):
        I_raw=y
        W=x

        polyx=np.array([W[0],W[int(len(W)/2)],W[len(W)-1]])
        polyy=np.array([I_raw[0],I_raw[int(len(W)/2)],I_raw[len(W)-1]])        
        bkgfit=np.polyfit(polyx,polyy,2)
        bkgpoly=(bkgfit[0]*W**2)+(bkgfit[1]*W)+bkgfit[2]
        I_raw=I_raw-bkgpoly
    
        m=(I_raw[len(W)-1]-I_raw[0])/(W[len(W)-1]-W[0])
        b=I_raw[len(W)-1]-m*W[len(W)-1]
        bkglin=m*W+b
    
        I_raw=I_raw-bkglin
    
        I=((I_raw-np.min(I_raw))/np.max(I_raw-np.min(I_raw)));
        return I

    def checkParams(self,G_params,Gp_params):
        x=np.array([1,2,3,4,5,6])
        diffs=[]

        PGp=np.array(Gp_params)
        PG=np.array(G_params)

        layer_keys=['monolayer','bilayer','trilayer','four layers','five layers','graphene']

        for key in layer_keys:
            LGp=np.array([cdat[key][1]['a'],cdat[key][1]['w'],cdat[key][1]['b']])
            LG=np.array([cdat[key][0]['a'],cdat[key][0]['w'],cdat[key][0]['b']])

            dfGp=np.average(np.absolute(100*(PGp-LGp)/LGp),weights=[1,1,0.5])
            dfG=np.average(np.absolute(100*(PG-LG)/LG),weights=[1,1,0.5])
            drat=np.absolute(100*(((PG[0]/PGp[0])-(LG[0]/LGp[0]))/(LG[0]/LGp[0])))
            df=np.average([dfGp,dfG,drat],weights=[0.5,0.5,1])
            diffs.append(df)

        diff_array=np.array(diffs)
        idx=diffs.index(np.min(diff_array))
        
        self.layers=layer_keys[idx]

        self.diff_plot=pg.plot(x,diff_array,pen=None,symbol='o')
        self.diff_plot.setLabel('left',u'\u0394'+'[%]')
        self.diff_plot.setLabel('bottom','# Layers')
        ticks=[list(zip(range(7),('','1','2','3','4','5','graphene')))]
        self.diff_label=self.diff_plot.getAxis('bottom')
        self.diff_label.setTicks(ticks)
        self.diff_plot.win.hide()

    def fitToPlot(self,x,y):
        I=self.backgroundFit(x,y)
        pG=[1.1*np.max(I), 50, 1581.6] #a w b
        pGp=[1.1*np.max(I), 50, 2675]
        pD=[0.1*np.max(I),15,1350]

        #fit G peak
        G_param,G_cov=curve_fit(self.Single_Lorentz,x,y,bounds=([0.3*np.max(I),33,1400],[1.5*np.max(I),60,2000]),p0=pG)
        G_fit=self.Single_Lorentz(x,G_param[0],G_param[1],G_param[2])

        #fit G' peak
        Gp_param,Gp_cov=curve_fit(self.Single_Lorentz,x,y,bounds=([0.3*np.max(I),32,2000],[1.5*np.max(I),60,3000]),p0=pGp)
        Gp_fit=self.Single_Lorentz(x,Gp_param[0],Gp_param[1],Gp_param[2])

        #fit D peak
        D_param,D_cov=curve_fit(self.Single_Lorentz,x,y,bounds=([0,10,1300],[np.max(I),50,1400]),p0=pD)
        D_fit=self.Single_Lorentz(x,D_param[0],D_param[1],D_param[2])

        param_dict={'G':{'a':G_param[0],'w':G_param[1],'b':G_param[2]},'Gp':{'a':Gp_param[0],'w':Gp_param[1],'b':Gp_param[2]},'D':{'a':D_param[0],'w':D_param[1],'b':D_param[2]}}
        with open(raman.newpath+'/spectParams.json','w') as fp:
            data=json.dump(param_dict, fp, sort_keys=True, indent=4)

        y_fit=G_fit+Gp_fit+D_fit
        self.checkParams(G_param,Gp_param)

        test_params=cdat[self.layers]
        G_test=self.Single_Lorentz(x,test_params[0]['a'],test_params[0]['w'],test_params[0]['b'])
        Gp_test=self.Single_Lorentz(x,test_params[1]['a'],test_params[1]['w'],test_params[1]['b'])
        y_test=G_test+Gp_test

        self.fit_plot=pg.plot(x,y_fit,pen='k')
        self.fit_plot.setRange(yRange=[0,1])
        self.fit_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.fit_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.fit_plot.win.hide()

        self.overlay_plot=pg.plot()
        self.overlay_plot.addLegend(offset=(-1,1))
        self.overlay_plot.plot(x,y,pen='g',name='Raw Data')
        self.overlay_plot.plot(x,y_fit,pen='r',name='Fitted Data')
        self.overlay_plot.plot(x,y_test,pen='b',name='Test Data')
        self.overlay_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.overlay_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.overlay_plot.win.hide()
        exporter2=pg.exporters.ImageExporter(self.overlay_plot.plotItem)
        exporter2.params.param('width').setValue(1024, blockSignal=exporter2.widthChanged)
        exporter2.params.param('height').setValue(860, blockSignal=exporter2.heightChanged)
        exporter2.export(raman.newpath+'/overlayplot.png')

        #for i in reversed(range(layout.count())): 
        #    layout.itemAt(i).widget().setParent(None)
        
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
            Quality="""+str(round(1-(D_param[0]/G_param[0]),4))+"""(Ratio of D to G)
            Number of layers (best match): """+self.layers)

        #self.fitting_params.setFixedSize(500,500)
        pal = self.fitting_params.palette()
        pal.setColor(self.fitting_params.backgroundRole(), Qt.white)
        self.fitting_params.setPalette(pal)
        self.fitting_params.setAutoFillBackground(True)
        self.layout.addWidget(self.fitting_params,2,2)

    def plotSpect(self,x,y):
        y_norm=[]
        for i in y:
            y_norm.append((i-np.min(y))/(np.max(y)-np.min(y)))

        self.spect_plot=pg.plot(x,y_norm,pen='k')
        self.spect_plot.setFixedSize(500,500)
        self.spect_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.spect_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.spect_plot.win.hide()

        self.fitToPlot(x,y_norm)

        self.TabWidget=QtWidgets.QTabWidget()
        self.TabWidget.addTab(self.fit_plot,"Fit")
        self.TabWidget.addTab(self.overlay_plot,"Overlay")
        self.TabWidget.addTab(self.diff_plot,"Diffs")
        self.TabWidget.setFixedSize(500,500)

        self.layout.addWidget(self.TabWidget,2,1)
        self.layout.addWidget(self.spect_plot,2,0)


if __name__=='__main__':
    app=QtWidgets.QApplication([])
    raman=GSARaman()
    raman.show()
    app.exec_()