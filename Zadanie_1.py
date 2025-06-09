import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QColorDialog
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt

class PatternGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generator Wzorów")
        self.resize(500, 450)

        self.colors = [QColor("black"), QColor("red"), QColor("blue")]

        

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)


        self.canvas_label = QLabel()
        self.canvas = QPixmap(400, 300)
        self.canvas.fill(Qt.GlobalColor.white)
        self.canvas_label.setPixmap(self.canvas)
        main_layout.addWidget(self.canvas_label, alignment=Qt.AlignmentFlag.AlignCenter)

        #kontrolki
        ctrl_layout = QHBoxLayout()
        main_layout.addLayout(ctrl_layout)

        # Wybór wzoru
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(["Kropki", "Pionowe Linie", "Małe Kółka"])
        ctrl_layout.addWidget(self.pattern_combo)

        # Wybór kolorów
        self.color_count_combo = QComboBox()
        self.color_count_combo.addItems(["1", "2", "3"])
        ctrl_layout.addWidget(self.color_count_combo)

        # przycsiki
        self.color_buttons = []
        for i in range(3):
            btn = QPushButton(f"Kolor {i+1}")
            btn.clicked.connect(lambda _, idx=i: self.choose_color(idx))
            self.color_buttons.append(btn)
            ctrl_layout.addWidget(btn)

        draw_btn = QPushButton("Narysuj")
        draw_btn.clicked.connect(self.draw_pattern)
        ctrl_layout.addWidget(draw_btn)

    def choose_color(self, index):
        col = QColorDialog.getColor(
            initial=self.colors[index],
            parent=self,
            title=f"Wybierz kolor {index+1}"
        )
        if col.isValid():
            self.colors[index] = col
            # Pokazywanie wybranego koloru na  przycisku
            self.color_buttons[index].setStyleSheet(f"background-color: {col.name()};")

    def draw_pattern(self):         #generowanie patternu
        w, h = self.canvas.width(), self.canvas.height()
        count = int(self.color_count_combo.currentText())
        pattern = self.pattern_combo.currentText()

        new_canvas = QPixmap(w, h)
        new_canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(new_canvas)

        if pattern == "Kropki":
            step, size = 20, 8
            for x in range(0, w, step):
                for y in range(0, h, step):
                    idx = ((x // step) + (y // step)) % count
                    painter.setBrush(self.colors[idx])
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(x, y, size, size)

        elif pattern == "Pionowe Linie":
            spacing, pen_w = 15, 3
            for i, x in enumerate(range(0, w, spacing)):
                pen = QPen(self.colors[i % count], pen_w)
                painter.setPen(pen)
                painter.drawLine(x, 0, x, h)

        elif pattern == "Małe Kółka":
            step, r = 25, 10
            for x in range(step//2, w, step):
                for y in range(step//2, h, step):
                    idx = ((x // step) + (y // step)) % count
                    painter.setBrush(self.colors[idx])
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(x - r, y - r, 2*r, 2*r)

        painter.end()
        self.canvas_label.setPixmap(new_canvas)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PatternGenerator()
    window.show()
    sys.exit(app.exec())
