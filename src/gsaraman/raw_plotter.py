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

class RamanSubmitWidget(QtWidgets.QWidget):
    def __init__(self, path, specttype='single', *args,**kwargs):
        super(RamanSubmitWidget, self).__init__(*args,**kwargs)
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

    @errorCheck(show_traceback=True)
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

class RamanQueryWidget(QtWidgets.QWidget):
    def __init__(self, data_table, specttype='single', *args,**kwargs):
        super(RamanQueryWidget, self).__init__(*args,**kwargs)
        layout = QtWidgets.QGridLayout(self)
        self.spect_type = specttype

        frequency, intensity_norm = self.loadData(data_table)

        self.plot_spect = pg.PlotWidget()
        self.plot_spect.plot(frequency,intensity_norm,pen=pg.mkPen('k',width=4),brush=pg.mkBrush('b',alpha=0.3))
        self.plot_spect.setLabel('left','I<sub>norm</sub>[arb]')
        self.plot_spect.setLabel('bottom',u'\u03c9'+'[cm<sup>-1</sup>]')

        layout.addWidget(self.plot_spect,0,0)
        layout.setAlignment(QtCore.Qt.AlignTop)

    @errorCheck(show_traceback=True)
    def loadData(self, data_table):
        cols=data_table.shape[1]
        rows=data_table.shape[0]

        if cols == 1:
            self.data=pd.DataFrame(data_table.iloc[0:rows/2,0],data_table.iloc[rows/2:rows,0])
        elif cols == 2:
            if type(data_table.iloc[0,0]) is str:
                self.data=data_table.iloc[1:rows,:]
            else:
                self.data=data_table
        else:
            raise ValueError('Please use a single spectrum only')

        frequency=np.array(self.data.iloc[:,0])
        intensity=np.array(self.data.iloc[:,1])

        intensity_norm=[]
        for i in intensity:
            intensity_norm.append((i-np.min(intensity))/(np.max(intensity)-np.min(intensity)))

        return frequency, intensity_norm

if __name__ == '__main__':
    REPO_DIR = subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
    app = QtGui.QApplication([])
    raman = RamanSubmitWidget(path=os.path.join(REPO_DIR,'data','raw','spectest.csv'))
    raman.show()
    sys.exit(app.exec_())