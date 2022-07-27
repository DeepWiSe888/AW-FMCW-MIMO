import sys
from pyqtgraph.Qt import QtGui, QtCore,QtWidgets
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import matplotlib.pyplot as plt


class PlotData():
    def __init__(self):
        # Set graphical window, its title and size
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.resize(800,600)
        self.win.setWindowTitle('plot radar data')
        self.win.setBackground("w")

        pg.setConfigOptions(antialias=True)
        self.colorMap = pg.colormap.get("CET-R4")
        self.curves = []
        
        #definde different style
        self.curves = self._plot_style_1()
        self._start()
        
    def _plot_style_1(self):
        curves = []
        curve1 = self._add_item(title = 'range-time',
                                           left_label = 'time',
                                           bottom_label = 'range',
                                           left_ticks = [],
                                           bottom_ticks = [],image_item = True)
        curve2 = self._add_item(title = 'range-doppler',
                                           left_label = 'doppler',
                                           bottom_label = 'range',
                                           left_ticks = [],
                                           bottom_ticks = [],image_item = True)
        self.win.nextRow()
        curve3 = self._add_item(title = 'range-azimuth',
                                           left_label = 'rad',
                                           bottom_label = 'range',
                                           left_ticks = [],
                                           bottom_ticks = [],image_item = True)
        
        curve4 = self._add_item(title = 'range-elevation',
                                           left_label = 'rad',
                                           bottom_label = 'range',
                                           left_ticks = [],
                                           bottom_ticks = [],image_item = True)
        curves.append(curve1)
        curves.append(curve2)
        curves.append(curve3)
        curves.append(curve4)
        return curves
        
        
    def _add_item(self,title,left_label,bottom_label,left_ticks,bottom_ticks,image_item = False):
        curve = None
        p = self.win.addPlot(title=title)
        if image_item:
            curve = pg.ImageItem()
            p.addItem(curve)
            bar = pg.ColorBarItem(values=(0,1), colorMap=self.colorMap) 
            bar.setImageItem(curve) 
        else:
            curve = p.plot(pen='b')
        p.setLabels(left=left_label,bottom=bottom_label)
        ax = p.getAxis('left')
        ax.setTicks(left_ticks)
        ax = p.getAxis('bottom')
        ax.setTicks(bottom_ticks)
        return curve
     
    def _start(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1)
            
    def update(self,datas):
        assert len(self.curves) == len(datas),'The number of curves is equal to the number datas'
        for i in range(len(datas)):
            if hasattr(self.curves[i],'setImage'):
                self.curves[i].setImage(datas[i].T)
            elif hasattr(self.curves[i],'setData'):
                self.curves[i].setData(datas[i].T)
            else:
                pass
        #update plot immediate
        QtGui.QApplication.processEvents()