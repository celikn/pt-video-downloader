
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .ptvideobin import PtVideoBin
import urllib.request
from functools import partial
import time
import sys
import os
import subprocess
import signal

downlist = {}

class PtVideoGui(QWidget):

    def __init__(self):
        super().__init__()
        #self.piccount = piccount
        #self.initUI()
        #self.setAttribute(Qt.WA_DeleteOnClose)

    def getImage(self, url):
        try:
            data = urllib.request.urlopen(url).read()
        except Exception as ex:
            main_folder = str(os.environ['HOME']) + "/pt_video_downloader"
            data = open(main_folder + '/app_data/images/no_thumbnail.jpg', 'rb+').read()
        finally:
            image = QImage()
            image.loadFromData(data)
            return image


    def initUI(self):
        self.table = QTableWidget()
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()
        self.mainUI()
        slay = self.searchUI()
        self.mainlay.addLayout(slay)
        self.mainlay.addWidget(self.table)
        self.btnindir = []
        self.ind = 0


    def mainUI(self):
        self.mainlay = QVBoxLayout()
        self.setLayout(self.mainlay)
        self.move(300, 200)
        self.setFixedSize(800,640)
        self.setWindowTitle('Search and Add New Video')
        self.show()
        self.acceptDrops()
        self.actions()

class PtVideoLinkGui(QWidget):
    """For single video link"""
    def __init__(self, parent=None):
        super(PtVideoLinkGui, self).__init__()
        fbox = QFormLayout()
        self.txt_link = QLineEdit(self)
        self.txt_link.setFixedSize(420,25)
        self.btn_link = QPushButton("Add")
        self.btn_link.setFixedSize(50,25)
        self.btn_link.setCursor(Qt.PointingHandCursor)
        fbox.addRow(self.txt_link, self.btn_link)
        self.setLayout(fbox)
        self.move(300, 200)
        self.setFixedSize(500,50)
        self.setWindowTitle('Add New Video by a Link')
        self.show()
        self.acceptDrops()
        self.actions()

class PtVideoLinksGui(QWidget):
    """For single video link"""
    def __init__(self, parent=None):
        super(PtVideoLinksGui, self).__init__()
        vbox = QVBoxLayout()
        self.txt_links = QTextEdit(self)
        self.txt_links.setFixedHeight(600)
        self.btn_links = QPushButton("Add Links")
        self.btn_links.setFixedHeight(25)
        self.btn_links.setCursor(Qt.PointingHandCursor)
        vbox.addWidget(self.txt_links)
        vbox.addWidget(self.btn_links)
        self.setLayout(vbox)
        self.move(300, 100)
        self.setFixedSize(520,630)
        self.setWindowTitle('Add New Video by Links')
        self.show()
        self.acceptDrops()
        self.actions()

