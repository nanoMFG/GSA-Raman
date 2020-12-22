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
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import qimage2ndarray
import shutil
import subprocess, os, sys
import json
from util.gwidgets import *
from util.icons import Icon
from utility import errorCheck
import zipfile
import tempfile


IMPORT_LOCATION = "/apps/importfile/bin/importfile"

filelist=[]
layer1=[{'a':3.00007920e-01,'w':3.73588869e+01,'b':1.58577373e+03},{'a':1.00000000e+00,'w':3.25172389e+01,'b':2.68203383e+03}]
layer2=[{'a':1.04377489e+00,'w':3.34349819e+01,'b':1.59438802e+03},{'a':7.06298092e-01,'w':6.14683794e+01,'b':2.70286968e+03}]
layer3=[{'a':1.04128278e+00,'w':2.63152833e+01,'b':1.60154940e+03},{'a':6.50155655e-01,'w':5.73486165e+01,'b':2.72324859e+03}]
layer4=[{'a':1.01520762e+00,'w':2.79110458e+01,'b':1.61188139e+03},{'a':5.18657822e-01,'w':6.83826156e+01,'b':2.73099972e+03}]
layer5=[{'a':9.67793017e-01,'w':2.80824430e+01,'b':1.62490732e+03},{'a':4.30042148e-01,'w':6.41600512e+01,'b':2.75285511e+03}]
graphite=[{'a':9.98426340e-01,'w':2.83949973e+01,'b':1.63840546e+03},{'a':4.22730948e-01,'w':7.98338055e+01,'b':2.76274546e+03}]
cdat={'monolayer':layer1,'bilayer':layer2,'trilayer':layer3,'four layers':layer4,'five layers':layer5,'graphite':graphite}

BLFitDegrees=['2','3','4','5','6','7','8']
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.mkPen('k')
devel = False

QW=QtWidgets
QC=QtCore
QG=QtGui

class Main(QW.QMainWindow):
    """
    Main window containing the GSARaman widget. Adds menu bar / tool bar functionality.
    """
    def __init__(self,mode='local', repo_dir = '', *args,**kwargs):
        super(Main,self).__init__(*args,**kwargs)

        self.mode = mode # define mode, default set as 'local', can also be 'nanohub'
        self.repo_dir = repo_dir # define mode, default set as '', will call REPO_DIR which is set in invoke
        self.mainWidget = GSARaman(mode=mode) # 'mainWidget' is assigned to the GSARaman class, which is a QtWidget; mode variable is transferred
        self.setCentralWidget(self.mainWidget)
        self.resize(1280,720)

        # building main menu
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)

        importAction = QG.QAction("&Import",self) 
        importAction.setIcon(Icon('download.svg'))
        importAction.triggered.connect(self.mainWidget.openFileName)

        exportAction = QG.QAction("&Export",self)
        exportAction.setIcon(Icon('upload.svg'))
        exportAction.triggered.connect(self.mainWidget.menubarExport)

        clearAction = QG.QAction("&Clear",self)
        clearAction.setIcon(Icon('trash.svg'))
        clearAction.triggered.connect(self.mainWidget.clearPast)

        exitAction = QG.QAction("&Exit",self)
        exitAction.setIcon(Icon('log-out.svg'))
        exitAction.triggered.connect(self.close)
        
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(importAction)
        fileMenu.addAction(exportAction)
        fileMenu.addAction(clearAction)
        if mode == 'local':
            fileMenu.addAction(exitAction)

        aboutAction = QG.QAction("&About",self)
        aboutAction.setIcon(Icon('info.svg'))
        aboutAction.triggered.connect(self.showAboutDialog)

        testImageAction = QG.QAction("&Import Test Spectrum",self)
        testImageAction.setIcon(Icon('image.svg'))
        testImageAction.triggered.connect(self.importTestSpectrum)

        helpMenu = mainMenu.addMenu('&Help')
        helpMenu.addAction(testImageAction)
        helpMenu.addAction(aboutAction)

        self.show()

    def showAboutDialog(self):
        about_dialog = QW.QMessageBox(self)
        about_dialog.setText("About This Tool")
        about_dialog.setWindowModality(QC.Qt.WindowModal)
        copyright_path = os.path.join(self.repo_dir,'COPYRIGHT')
        print(f"okay:{copyright_path}")
        if os.path.isfile(copyright_path):
            with open(copyright_path,'r') as f:
                copyright = f.read()
                print(f"hey:{copyright}")
        else:
            copyright = ""

        version_path =  os.path.join(self.repo_dir,'VERSION')
        if os.path.isfile(version_path):
            with open(os.path.join(self.repo_dir,'VERSION'),'r') as f:
                version = f.read()
        else:
            version = ""

        # Needs text
        about_text = "Version: %s \n\n"%version
        about_text += copyright

        about_dialog.setInformativeText(about_text)
        about_dialog.exec()

    def importTestSpectrum(self):
        if devel:
            print('Starting importTestSpectrum')

        path = os.path.join(self.repo_dir,'data','raw','spectest.csv')
        filelist.append(path)
        self.mainWidget.loadData(filelist[-1])
        self.mainWidget.fittingBtn.setEnabled(True)

        if devel:
            print('Ending importTestSpectrum')

