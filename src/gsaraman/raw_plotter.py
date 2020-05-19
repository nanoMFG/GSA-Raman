from PyQt5 import QtGui, QtCore, QtWidgets 
import pyqtgraph as pg 
import pyqtgraph.exporters 
import pandas as pd 
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg 
import pyqtgraph.exporters 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
#from skimage import util
from gsaraman.util import errorCheck
import os,subprocess,sys

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class RamanWidget(QtWidgets.QWidget):
    def __init__(self, path, specttype='single', *args,**kwargs):
        super(RamanWidget, self).__init__(*args,**kwargs)
        layout = QtWidgets.QGridLayout(self)
        self.data = []
        self.spect_type = specttype

        self.checkFileType(path)
        frequency, intensity_norm = self.loadData(path)

        self.plot_spect = pg.PlotWidget()
        self.plot_spect.plot(frequency,intensity_norm,pen=pg.mkPen('k',width=4),brush=pg.mkBrush('b',alpha=0.3))
        # self.plot_spect = pg.plot(frequency,intensity_norm,pen=pg.mkPen('k',width=4),brush=pg.mkBrush('b',alpha=0.3))
        self.plot_spect.setLabel('left','I<sub>norm</sub>[arb]')
        self.plot_spect.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
        #self.plot_spect.win.hide()

        layout.addWidget(self.plot_spect,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)

    @errorCheck()
    def checkFileType(self, path):
        if path[-3:]!='txt' and path[-3:]!='csv':
            raise ValueError('Please upload a .txt or .csv file')

    @errorCheck(show_traceback=True)
    def loadData(self, path):
        if path[-3:]=='csv':
            self.data=pd.read_csv(path)
        else:
            self.data=pd.read_table(path)

        cols=self.data.shape[1]
        rows=self.data.shape[0]

        if cols == 1:
            self.data=pd.DataFrame(self.data.iloc[0:rows/2,0],self.data.iloc[rows/2:rows,0])
        elif cols == 2:
            if type(self.data.iloc[0,0]) is str:
                self.data=self.data.iloc[1:rows,:]
            else:
                self.data=self.data
        else:
            raise ValueError('Please use a single spectrum only')

        frequency=np.array(self.data.iloc[:,0])
        intensity=np.array(self.data.iloc[:,1])

        intensity_norm=[]
        for i in intensity:
            intensity_norm.append((i-np.min(intensity))/(np.max(intensity)-np.min(intensity)))

        return frequency, intensity_norm


# from PyQt5 import QtGui, QtCore, QtWidgets 
# import pyqtgraph as pg 
# import pyqtgraph.exporters 
# import pandas as pd 
# import numpy as np 
# #from scipy.optimize import curve_fit 
# #from scipy.sparse import vstack 
# #from scipy.interpolate import griddata 
# # from multiprocessing import Pool 
# import matplotlib.pyplot as plt 
# #import qimage2ndarray 
# #import tempfile 
# #import shutil 
# #import os 
# #import zipfile 
# #from zipfile import ZipFile 
# #import json
# from util.util import errorCheck

# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')
# # pg.mkPen('k')

# #filelist = []

# class RamanWidget(QtWidgets.QWidget):
#     def __init__(self, path, filetype='single', *args,**kwargs):
#         super(RamanWidget, self).__init__(*args,**kwargs)
#         viewraman = QtWidgets.QGridLayout(self)
#         addwidget
#         viewraman.setAlignment(QtCore.Qt.AlignTop)
#         self.data = {"frequency":[],"intensity":[]}
#         self.spect_type = filetype
#         # self.errmsg=QtWidgets.QMessageBox()

#         self.loadData(path,filetype)

#         self.plot = pg.PlotWidget()
#         self.plot.setLabel('left','I<sub>norm</sub>[arb]')
#         self.plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')

#         # filelist.append(path)
#         # if filelist[-1]!=u'':
#         #     if filelist[-1][-3:]!='txt' and filelist[-1][-3:]!='csv':
#         #         self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
#         #         self.errmsg.setText('Please upload a .txt or .csv file')
#         #         self.errmsg.exec_()

#         #         del filelist[-1]
#         # else:
#         #     del filelist[-1]

#         # self.f_list=filelist

#         self.doFitting()

#     # def make_temp_dir(self):
#     #     self.dirpath = tempfile.mkdtemp()
#     #     self.pathmade=True

#     def doFitting(self):
#         # if not self.pathmade:
#         #         self.make_temp_dir()
#         # sing_i=1
#         # for flnm in filelist:
#             # self.checkFileType(flnm)
#             if check if single:
#                 stuff
#             else:
#                 raise ValueError('Shitty filetype')
#             # if self.spect_type=='single':

#             #     self.newpath=str(self.dirpath)+'/SingleSpect'+str(sing_i)
#             #     if not os.path.exists(self.newpath):
#             #         os.makedirs(self.newpath)
#             #         sing_i+=1
#             #     shutil.copy2(flnm,self.newpath)

#                 # self.widget=self.singleSpect
#                 # self.displayWidget.setCurrentWidget(self.widget)

#                 x=np.array(self.data.iloc[:,0])
#                 y=np.array(self.data.iloc[:,1])

#                 y_norm=[]
#                 for i in y:
#                     y_norm.append((i-np.min(y))/(np.max(y)-np.min(y)))

#                 self.plot.plot(x,y_norm,pen=pg.mkPen('k',width=4),brush=pg.mkBrush('b',alpha=0.3))
#             # else:
#             #     self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
#             #     self.errmsg.setText('Please use a single spectrum only')
#             #     self.errmsg.exec_()