class SettingsGui(QWidget):
    """Settings Gui"""
    def __init__(self, parent=None):
        super(SettingsGui, self).__init__()
        self._bin = PtVideoBin()
        self._confs = self._bin.get_configurations()
        hbox = QHBoxLayout()
        self.treebox = QTreeWidget(self)
        self.treebox.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding))
        self._addItems(self.treebox.invisibleRootItem())
        self.treebox.itemClicked.connect(self._handleChanged)
        self.panel = QWidget(self)
        self.panel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self.panelvbox = QVBoxLayout(self)
        self.panel.setLayout(self.panelvbox)
        hbox.addWidget(self.treebox)
        hbox.addWidget(self.panel)
        self.setLayout(hbox)
        self.move(300, 200)
        self.setFixedSize(800,650)
        self.setWindowTitle('Preferences')
        self.show()
        self.acceptDrops()
        self.actions()

    def _loadConfigs(self):
        for cf in self._confs:
            pass

    def _addItems(self, parent):
        column = 0
        system_items = self._addParent(parent, column, 'System', 'System Configurations')
        for cf in self._confs:
            self._addChild(system_items, column, cf, self._confs[cf])

    def _addParent(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        item.setExpanded (True)
        return item

    def _addChild(self, parent, column, title, data):
        item = QTreeWidgetItem(parent, [title])
        item.setData(column, Qt.UserRole, data)
        #item.setCheckState (column, Qt.Unchecked)
        return item

    def _clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)

            if isinstance(item, QWidgetItem):
                item.widget().close()
            elif isinstance(item, QSpacerItem):
                pass

            else:
                self._clearLayout(item.layout())
            layout.removeItem(item)

    def _showDialog(self, param):
        fname = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if fname.strip() != '':
            param.setText(fname)

    def _saveChanges(self, title):
        new_data = self._confs[title]
        for i in self._save_items:
            if 'txt_path' in dict(self._save_items[i]).keys():
                new_data[i]['value'] = self._save_items[i]['txt_path'].text()
                if new_data[i]['value'][(len(new_data[i]['value'])-1):] != '/':
                    new_data[i]['value'] += '/'
            if 'chk_select' in dict(self._save_items[i]).keys():
                new_data[i]['value'] = self._save_items[i]['chk_select'].isChecked()
            if 'spn_box' in dict(self._save_items[i]).keys():
                new_data[i]['value'] = self._save_items[i]['spn_box'].value()
        self._confs[title] = new_data
        self._bin.set_configurations(self._confs)
        self.close()

    def _handleChanged(self, item, column):
        try:
            title = item.text(column)
            data = self._confs[title]
            syc = 0
            self._clearLayout(self.panelvbox)
            btn_save = QPushButton("Save Changes")
            self._save_items = {}
            for i in data:
                gbox = QGridLayout()
                vtitle = data[i]['title']
                vvalue = data[i]['value']
                vtype = data[i]['type']
                self._save_items[i] = {}
                if vtype == "file":
                    gbox.addWidget(QLabel(vtitle), syc, 0, 1, 1)
                    self._save_items[i]['txt_path'] = QLineEdit(str(data[i]['value']), self.panel)
                    gbox.addWidget(self._save_items[i]['txt_path'], syc, 1, 1, 1)
                    btn_selectpath = QPushButton("...")
                    btn_selectpath.setCursor(Qt.PointingHandCursor)
                    btn_selectpath.clicked.connect(partial(self._showDialog, param=self._save_items[i]['txt_path']))
                    gbox.addWidget(btn_selectpath, syc, 2, 1, 1)
                    self.panelvbox.addLayout(gbox)
                if vtype == "bool":
                    self._save_items[i]['chk_select'] = QCheckBox(vtitle, self.panel)
                    self._save_items[i]['chk_select'].setChecked(vvalue)
                    self._save_items[i]['chk_select'].setCursor(Qt.PointingHandCursor)
                    gbox.addWidget(self._save_items[i]['chk_select'], syc, 0, 1, 1)
                    self.panelvbox.addLayout(gbox)
                if vtype == "int":
                    gbox.addWidget(QLabel(vtitle), syc, 0, 1, 1)
                    self._save_items[i]['spn_box'] = QSpinBox(self.panel)
                    self._save_items[i]['spn_box'].setCursor(Qt.PointingHandCursor)
                    self._save_items[i]['spn_box'].setValue(vvalue)
                    gbox.addWidget(self._save_items[i]['spn_box'], syc, 1, 1, 1)
                    self.panelvbox.addLayout(gbox)
                syc += 1
            btn_save.clicked.connect(partial(self._saveChanges, title=title))
            btn_save.setCursor(Qt.PointingHandCursor)
            self.panelvbox.addWidget(btn_save)
        except Exception as ex:
            pass

class SearchThread(QThread):
    search_load = pyqtSignal(object)
    def __init__(self, param):
        QThread.__init__(self)
        self._param = param

    def _getImage(self, url):
        try:
            data = urllib.request.urlopen(url).read()
        except Exception as ex:
            main_folder = str(os.environ['HOME']) + "/pt_video_downloader"
            data = open(main_folder + '/app_data/images/no_thumbnail.jpg', 'rb+').read()
        finally:
            image = QImage()
            image.loadFromData(data)
            return image

    def _procTask(self):
        title = self._param['title']
        image = self._getImage(self._param['thumbnail'])
        self.search_load.emit((image, title, self._param))

    def run(self):
        self._procTask()

class DownloadThread(QThread):

    data_downloaded = pyqtSignal(object)
    data_end = pyqtSignal(object)

    def __init__(self, videoid, downformat, conf):
        QThread.__init__(self)
        self.videoid = videoid
        self._configs = conf
        self._downformat = downformat

    def DownloadUrl(self, url):
        process = subprocess.Popen(["youtube-dl", "--no-warnings", "-i", "-f",
        self._downformat, "-o", self._configs['download']['down_path']['value'] + "%(title)s.%(ext)s", url],
        stdout = subprocess.PIPE, universal_newlines=True)
        status = True
        while process.poll() is None:
            try:
                if downlist[self.videoid]['process']:
                    if not status:
                        os.kill(process.pid, signal.SIGCONT)
                    result = process.stdout.readline()
                    if "%" in result:
                        self.data_downloaded.emit(url.rsplit('=')[1].strip() + " " + result)
                    sys.stdout.flush()
                else:
                    status = False
                    os.kill(process.pid, signal.SIGSTOP)
                    while True:
                        if downlist[self.videoid]['process']:
                            break
                        time.sleep(0.5)

            except Exception as ex:
                pass

    def run(self):
        vbin = PtVideoBin()
        url = "https://www.youtube.com/watch?v=%s" % (self.videoid)
        self.DownloadUrl(url)
        self.data_end.emit(self.videoid)

