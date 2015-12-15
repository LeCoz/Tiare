from PySide import QtGui, QtCore
from pyqtgraph import PlotWidget, FillBetweenItem, mkPen
from analysers import load_sound, energy, cut
from datetime import datetime


class Tiare(QtGui.QMainWindow):
    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.statusBar().showMessage('Pret')
        self.th = 0
        self.widget = QtGui.QWidget(self)
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Quitter', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip("Ferme l'application")
        exitAction.triggered.connect(self.close)

        openAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Charger', self)
        openAction.setShortcut('Ctrl+L')
        openAction.setStatusTip("Charge un fichier wav")
        openAction.triggered.connect(self.load)

        self.saveAction = QtGui.QAction(QtGui.QIcon('save.png'), '&Exporter', self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip("Exporter en CSV")
        self.saveAction.triggered.connect(self.export)
        self.saveAction.setEnabled(False)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(exitAction)

        self.th_slider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.th_slider.setValue(self.th)
        self.th_slider.valueChanged[int].connect(self.change_threshold)

        self.min_len = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.min_len.setValue(10)
        self.min_len.setMinimum(1)
        self.min_len.setMaximum(100)
        self.min_len.valueChanged[int].connect(self.change_min_len)

        self.min_len_sil = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.min_len_sil.setValue(10)
        self.min_len_sil.setMinimum(1)
        self.min_len_sil.setMaximum(100)
        self.min_len_sil.valueChanged[int].connect(self.change_min_len)


        # Make sizer and embed stuff
        self.sizer = QtGui.QVBoxLayout(self.widget)
        self.fig_signal = PlotWidget(self.widget, background="w")
        self.fig_signal.setLimits(xMin=0, yMin=-1, yMax=1, minXRange=1, maxXRange=30, minYRange=2, maxYRange=2)
        self.fig_energy = PlotWidget(self.widget, background="w")
        self.fig_energy.setXLink(self.fig_signal)
        self.fig_segments = PlotWidget(self.widget, background="w")
        self.fig_segments.setXLink(self.fig_signal)
        self.fig_segments.hideAxis('bottom')
        self.fig_segments.hideAxis('left')
        self.fig_segments.setLimits(yMin=-1, yMax=1, minYRange=2, maxYRange=2)

        self.sizer.addWidget(self.fig_signal, 5)
        self.sizer.addWidget(self.fig_energy, 5)
        self.sizer.addWidget(self.fig_segments, 3)
        self.sizer.addWidget(QtGui.QLabel('Seuil de segmentation'), 0)
        self.sizer.addWidget(self.th_slider, 0)
        self.min_seg_label = QtGui.QLabel('Longeur minimal de segment (%.3f s)' % (float(self.min_len.value())/100))
        self.sizer.addWidget(self.min_seg_label, 0)
        self.sizer.addWidget(self.min_len, 0)

        self.min_sil_label = QtGui.QLabel('Longeur minimal de silence (%.3f s)' % (float(self.min_len_sil.value())/100))
        self.sizer.addWidget(self.min_sil_label, 0)
        self.sizer.addWidget(self.min_len_sil, 0)

        # Apply sizers
        self.setCentralWidget(self.widget)

        # Finish
        self.resize(560, 420)
        self.setWindowTitle('Tiare')
        self.energy_tl, self.energy = [], []
        self.thline = None
        self.seg_up = None
        self.seg_down = None
        self.fig_energy_plot = None
        self.segments = []
        self.samples = []
        self.sr = 0
        self.filepath = None
        self.widget.hide()
        self.show()

    def change_threshold(self, value):
        value = float(value)/100
        if self.thline is not None :
            self.thline.setData([self.energy_tl[0], self.energy_tl[-1]], [value]*2)
            self.segments = map(lambda (x, y): (self.energy_tl[x],self.energy_tl[y]),
                                cut(self.energy, value, self.min_len.value(), self.min_len_sil.value()))
            x = [v for start, stop in self.segments for v in [start, start, stop, stop]]
            y = [v for _ in self.segments for v in [-0.85, 0.85, 0.85, -0.85]]
            self.seg_up.setData(x, y)
            self.seg_down.setData([self.energy_tl[0], self.energy_tl[-1]], [-0.85, -0.85])

    def change_min_len(self, value=0):
        self.min_seg_label.setText("Longeur minimale d'un segment (%.3f s)" % (float(self.min_len.value())/100))
        self.min_sil_label.setText("Longeur minimale d'un silence (%.3f s)" % (float(self.min_len_sil.value())/100))
        self.change_threshold(self.th_slider.value())

    def compute_energy(self, value=None):
        self.energy_tl, self.energy = energy(self.samples, self.sr)
        if self.fig_energy_plot is not None:
            self.fig_energy_plot.setData(self.energy_tl, self.energy)
            self.change_min_len()

    def export(self):
        fpath = QtGui.QFileDialog.getSaveFileName(self, "Sauvegader en CSV", self.filepath+".csv")
        if fpath:
            with open(fpath[0], "w") as f:

                for start, stop in self.segments:
                    f.write("Segments\t%s\t%s\n" % (datetime(day=1, month=1, year=1901, second=int(start),
                                                             microsecond=int(10e5*(start % 1)))
                                                    .strftime("%H:%M:%S.%f"),
                                                    datetime(day=1, month=1, year=1901, second=int(stop),
                                                             microsecond=int(10e5*(stop % 1)))
                                                    .strftime("%H:%M:%S.%f")))

    def load(self):
        fpath, _ = QtGui.QFileDialog.getOpenFileName(self, 'Choisir un fichier', '~/', filter="*.wav")
        self.widget.show()
        if fpath:
            self.filepath = fpath
            self.saveAction.setEnabled(True)

            self.samples, self.sr = load_sound(fpath)
            m = max(map(abs, self.samples))
            timeline = [float(t)/self.sr for t in range(len(self.samples))]
            self.fig_signal.setLimits(xMax=timeline[-1])

            self.compute_energy()

            self.fig_signal.getPlotItem().plot(timeline, map(lambda x: x/m, self.samples))
            self.fig_energy_plot = self.fig_energy.getPlotItem().plot(self.energy_tl, self.energy)
            self.thline = self.fig_energy.getPlotItem().plot([self.energy_tl[0], self.energy_tl[-1]],
                                                             [float(self.th_slider.value())/100]*2,
                                               pen=({'color': "k", "width": 1.5}))
            self.seg_up = self.fig_segments.getPlotItem().plot([self.energy_tl[0], self.energy_tl[-1]],
                                                               [-0.85, -0.85])

            self.seg_down = self.fig_segments.getPlotItem().plot([self.energy_tl[0], self.energy_tl[-1]],
                                                                 [-0.85, -0.85])
            self.segments = FillBetweenItem(self.seg_up, self.seg_down, 0.7)
            self.fig_segments.addItem(self.segments)

