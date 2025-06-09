import sys
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtCore import Qt


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.draw_something()

    def draw_something(self):
        from random import randint
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)

       
        pen = QtGui.QPen()
        pen.setWidth(60)
        pen.setColor(QtGui.QColor('green'))
        painter.setPen(pen)
        painter.drawLine(10, 10, 300, 200)  #rysowanie linii
        painter.drawPoint(200, 150)     #rysowanie punktu

        for n in range(10000):
            painter.drawPoint(
                200+randint(-75, 100),  # x
                150+randint(-100, 80)   # y
                )
        


        painter.end()
        self.label.setPixmap(canvas)

        

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()