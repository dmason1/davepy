
# -*- coding: utf-8 -*-
"""
Simple Qt
"""

import os

os.environ['QT_API'] = 'pyqt'

import sys
#from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import time
import numpy as np
from numpy import *
import traceback
from Queue import Queue
import spinmob as s
import visa


#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib as mpl
import pyqtgraph as pg

#import continuous_polling as cp
#import HF2_grab_util as hf2grabber


plt.ioff()

mpl.rc('axes', linewidth=2)
mpl.rc('font',weight='bold')




class MainWidg(QWidget,QObject):
    ready_to_plot_signal = pyqtSignal()

    def __init__(self,parent=None):
#        super(MainWidg, self).__init__()
        QWidget.__init__(self,parent)
        QObject.__init__(self)
        self.initUI()
        
    def initUI(self):
        self.simulate=False

        self.rm=visa.ResourceManager()
        self.inst = self.rm.open_resource('GPIB0::5::INSTR')

        self.setGeometry(100, 100, 750, 500)
        self.setWindowTitle('Icon')
        self.layout = QVBoxLayout()

#        self.figure = plt.figure()
#        self.canvas = FigureCanvas(self.figure)
#        self.figure.set_facecolor('white')
#        self.toolbar = NavigationToolbar(self.canvas, self)
#        self.ax = self.figure.add_subplot(111)
#        self.figure.axes[0].plot([5,6],[1,2])
#        self.figure.axes[0].set_axis_bgcolor('lightgray')

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        self.plotwidgA = pg.PlotWidget()
        penA = pg.mkPen('r',width=6)
        penB = pg.mkPen('b',width=6)
        penC = pg.mkPen('g',width=6)
        penD = pg.mkPen('c',width=6)

        self.pgplotA = self.plotwidgA.plot(pen=penA)
        self.plotwidgA.plotItem.sigXRangeChanged.connect(self.funk)
        self.plotwidgA.plotItem.showGrid(True,True)
        self.plotwidgA.disableAutoRange()

        self.plotwidgB = pg.PlotWidget()
        self.pgplotB = self.plotwidgB.plot(pen=penB)
        self.plotwidgB.plotItem.sigXRangeChanged.connect(self.funk)
        self.plotwidgB.plotItem.showGrid(True,True)
        self.plotwidgB.disableAutoRange()

        self.plotwidgC = pg.PlotWidget()
        self.pgplotC = self.plotwidgC.plot(pen=penC)
        self.plotwidgC.plotItem.sigXRangeChanged.connect(self.funk)
        self.plotwidgC.plotItem.showGrid(True,True)
        self.plotwidgC.disableAutoRange()

        self.plotwidgD = pg.PlotWidget()
        self.pgplotD = self.plotwidgD.plot(pen=penD)
        self.plotwidgD.plotItem.sigXRangeChanged.connect(self.funk)
        self.plotwidgD.plotItem.showGrid(True,True)
        self.plotwidgD.disableAutoRange()
        self.plotwidgD.setFont(QFont('Serif', 20, QFont.Bold))

        #pal = self.palette()
        #pal.setColor(self.backgroundRole(),Qt.red)
        #self.setPalette(pal)
        
        self.col=QColor(255,255,255)
        self.setStyleSheet("QWidget { background-color: %s }"%self.col.name())


#        self.layout.addWidget(self.toolbar)
#        self.layout.addWidget(self.canvas)        
#        self.layout.setAlignment(Qt.AlignHCenter)

        self.acq_button = QPushButton("Acquire!")
        self.acq_button.setStyleSheet('QPushButton {color: white; font: bold ; font-size: 16px ; background-color : green}')
        self.acq_button.setCheckable(True)
#        self.acq_button.setFixedHeight(60)
#        self.acq_button.setIconSize(QSize(64,584))

        self.save_current_button = QPushButton("Save Current")
        self.save_current_button.clicked.connect(self.save_current)        
        self.save_current_button.setStyleSheet('QPushButton {color: white; font: bold ; font-size: 16px ; background-color : gray}')

        self.show_latest_button = QPushButton("Always Show Latest")
        self.show_latest_button.setCheckable(True)
        self.show_latest_button.setStyleSheet('QPushButton {color: white; font: bold ; font-size: 16px ; background-color : gray}')

        
        self.gridlayout = QGridLayout()
        self.gridlayout.setSpacing(10) 

        self.trace_length = QSpinBox()
        self.trace_length.setValue(10)
        self.trace_length.setMaximum(1000)
        self.trace_length.setMinimum(1)
        self.trace_length.setSingleStep(10)

        self.time_delay = QDoubleSpinBox()
        self.time_delay.setValue(.1)
        self.time_delay.setMinimum(.01)
        self.time_delay.setMaximum(100)
        self.time_delay.setSingleStep(.01)

        font=QFont()
        font.setBold(True)
        font.setPointSize(20)

        self.T_A = QLabel()
        self.T_A.setStyleSheet('QLabel {color: red; font: bold; font-size: 20px}')
        self.T_A.setText("SORB:")
        self.T_B = QLabel()
        self.T_B.setStyleSheet('QLabel {color: blue; font: bold; font-size: 20px}')
        self.T_B.setText("1K POT:")
        self.T_C = QLabel()
        self.T_C.setStyleSheet('QLabel {color: green; font: bold; font-size: 20px}')
        self.T_C.setText("3HE POT:")
        self.T_D = QLabel()
        self.T_D.setStyleSheet('QLabel {color: cyan; font: bold; font-size: 20px}')
        self.T_D.setText("STAGE:")
        


