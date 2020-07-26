import os
import sys
from PyQt5 import Qt, QtGui, QtCore
from PyQt5.Qt import QFileDialog, QApplication, QMessageBox, QMainWindow, QWindow


class CSVCurveLoader(QFileDialog):
    """ This class loads only CSV files, and outputs them as either str or pandas.DataFrame"""
    def __init__(self, parent=None, window_title='Select a File', start_dir=os.getcwd(), *args):
        QFileDialog.__init__(self, parent, window_title, start_dir, *args)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        if sys.platform == 'darwin':
            self.setOption(QFileDialog.DontUseNativeDialog)
        self.data = None
        title = 'Select a csv file to plot'
        while True:
            self.file_path: str = self.getOpenFileName(self, title)[0]
            if self.file_path[-3:] == 'csv':
                with open(file=self.file_path, mode='r') as csvfile:
                    self.data = csvfile.read()
                    break
            elif self.file_path == "":
                break
            else:
                dialog = QMessageBox(icon=QMessageBox.Warning)
                dialog.setText('Please, select a csv file!')
                dialog.exec_()
                dialog.show()
                continue

    def get_data_string(self):
        return self.data

    def get_data_dataframe(self):
        import pandas as pd
        df = None
        if self.file_path[-3:] == 'csv':
            df = pd.read_csv(self.file_path)
        return df
    pass


if __name__ == '__main__':
    # TEST section
    app = QApplication([])
    cv = CSVCurveLoader()
    print(f'data: {cv.get_data_string()}')  # TODO verify if Exceptions are properly handles (ex no file selected)
    print(f'df: {cv.get_data_dataframe()}')
    pass

# TODO:
#   example: QFileDialog(None, "Load Flowchart..", startDir, "Flowchart (*.fc)")