class GSARaman(QtWidgets.QWidget):
    def __init__(self, mode='local',parent=None,*args,**kwargs):
        super(GSARaman,self).__init__(*args,**kwargs)
        
        if devel:
            print('Starting GSARaman')

        # self.resize(1280,720)
        self.singleSpect = SingleSpect()
        # self.mapSpect = MAPSpect()
        self.spect_type = ''
        self.mode = mode
        self.data = []

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        # -------------------- SpectWidget --------------------
        self.SpectWidget = QtWidgets.QStackedWidget()
        self.SpectWidget.addWidget(self.singleSpect)
        #self.SpectWidget.addWidget(self.mapSpect)
        # -------------------- -------------------- --------------------        

        # -------------------- All the buttons --------------------
        # Upload File Button: 
            # 1. Allows user to upload a csv or txt file
            # 2. After successful upload, clears all plots, clears fitted values, disables Do Fitting Button, disables Export Data Button
            # 3. Displays the raw spectrum
            # 4. Activates the Fit Baseline Button and dropdown menu
            # 4. Fits baseline to polynomial of degree 2 by default
            # 5. Displays normalised spectrum
            # 6. Activates Do Fitting Button
        self.uploadBtn = QtWidgets.QPushButton('Upload File')
        self.uploadBtn.clicked.connect(self.openFileName)
        self.uploadBtn.setFixedSize(320,50)

        # Do Fitting Button: 
            # 1. Fits the normalised spectrum
            # 2. Runs statusBar
            # 3. Displays fitted spectrum
            # 4. Displays overlaid spectra
            # 5. Displays diffs plot
            # 6. Displays fitting parameters
            # 7. Activates Export Data Button
        self.fittingBtn = QtWidgets.QPushButton('Do Fitting')
        self.fittingBtn.clicked.connect(self.doFitting)
        self.fittingBtn.setEnabled(False)
        self.fittingBtn.setFixedSize(320,50)

        # Export Data Button: 
            # 1. Zips the fitted spectrum (image), overlaid spectra (image), diffs plot (image) and fitting parameters (text)
            # 2. Downloads the zip file
        self.exportBtn = QtWidgets.QPushButton('Export Data')
        self.exportBtn.clicked.connect(self.exportData)
        self.exportBtn.setEnabled(False)
        self.exportBtn.setFixedSize(320,50)
        self.export_list = []

        # Progress Bar:
            # Progress bar for Do Fitting Button
            # Mainly useful for MAP files
        self.statusBar = QtWidgets.QProgressBar()
        self.statusBar.setFixedHeight(50)
        # -------------------- -------------------- --------------------

        # -------------------- Adding components to main GSARaman widget --------------------
        self.layout.addWidget(self.uploadBtn,0,0,1,1)
        self.layout.addWidget(self.fittingBtn,0,1,1,1)
        self.layout.addWidget(self.exportBtn,0,2,1,1)
        self.layout.addWidget(self.statusBar,0,3,1,1)
        self.layout.addWidget(self.SpectWidget,1,0,1,4)
        # -------------------- -------------------- --------------------

        if devel:
            print('Ending GSARaman')

    # Opens file based on mode; appends file path to 'filelist'
    #@errorCheck(show_traceback=True)
    def openFileName(self):

        if devel: 
            print('Starting openFileName')

        if self.mode == 'local':
            fpath = QtGui.QFileDialog.getOpenFileName()
            if isinstance(fpath,tuple):
                fpath = fpath[0]
        elif self.mode == 'nanohub':
            fpath = subprocess.check_output(IMPORT_LOCATION,shell=True).strip().decode("utf-8")

        filelist.append(fpath)

        if filelist[-1]!=u'':
            if filelist[-1][-3:]!='txt' and filelist[-1][-3:]!='csv':
                del filelist[-1]
                raise ValueError('Please upload a .txt or .csv file')
            else:
                self.loadData(filelist[-1])
        else:
            del filelist[-1]

        self.fittingBtn.setEnabled(True)

        if devel:
            print('Ending openFileName')


    #@errorCheck(show_traceback=True)
    def loadData(self, path):

        if devel: 
            print('Starting loadData')

        if path[-3:]=='csv':
            self.data=pd.read_csv(path)
        else:
            self.data=pd.read_table(path)

        cols=self.data.shape[1]
        rows=self.data.shape[0]

        if cols == 1:
            self.clearPast()
            self.data=pd.DataFrame(self.data.iloc[0:rows/2,0],self.data.iloc[rows/2:rows,0])
            self.setSingle()
        elif cols == 2:
            if type(self.data.iloc[0,0]) is str:
                self.clearPast()
                self.data=self.data.iloc[1:rows,:]
                self.setSingle()
            else:
                self.clearPast()
                self.data=self.data
                self.setSingle()
        else:
            del filelist[-1]
            self.data = []
            raise ValueError('Please use a single spectrum only')

        if devel:
            print('Ending loadData')


    def clearPast(self):

        if devel:
            print('Starting clearPast')

        if self.SpectWidget.isVisible():
            # self.SpectWidget.close()
            self.fittingBtn.setEnabled(False)
            self.exportBtn.setEnabled(False)

        if devel:
            print('Ending clearPast')

            # clear data
            # clear degree??
            # clear norm plot
            # clear BL plot
            # clear Fit plot
            # clear Overlay plot
            # clear Diffs plot
            # clear Fitting Params Widget


    def setSingle(self):

        if devel:
            print('Starting setSingle')

        del filelist[-1]
        self.spect_type='single'
        self.SpectWidget.setCurrentWidget(self.singleSpect)

        self.singleSpect.normPlotter(self.data)

        if devel:
            print('Ending setSingle')


    # def setMAP(self):


    def doFitting(self):

        if devel: 
            print('Starting doFitting')

        if self.spect_type == 'single':
            self.singleSpect.fitToPlot()
            self.statusBar.setValue(100)
        #elif self.spect_type == 'MAP'

        self.exportBtn.setEnabled(True)

        if devel:
            print('Ending doFitting')


    def check_extension(self, file_name, extensions):
        return any([(file_name[-4:]==ext and len(file_name)>4) for ext in extensions])


    def retrieve_file_paths(self,dirName):
 
        filePaths = []

        for root, directories, files in os.walk(dirName):
            for filename in files:
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        return filePaths

    def exportData(self):
        dirpath = tempfile.mkdtemp()
        self.singleSpect.normPlot_exporter.export(os.path.join(dirpath,'Normalised_Plot.png'))
        self.singleSpect.BaselinePlot_exporter.export(os.path.join(dirpath,'Baseline_Fit_Plot.png'))
        self.singleSpect.fit_plot_exporter.export(os.path.join(dirpath,'Fitted_Plot.png'))
        self.singleSpect.overlay_plot_exporter.export(os.path.join(dirpath,'Overlay_Plot.png'))
        self.singleSpect.diff_plot_exporter.export(os.path.join(dirpath,'Diffs_Plot.png'))

        with open(os.path.join(dirpath,'fitting_paramters.txt'),'w') as resultsfile:
            resultsfile.write("Fitting Parameters: %s" %self.singleSpect.values_text)

        if self.mode == 'local':
            path = os.path.join(os.getcwd(),"data")
            name = QtWidgets.QFileDialog.getSaveFileName(None, 
                "Export Data", 
                path, 
                "ZIP File (*.zip)",
                "ZIP File (*.zip)")[0]
            if name != '' and self.check_extension(name, [".zip"]):
                shutil.make_archive((name[:-4]), 'zip',dirpath) 
                shutil.rmtree(dirpath)
        elif self.mode == 'nanohub':
            filepaths = self.retrieve_file_paths(dirpath)
            zip_file = zipfile.ZipFile('data.zip','w')
            with zip_file:
                for fname in filepaths:
                    zip_file.write(fname)
            path = os.path.join(os.getcwd(),zip_file)
            subprocess.check_output('exportfile %s'%path,shell=True)
            shutil.rmtree(dirpath)
        else:
            return

        #path = os.path.join(os.getcwd(),"data")
        #name = QtWidgets.QFileDialog.getSaveFileName(None, 
        #    "Export Data", 
        #    path, 
        #    "ZIP File (*.zip)",
        #    "ZIP File (*.zip)")[0]
        #print(type(name))
        #print(name)
        #if name != '' and self.check_extension(name, [".zip"]):
        #    shutil.make_archive((name[:-4]), 'zip',dirpath) 
        #shutil.rmtree(dirpath)


    #@errorCheck(show_traceback=True)
    def menubarExport(self):

        if devel:
            print('Starting menubarExport')

        if self.exportBtn.isEnabled():
            if self.spect_type == 'single':
                self.exportData()
            #elif self.spect_type == 'MAP'
        else:
            raise ValueError('Nothing to export')

        if devel:
            print('Ending menubarExport')


