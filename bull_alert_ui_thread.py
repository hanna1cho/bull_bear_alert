import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import pyupbit
import time

tickers = pyupbit.get_tickers(fiat="KRW")
form_class = uic.loadUiType("alert.ui")[0]


class Worker(QThread):
    finished = pyqtSignal(dict)  # create signal called 'finished'

    def run(self):
        while True:
            data = {}

            for ticker in tickers:
                data[ticker] = self.get_market_info(ticker)  # form dictionary with key and value

            self.finished.emit(data)  # call 'finished'event and emit/send 'data'
            time.sleep(0.5)

    def get_market_info(self, ticker):
        try:
            df = pyupbit.get_ohlcv(ticker)
            ma5 = df['close'].rolling(5).mean()
            last_ma5 = ma5[-2]  # moving average of the last five days excluding today
            price = pyupbit.get_current_price(ticker)

            state = None
            if price > last_ma5:
                state = "Bull"
            else:
                state = "Bear"

            return price, last_ma5, state
        except:
            return None, None, None


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tableWidget.setRowCount(len(tickers))
        self.worker = Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()

    @pyqtSlot(dict)
    def update_table_widget(self, data):
        try:
            for ticker, infos in data.items():
                index = tickers.index(ticker)

                self.tableWidget.setItem(index, 0, QTableWidgetItem(ticker))
                self.tableWidget.setItem(index, 1, QTableWidgetItem(str(infos[0])))
                self.tableWidget.setItem(index, 2, QTableWidgetItem(str(infos[1])))
                self.tableWidget.setItem(index, 3, QTableWidgetItem(str(infos[2])))
        except:
            pass


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()