#        self.gridlayout.addWidget(self.toolbar,0,0,1,4)
#        self.gridlayout.addWidget(self.canvas,1,0,1,4)
        self.gridlayout.addWidget(self.T_A,0,2,1,1)
        self.gridlayout.addWidget(self.plotwidgA,1,2,3,4)

        self.gridlayout.addWidget(self.T_B,0,6,1,1)
        self.gridlayout.addWidget(self.plotwidgB,1,6,3,4)

        self.gridlayout.addWidget(self.T_C,6,2,1,1)
        self.gridlayout.addWidget(self.plotwidgC,7,2,5,4)

        self.gridlayout.addWidget(self.T_D,6,6,1,1)
        self.gridlayout.addWidget(self.plotwidgD,7,6,5,4)
        
        self.gridlayout.addWidget(self.acq_button,1,0,1,2)
        self.gridlayout.addWidget(self.save_current_button,2,0,1,2)
        self.gridlayout.addWidget(self.show_latest_button,3,0,1,1)
        self.gridlayout.addWidget(self.trace_length,3,1,1,1)
        self.time_delay_label = QLabel("Time between samples: ")
        self.time_delay_label.setStyleSheet('QLabel {color:gray ; font: bold ; font-size: 16px}')
        self.gridlayout.addWidget(self.time_delay_label,4,0,1,1)
        self.gridlayout.addWidget(self.time_delay,4,1,1,1)
#        self.gridlayout.addWidget(self.show_tl_1,7,2,1,1)


#        self.trace_length.valueChanged.connect(self.trace_length_changed)

        #self.hf2_grabber = hf2grabber.grabber()
      
        self.timestamps=array([])
        self.valuesA = array([])
        self.valuesB = array([])
        self.valuesC = array([])
        self.valuesD = array([])
        
        
        self.max_stored_data = 1000000        
                        
        self.setLayout(self.gridlayout)
    
        pal = self.palette()
        pal.setColor(self.backgroundRole(),Qt.white)
        self.setPalette(pal)

        self.q_data = Queue()
        #self.q_plot = Queue()

        self.ready_to_plot_signal.connect(self.plot_latest)
 
        self.acq = acq_thread(self)
        self.acq_button.clicked.connect(self.acq.update_acq_button)
        self.acq.start()


        #self.proc = proc_thread(self)
        #self.proc.start()


        #self.accumulated_data = s.data.databox()
        self.accumulated_data = array([])


        self.show()

    def funk(self):
        print "View range changed!"
        self.current_width = self.plotwidgA.plotItem.vb.viewRange()[0][1]-self.plotwidgA.plotItem.vb.viewRange()[0][0]



    def save_current(self):
        self.path_save_current = QFileDialog.getSaveFileName(self,"Save the current processed data")
#        try:
#            self.current_data.save_file(self.path_save_current)
#        except:
#            traceback.print_exc()
            
    def plot_latest(self):
        print "Success!"
        try:
            newdata = self.q_data.get(False)