#     def loadData(self,filepath):
#         pass

#     def checkFileType(self, flnm):
#         if flnm[-3:]=='csv':
#             self.data=pd.read_csv(flnm)
#         else:
#             self.data=pd.read_table(flnm)

#         cols=self.data.shape[1]
#         rows=self.data.shape[0]
#         if cols == 1:
#             self.data=pd.DataFrame(self.data.iloc[0:rows/2,0],self.data.iloc[rows/2:rows,0])
#             self.spect_type='single'
#         elif cols == 2:
#             self.spect_type='single'
#             if type(self.data.iloc[0,0]) is str:
#                 self.data=self.data.iloc[1:rows,:]
#             else:
#                 self.data=self.data

#     # def plotSpect(self,x,y):
#     #     y_norm=[]
#     #     for i in y:
#     #         y_norm.append((i-np.min(y))/(np.max(y)-np.min(y)))

#     #     self.spect_plot=pg.plot(x,y_norm,pen='k')
#     #     # self.spect_plot.setFixedSize(400,500)
#     #     self.spect_plot.setLabel('left','I<sub>norm</sub>[arb]')
#     #     self.spect_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
#     #     self.spect_plot.win.hide()


# # from __future__ import division
# # import matplotlib
# # matplotlib.use('Qt5Agg')
# # from PyQt5 import QtGui, QtCore, QtWidgets
# # import pyqtgraph as pg
# # import pyqtgraph.exporters
# # import pandas as pd
# # import numpy as np
# # from scipy.optimize import curve_fit
# # from scipy.sparse import vstack
# # from scipy.interpolate import griddata
# # from PIL.ImageQt import ImageQt
# # from multiprocessing import Pool
# # from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# # from matplotlib.figure import Figure
# # import matplotlib.pyplot as plt
# # import qimage2ndarray
# # import tempfile
# # import shutil
# # import os
# # import zipfile
# # from zipfile import ZipFile
# # import json

# # pg.setConfigOption('background', 'w')
# # pg.setConfigOption('foreground', 'k')
# # pg.mkPen('k')

# # filelist = []

# # class RamanWidget(QtWidgets.QWidget):
# #     def __init__(self, path, *args,**kwargs):
# #         super(RamanWidget, self).__init__(*args,**kwargs)
# #         self.layout = QtWidgets.QGridLayout(self)
# #         self.data = []
# #         self.spect_type = ''
# #         self.errmsg=QtWidgets.QMessageBox()

# #         filelist.append(path)
# #         if filelist[-1]!=u'':
# #             if filelist[-1][-3:]!='txt' and filelist[-1][-3:]!='csv':
# #                 self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
# #                 self.errmsg.setText('Please upload a .txt or .csv file')
# #                 self.errmsg.exec_()

# #                 del filelist[-1]
# #         else:
# #             del filelist[-1]

# #         self.f_list=filelist

        
# #         #self.viewraman = QtWidgets.QWidget()
# #         self.doFitting()
# #         self.layout.addWidget(self.doFitting,0,0)
# #         self.layout.setAlignment(QtCore.Qt.AlignTop)

# #     def make_temp_dir(self):
# #         self.dirpath = tempfile.mkdtemp()
# #         self.pathmade=True

# #     def doFitting(self):
# #         if not self.pathmade:
# #                 self.make_temp_dir()
# #         sing_i=1
# #         for flnm in filelist:
# #             self.checkFileType(flnm)
# #             if self.spect_type=='single':

# #                 self.newpath=str(self.dirpath)+'/SingleSpect'+str(sing_i)
# #                 if not os.path.exists(self.newpath):
# #                     os.makedirs(self.newpath)
# #                     sing_i+=1
# #                 shutil.copy2(flnm,self.newpath)

# #                 self.widget=self.singleSpect
# #                 self.displayWidget.setCurrentWidget(self.widget)

# #                 x=np.array(self.data.iloc[:,0])
# #                 y=np.array(self.data.iloc[:,1])

# #                 self.widget.plotSpect(x,y)
# #             else:
# #             	self.errmsg.setIcon(QtWidgets.QMessageBox.Critical)
# #             	self.errmsg.setText('Please use a single spectrum only')
# #             	self.errmsg.exec_()

# #     def checkFileType(self, flnm):
# #         if flnm[-3:]=='csv':
# #             self.data=pd.read_csv(flnm)
# #         else:
# #             self.data=pd.read_table(flnm)

# #         cols=self.data.shape[1]
# #         rows=self.data.shape[0]
# #         if cols == 1:
# #             self.data=pd.DataFrame(self.data.iloc[0:rows/2,0],self.data.iloc[rows/2:rows,0])
# #             self.spect_type='single'
# #         elif cols == 2:
# #             self.spect_type='single'
# #             if type(self.data.iloc[0,0]) is str:
# #                 self.data=self.data.iloc[1:rows,:]
# #             else:
# #                 self.data=self.data

# #     def plotSpect(self,x,y):
# #         y_norm=[]
# #         for i in y:
# #             y_norm.append((i-np.min(y))/(np.max(y)-np.min(y)))

# #         self.spect_plot=pg.plot(x,y_norm,pen='k')
# #         self.spect_plot.setFixedSize(400,500)
# #         self.spect_plot.setLabel('left','I<sub>norm</sub>[arb]')
# #         self.spect_plot.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')
# #         self.spect_plot.win.hide()

if __name__ == '__main__':
    REPO_DIR = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
    app = QtGui.QApplication([])
    raman = RamanWidget(path=os.path.join(REPO_DIR,'data','raw','spectest.csv'))
    raman.show()
    sys.exit(app.exec_())