class MainGui(QWidget):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        vbox = QVBoxLayout()
        self.lbl = QLabel("PT Video Downloader", self)
        self.lbl.setFont(QFont("Noto Sans [monotype]", 26, QFont.Bold))
        vbox.addWidget(self.lbl)

        self.maintable = QTableWidget(self)
        self.maintable.horizontalHeader().hide()
        vbox.addWidget(self.maintable)
        self.setLayout(vbox)

class PtVideoGuiMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self._bin = PtVideoBin()
        #self._bin.get_youtube_video_formats("https://www.youtube.com/watch?v=f9SPSTxqhF0")
        self._central_widget = QStackedWidget()
        self.setCentralWidget(self._central_widget)
        self.main_widget = MainGui(self)
        self._central_widget.addWidget(self.main_widget)
        self.initUI()
        self._configs = self._bin.get_configurations()

    def _showDialog(self):
        fname = QFileDialog.getOpenFileName(self, 'Open File', '', 'Text (*.txt)',
                   None, QFileDialog.DontUseNativeDialog)
        if fname[0] == '':
            return
        f = open(fname[0], 'r')
        with f:
            data = f.read()
            for ln in data.split('\n'):
                dt = self._bin.get_youtube_video_info(ln.strip())
                self._addVideotoTable(dt)

    def _openPreferences(self):
        self._settings = SettingsGui()
        self._settings.show()

    def initUI(self):

        self.statusBar().showMessage('Ready')
        main_folder = str(os.environ['HOME']) + "/pt_video_downloader"
        byLinkAction = QAction(QIcon(main_folder + '/app_data/images/link.png'), '&byLink', self)
        byLinkAction.setShortcut('Ctrl+A')
        byLinkAction.setStatusTip('Add Video by Link')
        byLinkAction.triggered.connect(self._openNewLinkWindow)

        byLinksAction = QAction(QIcon(main_folder + '/app_data/images/links.png'), '&byLinks', self)
        byLinksAction.setShortcut('Ctrl+M')
        byLinksAction.setStatusTip('Add Video by Links')
        byLinksAction.triggered.connect(self._openNewLinksWindow)

        byFileAction = QAction(QIcon(main_folder + '/app_data/images/file.png'), '&byFile', self)
        byFileAction.setShortcut('Ctrl+N')
        byFileAction.setStatusTip('Add Video by File')
        byFileAction.triggered.connect(self._showDialog)

        bySearchAction = QAction(QIcon(main_folder + '/app_data/images/search.png'), '&bySearch', self)
        bySearchAction.setShortcut('Ctrl+N')
        bySearchAction.setStatusTip('Add Video by Searching')
        bySearchAction.triggered.connect(self._openNewWindow)

        settingsAction = QAction(QIcon(main_folder + '/app_data/images/settings.png'), '&Preferences', self)
        settingsAction.setShortcut('Ctrl+P')
        settingsAction.setStatusTip('Preferences')
        settingsAction.triggered.connect(self._openPreferences)

        exitAction = QAction(QIcon(main_folder + '/app_data/images/exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        self.statusBar()
        self.qproglist = {}

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(byLinkAction)
        fileMenu.addAction(byLinksAction)
        fileMenu.addAction(byFileAction)
        fileMenu.addAction(bySearchAction)
        fileMenu.addAction(settingsAction)
        fileMenu.addAction(exitAction)

        self.threads = []


        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle('PT Video Downloader')
        self.showMaximized()

    def _getImage(self, url):
        while True:
            try:
                data = urllib.request.urlopen(url).read()
                image = QImage()
                image.loadFromData(data)
                return image
            except Exception as e:
                time.sleep(1)
                continue

    def dataLoad(self, text):
        try:

            params = text.strip().split(' ')
            if params[3] != '':
                params.insert(3, '')
            val = float(params[4].strip('%'))
            size = params[6]
            dspeed = params[8]
            eta = params[10]
            dg = {'val': val, 'size': size, 'dspeed': dspeed, 'eta': eta}
            self.qproglist[params[0]]['status'].setText("Downloading")
            self.qproglist[params[0]]['progress'].setValue(val)
            self.qproglist[params[0]]['size'].setText(size)
            self.qproglist[params[0]]['speed'].setText(dspeed)
            self.qproglist[params[0]]['eta'].setText(eta)
            self.main_widget.maintable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            self.main_widget.maintable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        except Exception as e:
            pass

    def dataEnd(self, text):
        self.qproglist[text]['status'].setText("Complete")
        self.qproglist[text]['progress'].setValue(100)
        if self._configs['download']['down_after_remove']['value']:
            self.main_widget.maintable.removeRow(self.qproglist[text]['row'])
        else:
            self.qproglist[text]['stop'].setEnabled(False)


    def _openNewWindow(self):
        self.nwidget = PtVideoGui()
        self.nwidget.table = QTableWidget()
        self.nwidget.table.horizontalHeader().hide()
        self.nwidget.table.verticalHeader().hide()
        self.nwidget.mainUI()
        slay = self.searchUI()
        self.nwidget.mainlay.addLayout(slay)
        self.nwidget.mainlay.addWidget(self.nwidget.table)

    def _openNewLinkWindow(self):
        self.lnwidget = PtVideoLinkGui()
        self.lnwidget.btn_link.clicked.connect(self.btnAddLinkClicked)

    def _openNewLinksWindow(self):
        self.lnswidget = PtVideoLinksGui()
        self.lnswidget.btn_links.clicked.connect(self.btnAddLinksClicked)

    def getTable(self, query):
        #res = self._bin.get_youtube_videos(str(query).replace(' ', '+'))
        res = self._bin.search_youtube_videos(str(query))
        maxc = 5
        rows = 0
        syc = 0
        self.nwidget.table.setRowCount(len(res))
        self.nwidget.table.setColumnCount(4)
        self.nwidget.mapper = QSignalMapper(self.nwidget)
        self.nwidget.btnindir = []
        for i in res:
            #if syc == maxc: break
            i['row'] = rows
            srcth = SearchThread(i.copy())
            srcth.search_load.connect(self._loadSearchTable)
            srcth.start()
            rows += 1
            syc += 1
            time.sleep(0.1)
        self.nwidget.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.nwidget.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.nwidget.table.setShowGrid(False)

    def _loadSearchTable(self, isrc):
        title = QLabel(isrc[1])
        title.setFixedWidth(400)
        title.setWordWrap(True);
        lbl = QLabel(self.nwidget)
        pixmap = QPixmap(isrc[0])
        self.nwidget.btnindir.append(QPushButton("Add"))
        self.nwidget.btnindir[-1].setCursor(Qt.PointingHandCursor)
        self.nwidget.btnindir[-1].clicked.connect(partial(self.btnAddClicked, param=isrc[2]))
        btnsil = QPushButton("Delete")
        btnsil.setCursor(Qt.PointingHandCursor)
        lbl.setPixmap(pixmap)
        self.nwidget.table.setCellWidget(isrc[2]['row'], 0, lbl)
        self.nwidget.table.setCellWidget(isrc[2]['row'], 1, title)
        self.nwidget.table.setCellWidget(isrc[2]['row'], 2, self.nwidget.btnindir[-1])
        self.nwidget.table.setCellWidget(isrc[2]['row'], 3, btnsil)

    def btnSearchClicked(self):
        #self.mainlay.addLayout(self._resultUI(self.txt_arama.text()))
        self.getTable(self.nwidget.txt_arama.text())

    def _addVideotoTable(self, param, widget=None):
        downlist[param['id']] = param.copy()
        lblimg = QLabel(self)
        pixmap = QPixmap(self._getImage(param['thumbnail']))
        lblimg.setPixmap(pixmap)
        title = QLabel(param['title'], self)
        title.setFixedWidth(400)
        title.setWordWrap(True)

        rows = self.main_widget.maintable.rowCount()
        self.qproglist[param['id']] = {
            'image': lblimg,
            'title': title,
            'format': QComboBox(self),
            'progress': QProgressBar(self),
            'size': QLabel(self),
            'speed': QLabel(self),
            'eta': QLabel(self),
            'sil': QPushButton("Remove"),
            'download': QPushButton("Download"),
            'stop': None,
            'row': rows,
            'status': QLabel("Waiting")
        }
        self.main_widget.maintable.setRowCount(rows + 1)
        self.main_widget.maintable.setColumnCount(10)

        self.main_widget.maintable.setCellWidget(rows, 0, self.qproglist[param['id']]['image'])
        self.main_widget.maintable.setCellWidget(rows, 1, self.qproglist[param['id']]['title'])
        self.main_widget.maintable.setCellWidget(rows, 2, self.qproglist[param['id']]['format'])
        self.main_widget.maintable.setCellWidget(rows, 3, self.qproglist[param['id']]['progress'])
        self.main_widget.maintable.setCellWidget(rows, 4, self.qproglist[param['id']]['size'])
        self.main_widget.maintable.setCellWidget(rows, 5, self.qproglist[param['id']]['speed'])
        self.main_widget.maintable.setCellWidget(rows, 6, self.qproglist[param['id']]['eta'])
        self.main_widget.maintable.setCellWidget(rows, 7, self.qproglist[param['id']]['download'])
        self.main_widget.maintable.setCellWidget(rows, 8, self.qproglist[param['id']]['sil'])
        self.main_widget.maintable.setCellWidget(rows, 9, self.qproglist[param['id']]['status'])
        self.main_widget.maintable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.main_widget.maintable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.qproglist[param['id']]['download'].setCursor(Qt.PointingHandCursor)
        self.qproglist[param['id']]['sil'].setCursor(Qt.PointingHandCursor)
        self.qproglist[param['id']]['format'].setCursor(Qt.PointingHandCursor)
        formats = self._bin.get_youtube_video_formats(param['url'])
        for fm in formats:
            self.qproglist[param['id']]['format'].addItem(fm[0], fm[1])

        self.qproglist[param['id']]['sil'].clicked.connect(partial(self._removebyId, param=param['id']))
        self.qproglist[param['id']]['download'].clicked.connect(partial(self._downloadbyId, param=param['id']))
        if widget is not None:
            widget.close()

    def _removebyId(self, param):
        self.main_widget.maintable.removeRow(self.qproglist[param]['row'])
        downlist[param]['process'] = False

    def _stopbyId(self, param):
        downlist[param]['process'] = False
        self.qproglist[param]['download'] = QPushButton("Continue")
        self.main_widget.maintable.setCellWidget(self.qproglist[param]['row'], 7, self.qproglist[param]['download'])
        self.qproglist[param]['download'].setCursor(Qt.PointingHandCursor)
        self.qproglist[param]['download'].clicked.connect(partial(self._continuebyId, param=param))

    def _continuebyId(self, param):
        downlist[param]['process'] = True
        self.qproglist[param]['stop'] = QPushButton("Pause")
        self.main_widget.maintable.setCellWidget(self.qproglist[param]['row'], 7, self.qproglist[param]['stop'])
        self.qproglist[param]['stop'].setCursor(Qt.PointingHandCursor)
        self.qproglist[param]['stop'].clicked.connect(partial(self._stopbyId, param=param))

    def _downloadbyId(self, param):
        self.qproglist[param]['stop'] = QPushButton("Pause")
        self.main_widget.maintable.setCellWidget(self.qproglist[param]['row'], 7, self.qproglist[param]['stop'])
        self.qproglist[param]['stop'].setCursor(Qt.PointingHandCursor)
        self.qproglist[param]['stop'].clicked.connect(partial(self._stopbyId, param=param))
        downformat = self.qproglist[param]['format'].currentData()
        self.qproglist[param]['format'].setEnabled(False)
        downlist[param]['process'] = True
        downloadthread = DownloadThread(param, downformat, self._configs)
        downloadthread.data_downloaded.connect(self.dataLoad)
        downloadthread.data_end.connect(self.dataEnd)
        self.threads.append(downloadthread)
        downloadthread.start()

    def btnAddClicked(self, param):
        self._addVideotoTable(param, self.nwidget)

    def btnAddLinkClicked(self):
        data = self._bin.get_youtube_video_info(self.lnwidget.txt_link.text())
        self._addVideotoTable(data, self.lnwidget)

    def btnAddLinksClicked(self):
        for ln in self.lnswidget.txt_links.toPlainText().split('\n'):
            data = self._bin.get_youtube_video_info(ln.strip())
            self._addVideotoTable(data, self.lnswidget)

    def searchUI(self):
        fbox = QFormLayout()
        fbox.setSpacing = 2
        self.nwidget.txt_arama = QLineEdit()
        self.nwidget.txt_arama.setFixedWidth(720)
        #txt_arama.setText("Aranacak anahtar kelime")
        btn_arama = QPushButton("SEARCH")
        btn_arama.setFixedWidth(50)
        btn_arama.clicked.connect(self.btnSearchClicked)
        btn_arama.setCursor(Qt.PointingHandCursor)
        self.nwidget.txt_arama.returnPressed.connect(self.btnSearchClicked)
        fbox.addRow(self.nwidget.txt_arama, btn_arama)
        return fbox