class SingleSpect(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SingleSpect,self).__init__(parent=parent)

        if devel:
            print('Starting SingleSpect')

        self.layout=QtWidgets.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        #self.data = []
        self.frequency = []
        # self.intensity_norm = []
        self.I_BL = []

        # -------------------- NormPlotWidget --------------------
        self.NormPlotWidget = QtWidgets.QWidget()
        self.normplotlayout = QtGui.QGridLayout()
        self.NormPlotWidget.setLayout(self.normplotlayout)
        self.NormPlotWidget.resize(400,500)
        # -------------------- -------------------- --------------------

        # -------------------- BLFitDrop --------------------
        self.BLFitDrop = QW.QComboBox()
        self.BLFitDrop.addItems(BLFitDegrees)
        self.BLFitDrop.setCurrentIndex(0)
        self.BLFitDrop.resize(80,50)
        self.BLFitDrop.setFixedHeight(50)
        # -------------------- -------------------- --------------------

        # -------------------- BLFitBtn --------------------
        self.BLFitBtn = QtWidgets.QPushButton('Fit BL')
        self.BLFitBtn.setEnabled(False)
        self.BLFitBtn.resize(160,50)
        self.BLFitBtn.setFixedHeight(50)
        # -------------------- -------------------- --------------------

        # -------------------- RawPlotWidget --------------------
        self.RawPlotWidget = QtWidgets.QWidget()
        self.rawplotlayout = QtGui.QGridLayout()
        self.RawPlotWidget.setLayout(self.rawplotlayout)
        self.RawPlotWidget.resize(400,620)
        self.rawplotlayout.addWidget(SubheaderLabel('Raw Plot'),0,0,1,3)
        self.rawplotlayout.addWidget(self.NormPlotWidget,1,0,1,3)
        self.rawplotlayout.addWidget(BasicLabel('BL Degree:'),2,0,1,1)
        self.rawplotlayout.addWidget(self.BLFitDrop,2,1,1,1)
        self.rawplotlayout.addWidget(self.BLFitBtn,2,2,1,1)
        # -------------------- -------------------- --------------------

        # -------------------- TabWidget --------------------
        self.TabWidget=QtWidgets.QTabWidget()
        self.TabWidget.resize(500,500)
        self.TabWidget.setTabPosition(QtGui.QTabWidget.South)
        # -------------------- -------------------- --------------------

        # -------------------- FittedPlotWidget --------------------
        # Gets inserted into DisplayWidget
        # Contains 2 parts:
            # (0,0): Heading = "Fitted Plots"
            # (1,0): tabs of nromalised, fit, overlay and diffs plot = TabWidget
        self.FittedPlotWidget = QtWidgets.QWidget()
        fittedplotwidgetlayout = QtGui.QGridLayout()
        self.FittedPlotWidget.setLayout(fittedplotwidgetlayout)
        self.FittedPlotWidget.resize(500,620)
        fittedplotwidgetlayout.addWidget(SubheaderLabel('Fitted Plots'),0,0)
        fittedplotwidgetlayout.addWidget(self.TabWidget,1,0)
        # -------------------- -------------------- --------------------

        # -------------------- DisplayWidget --------------------
        self.DisplayWidget = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.DisplayWidget.addWidget(self.RawPlotWidget)
        self.DisplayWidget.addWidget(self.FittedPlotWidget)
        # self.DisplayWidget.resize(900,620)
        # -------------------- -------------------- --------------------

        # -------------------- DataWidget --------------------
        # Gets inserted into main GSARaman widget
        # Contains 2 parts:
            # (0,0): Heading = "Fitting Data"
            # (1,0): contains values of the fitting parameters = valuesWidget
        self.DataWidget = QtWidgets.QWidget()
        self.datawidgetlayout = QtGui.QGridLayout()
        self.DataWidget.setLayout(self.datawidgetlayout)
        self.DataWidget.resize(340,620)
        self.DataWidget.setFixedWidth(340)
        self.datawidgetlayout.addWidget(SubheaderLabel('Fitting Parameters'),0,0)
        # -------------------- -------------------- --------------------

        # -------------------- Adding components to SingleSpect widget --------------------
        self.layout.addWidget(self.DisplayWidget,0,0)
        self.layout.addWidget(self.DataWidget,0,1)
        # -------------------- -------------------- --------------------

        if devel:
            print('Ending SingleSpect')

    def normPlotter(self, data):

        if devel:
            print('Starting normPlotter')

        self.frequency = np.array(data.iloc[:,0])
        intensity = np.array(data.iloc[:,1])
        length = len(self.frequency)
        a = 0
        for i in range(length):
            if self.frequency[i]<=0:
                a = a+1
            else:
                break
        self.frequency = self.frequency[a:]
        intensity = intensity[a:]

        self.intensity_norm = []
        for i in intensity:
            self.intensity_norm.append((i-np.min(intensity))/(np.max(intensity)-np.min(intensity)))

        # -------------------- Add plot to NormPlotWidget --------------------
        self.normPlot = pg.PlotWidget(title='Normalised Spectrum',enableMenu=False,antialias=True)
        self.normPlot.plot(self.frequency, self.intensity_norm,pen=pg.mkPen('k',width=4),brush=pg.mkBrush('b',alpha=0.3))
        self.normPlot.setLabel('left','I<sub>norm</sub>[arb]')
        self.normPlot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.normPlot.setXRange(self.frequency[0],self.frequency[len(self.frequency)-1])

        self.normPlot_exporter = pg.exporters.ImageExporter(self.normPlot.getPlotItem())
        self.normPlot_exporter.params.param('width').setValue(1920, blockSignal=self.normPlot_exporter.widthChanged)
        self.normPlot_exporter.params.param('height').setValue(1080, blockSignal=self.normPlot_exporter.heightChanged)

        self.normplotlayout.addWidget(self.normPlot,0,0)
        # -------------------- -------------------- --------------------

        self.BLFitBtn.setEnabled(True)
        self.BLPlot(2, self.frequency, self.intensity_norm)

        # -------------------- Get value from BLFitDrop --------------------
        self.degree = int(self.BLFitDrop.currentText())
        # -------------------- -------------------- --------------------

        # -------------------- Assign button trigger for BLFitBtn --------------------
        self.BLFitBtn.clicked.connect(self.BLBtnTrigger)
        # -------------------- -------------------- --------------------

        if devel:
            print('Ending normPlotter')


    def BLBtnTrigger(self):

        if devel:
            print('Starting BLBtnTrigger')

        self.BLPlot(self.degree,self.frequency,self.intensity_norm)

        if devel:
            print('Ending BLBtnTrigger')


    def BLPlot(self, degree, x, y):

        if devel:
            print('Starting BLPlot')

        n = degree
        I_raw = y
        W = x

        polyx = np.array([W[0],W[int(len(W)/2)],W[len(W)-1]])
        polyy = np.array([I_raw[0],I_raw[int(len(W)/2)],I_raw[len(W)-1]])        
        bkgfit = np.polyfit(polyx,polyy,degree)
        bkgpoly = 0
        for i in range(n):
            bkgpoly = bkgpoly + (bkgfit[i]*W**(n-i))
        I_raw = I_raw-bkgpoly
    
        m = (I_raw[len(W)-1]-I_raw[0])/(W[len(W)-1]-W[0])
        b = I_raw[len(W)-1]-m*W[len(W)-1]
        bkglin = m*W+b
    
        I_raw = I_raw-bkglin
    
        self.I_BL = ((I_raw-np.min(I_raw))/np.max(I_raw-np.min(I_raw)))

        # -------------------- BaselinePlot --------------------
        self.BaselinePlot = pg.PlotWidget(title='Baseline Corrected Spectrum',enableMenu=False,antialias=True)
        self.BaselinePlot.plot(self.frequency, self.I_BL,pen=pg.mkPen('k',width=4),brush=pg.mkBrush('b',alpha=0.3))
        self.BaselinePlot.setLabel('left','I<sub>norm</sub>[arb]')
        self.BaselinePlot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.BaselinePlot.setXRange(self.frequency[0],self.frequency[len(self.frequency)-1])

        self.BaselinePlot_exporter = pg.exporters.ImageExporter(self.BaselinePlot.getPlotItem())
        self.BaselinePlot_exporter.params.param('width').setValue(1920, blockSignal=self.BaselinePlot_exporter.widthChanged)
        self.BaselinePlot_exporter.params.param('height').setValue(1080, blockSignal=self.BaselinePlot_exporter.heightChanged)
        # -------------------- -------------------- --------------------

        # -------------------- Add BL to TabWidget --------------------
        for i in list(reversed(range(self.TabWidget.count()))):
            self.TabWidget.removeTab(i)
        self.TabWidget.addTab(self.BaselinePlot,"BL")
        # -------------------- -------------------- --------------------

        if devel:
            print('Ending BLPlot')


    def Single_Lorentz(self, x,a,w,b):
        return a*(((w/2)**2)/(((x-b)**2)+((w/2)**2)))


    def fitToPlot(self):

        if devel:
            print('Starting fitToPlot')

        x = self.frequency
        y = self.intensity_norm
        I = self.I_BL

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

        y_fit=G_fit+Gp_fit+D_fit

        self.checkDiffs(G_param,Gp_param)

        test_params=cdat[self.layers]
        G_test=self.Single_Lorentz(x,test_params[0]['a'],test_params[0]['w'],test_params[0]['b'])
        Gp_test=self.Single_Lorentz(x,test_params[1]['a'],test_params[1]['w'],test_params[1]['b'])
        y_test=G_test+Gp_test

        # -------------------- fit_plot --------------------
        self.fit_plot = pg.PlotWidget(title='Fitted Spectrum',enableMenu=False,antialias=True)
        self.fit_plot.plot(x,y_fit,pen='k')
        self.fit_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.fit_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.fit_plot.setRange(yRange=[0,1])
        self.fit_plot.setXRange(x[0],x[len(x)-1])

        self.fit_plot_exporter = pg.exporters.ImageExporter(self.fit_plot.getPlotItem())
        self.fit_plot_exporter.params.param('width').setValue(1920, blockSignal=self.fit_plot_exporter.widthChanged)
        self.fit_plot_exporter.params.param('height').setValue(1080, blockSignal=self.fit_plot_exporter.heightChanged)
        # -------------------- -------------------- --------------------

        # -------------------- overlay_plot --------------------
        self.overlay_plot=pg.PlotWidget(title='Overlay Spectrum',enableMenu=False,antialias=True)
        self.overlay_plot.addLegend(offset=(-1,1))
        self.overlay_plot.plot(x,I,pen='g',name='Raw Data')
        self.overlay_plot.plot(x,y_fit,pen='r',name='Fitted Data')
        self.overlay_plot.plot(x,y_test,pen='b',name='Test Data')
        self.overlay_plot.setLabel('left','I<sub>norm</sub>[arb]')
        self.overlay_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        self.overlay_plot.setXRange(x[0],x[len(x)-1])

        self.overlay_plot_exporter = pg.exporters.ImageExporter(self.overlay_plot.getPlotItem())
        self.overlay_plot_exporter.params.param('width').setValue(1920, blockSignal=self.overlay_plot_exporter.widthChanged)
        self.overlay_plot_exporter.params.param('height').setValue(1080, blockSignal=self.overlay_plot_exporter.heightChanged)
        # -------------------- -------------------- --------------------
        
        # -------------------- Add Fit, Overlay and Diffs to TabWidget --------------------
        self.TabWidget.addTab(self.fit_plot,"Fit")
        self.TabWidget.addTab(self.overlay_plot,"Overlay")
        self.TabWidget.addTab(self.diff_plot,"Diffs")
        self.TabWidget.setCurrentWidget(self.fit_plot)
        # -------------------- -------------------- --------------------        

        # -------------------- valuesWidget --------------------
        # Gets inserted into DataWidget
        # Contains all the fitting parameters
        self.values_text = ("""
        G Peak:
            alpha="""+str(round(G_param[0],4))+"""
            gamma="""+str(round(G_param[1],4))+"""
            omega="""+str(round(G_param[2],4))+"""
        G' Peak:
            alpha="""+str(round(Gp_param[0],4))+"""
            gamma="""+str(round(Gp_param[1],4))+"""
            omega="""+str(round(Gp_param[2],4))+"""
        D Peak:
            alpha="""+str(round(D_param[0],4))+"""
            gamma="""+str(round(D_param[1],4))+"""
            omega="""+str(round(D_param[2],4))+"""
        Quality="""+str(round(1-(D_param[0]/G_param[0]),4))+"""(1 - Intensity(D)/(G))
        Number of layers (best match): """+self.layers)
        self.valuesWidget = QtWidgets.QLabel(self.values_text)
        self.valuesWidget.resize(340,500)
        self.valuesWidget.setFixedWidth(340)
        # -------------------- -------------------- --------------------

        # -------------------- Add valuesWidget to DataWidget --------------------
        self.datawidgetlayout.addWidget(self.valuesWidget,1,0)
        # -------------------- -------------------- --------------------

        if devel:
            print('Ending fitToPlot')


    def checkDiffs(self,G_params,Gp_params):

        if devel:
            print('Starting checkDiffs')

        x=np.array([1,2,3,4,5,6])
        diffs=[]

        PGp=np.array(Gp_params)
        PG=np.array(G_params)

        layer_keys=['monolayer','bilayer','trilayer','four layers','five layers','graphite']

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

        self.diff_plot=pg.PlotWidget(title='Overlay Spectrum',enableMenu=False,antialias=True)
        self.diff_plot=pg.plot(x,diff_array,pen=None,symbol='o')
        self.diff_plot.setLabel('left',u'\u0394'+'[%]')
        self.diff_plot.setLabel('bottom','# Layers')
        self.diff_plot.win.hide()
        ticks=[list(zip(range(7),('','1','2','3','4','5','graphite')))]
        self.diff_label=self.diff_plot.getAxis('bottom')
        self.diff_label.setTicks(ticks)

        self.diff_plot_exporter = pg.exporters.ImageExporter(self.diff_plot.getPlotItem())
        self.diff_plot_exporter.params.param('width').setValue(1920, blockSignal=self.diff_plot_exporter.widthChanged)
        self.diff_plot_exporter.params.param('height').setValue(1080, blockSignal=self.diff_plot_exporter.heightChanged)

        if devel:
            print('Ending checkDiffs')
        # -------------------- -------------------- --------------------


def main():
    nargs = len(sys.argv)
    if nargs > 1:
        mode = sys.argv[1]
    else:
        mode = 'local'
    if mode not in ['nanohub','local']:
        mode = 'local'

    REPO_DIR = "."
    if mode == 'local':
        REPO_DIR = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
    else:
        if os.environ.get("RUN_LOCATION"):
            REPO_DIR = os.environ.get("RUN_LOCATION")
    
    app=QtWidgets.QApplication([])
    raman=Main(mode=mode, repo_dir=REPO_DIR)
    #raman.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

# if __name__=='__main__':
#     REPO_DIR = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
#     app=QtWidgets.QApplication([])
#     raman=Main(mode=mode, repo_dir=REPO_DIR)
#     raman.show()
#     app.exec_()
