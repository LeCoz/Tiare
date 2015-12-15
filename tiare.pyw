from PySide import QtGui
from view import Tiare
import sys


def main():
    app = QtGui.QApplication(sys.argv)
    m = Tiare()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