#            print newdata[0]
#            print newdata[1]
            if len(self.timestamps) < self.max_stored_data:
                self.timestamps = append(self.timestamps,newdata[0])
                self.valuesA = append(self.valuesA,newdata[1])
                self.T_A.setText("SORB: %.4f K"%newdata[1])
                self.valuesB = append(self.valuesB,newdata[2])
                self.T_B.setText("1K POT: %.4f K"%newdata[2])
                self.valuesC = append(self.valuesC,newdata[3])
                self.T_C.setText("3HE POT: %.4f K"%newdata[3])
                self.valuesD = append(self.valuesD,newdata[4])
                self.T_D.setText("STAGE: %.4f K"%newdata[4])

            else:
                print "Exceeded maximum data storage - please save data and reset!"


            #print self.timestamps
            #print self.valuesA

            self.pgplotA.setData(self.timestamps-self.timestamps[0],self.valuesA)
            self.pgplotB.setData(self.timestamps-self.timestamps[0],self.valuesB)
            self.pgplotC.setData(self.timestamps-self.timestamps[0],self.valuesC)
            self.pgplotD.setData(self.timestamps-self.timestamps[0],self.valuesD)

            if self.show_latest_button.isChecked():
                t0=time.time()
                self.plotwidgA.setXRange(self.timestamps[-self.trace_length.value()]-self.timestamps[0],self.timestamps[-1]-self.timestamps[0])
                self.plotwidgB.setXRange(self.timestamps[-self.trace_length.value()]-self.timestamps[0],self.timestamps[-1]-self.timestamps[0])
                self.plotwidgC.setXRange(self.timestamps[-self.trace_length.value()]-self.timestamps[0],self.timestamps[-1]-self.timestamps[0])
                self.plotwidgD.setXRange(self.timestamps[-self.trace_length.value()]-self.timestamps[0],self.timestamps[-1]-self.timestamps[0])

                min_A = min(self.valuesA[-self.trace_length.value():-1])
                max_A= max(self.valuesA[-self.trace_length.value():-1])
                min_B = min(self.valuesB[-self.trace_length.value():-1])
                max_B= max(self.valuesB[-self.trace_length.value():-1])
                min_C = min(self.valuesC[-self.trace_length.value():-1])
                max_C= max(self.valuesC[-self.trace_length.value():-1])
                min_D = min(self.valuesD[-self.trace_length.value():-1])
                max_D= max(self.valuesD[-self.trace_length.value():-1])

                
                self.plotwidgA.setYRange(.9999*min_A,1.0001*max_A)
                self.plotwidgB.setYRange(.9999*min_B,1.0001*max_B)
                self.plotwidgC.setYRange(.9999*min_C,1.0001*max_C)
                self.plotwidgD.setYRange(.9999*min_D,1.0001*max_D)
                
                print "Took %.3f seconds to plot"%(time.time()-t0)


#            self.ax.cla()
#            self.ax.plot(self.timestamps-self.timestamps[0],self.values)
#            self.ax.set_xlim(0,self.timestamps[-1]-self.timestamps[0])
#            self.ax.set_ylim(min(self.values),max(self.values))
#            self.figure.axes[0].lines[0].set_xdata(self.timestamps)
            #self.figure.axes[0].lines[0].set_ydata(self.values)
#            self.canvas.draw()

        except:
            traceback.print_exc()



class acq_thread(QThread):
    def __init__(self,main_widg):
        QThread.__init__(self)
        self.acq_button_checked = False
        self.main_widg=main_widg
    def run(self):
        while True:
            try:
                t0=time.time()
                if self.acq_button_checked==True:
                    print "Acquiring data..."
                    
                    if self.main_widg.simulate==True:
                        time.sleep(.2)
                        data=[time.time(),random.random()+5*sin(2*time.time())]
                        self.main_widg.q_data.put(data)
                        self.main_widg.ready_to_plot_signal.emit()
#                print "\n Total Acquisition Time: %.3f seconds"%(time.time()-t0)
                    else:
                        print "Acquiring real data..."

                        data = [time.time(),
                                float(self.main_widg.inst.query('KRDG? A')),
                                float(self.main_widg.inst.query('KRDG? B')),
                                float(self.main_widg.inst.query('KRDG? C')),
                                float(self.main_widg.inst.query('KRDG? D'))]
                        self.main_widg.q_data.put(data)
                        self.main_widg.ready_to_plot_signal.emit()
                        print "Acquisition took %.3f seconds"%(time.time()-t0)
                        time.sleep(.2)
                        print data
                    
            except:
                traceback.print_exc()
                continue
        return
        
    def update_acq_button(self):
        self.acq_button_checked= not self.acq_button_checked



#
#
#
#
#
#
#class proc_thread(QThread):
#
#    def __init__(self,main_widg):
#        QThread.__init__(self)
#        self.main_widg=main_widg
#    def run(self):
#        while True:
#            try: 
#                self.data = self.main_widg.q_data.get(False)
#                try:
#                    self.main_widg.current_data.clear_columns()
#
#                    for col in self.data.ckeys:
#                        self.main_widg.current_data.insert_column(self.data[col],col)
#
#                    for header in self.data.headers:
#                        self.main_widg.current_data.insert_header(header,self.data.h(header))
#
#                    self.main_widg.q_plot.put(self.main_widg.current_data)
#                    self.main_widg.ready_to_plot_signal.emit()
#                except:
#                    traceback.print_exc()
#            except:
#                continue

        
def main():
    app = QApplication(sys.argv)

    ex = MainWidg()
   
    sys.exit(app.exec_())


if __name__ == '__main__':
#    main()    
    app = QApplication(sys.argv)

    ex = MainWidg()
   
    sys.exit(app.exec_())