import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QMouseEvent
from PyQt6.QtCore import Qt, QTime, QPoint

#mouse events:
class MazeLabel(QLabel):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.setMouseTracking(True)

    def mousePressEvent(self, event: QMouseEvent):
        self.game.handle_press(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.game.handle_move(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.game.handle_release(event)


class MazeGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gra: Przejdź Labirynt")
        self.cols, self.rows = 10, 12
        self.cell_size = 40
        self.W, self.H = self.cols * self.cell_size, self.rows * self.cell_size

    # #=ściana, S=start, E=meta, spacja=ścieżka
        maps = [
            [
                "##########",
                "#S   #   #",
                "# ## ##  #",
                "#    #  ##",
                "###  #   #",
                "#   #### #",
                "#  #     #",
                "#    ##  #",
                "## ###   #",
                "#   #    #",
                "#  ##  E #",
                "##########",
            ],
            [
                "##########",
                "# S      #",
                "# ## ### #",
                "#    #   #",
                "#### # ###",
                "#    #   #",
                "# ## ### #",
                "# #  #   #",
                "#   ###  #",
                "#  ##   E#",
                "#        #",
                "##########",
            ],
            [
                "##########",
                "# S #    #",
                "#   ## # #",
                "###    # #",
                "#   #### #",
                "# #      #",
                "# # ######",
                "# #   #  #",
                "#   ##   #",
                "# ###  # #",
                "#     # E#",
                "##########",
            ],
        ]

    # Parsowanie stringa do siatki 
        self.mazes = []
        for idx, m in enumerate(maps, start=1):
            grid, Spos, Epos = [], None, None
            for r, row in enumerate(m):
                row_cells = []
                for c, ch in enumerate(row):
                    if ch == '#':
                        row_cells.append(1)
                    else:
                        row_cells.append(0)
                        if ch == 'S':
                            Spos = (c, r)
                        elif ch == 'E':
                            Epos = (c, r)
                grid.append(row_cells)
            self.mazes.append({
                "name": f"Labirynt {idx}",
                "grid": grid, "start": Spos, "end": Epos
            })

        self._init_ui()
        self.new_game()  # losowy wybór  na starcie

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        vbox = QVBoxLayout(central)

        self.label = MazeLabel(self)
        self.label.setFixedSize(self.W, self.H)
        vbox.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

    # Przycisk wybór labiryntu, przycisk Nowa Gra
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        self.maze_combo = QComboBox()
        for m in self.mazes:
            self.maze_combo.addItem(m["name"])
        hbox.addWidget(self.maze_combo)

        new_btn = QPushButton("Nowa Gra")
        new_btn.clicked.connect(self.new_game)
        hbox.addWidget(new_btn)

    def new_game(self):
        idx = self.maze_combo.currentIndex()
        self.current = self.mazes[idx]
        

        self.base_pixmap = QPixmap(self.W, self.H)
        self._draw_maze(self.base_pixmap, self.current["grid"],
                        self.current["start"], self.current["end"])
     
        self.path_pixmap = QPixmap(self.base_pixmap)
        self.label.setPixmap(self.path_pixmap)

       
        self.is_drawing = False
        self.start_time = None
        self.last_pt = None

        QMessageBox.information(
            self, "Witaj!",
            "Kliknij i przytrzymaj lewy przycisk myszy w zielonym polu START, "
            "następnie prowadź kursor do czerwonego pola META nie dotykając ścian i "
            "nie puszczając przycisku. Powodzenia")

    def _draw_maze(self, pix: QPixmap, grid, start, end):
       
        pix.fill(Qt.GlobalColor.white)
        p = QPainter(pix)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(Qt.GlobalColor.black)
    # Ściany
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                if cell == 1:
                    p.drawRect(c*self.cell_size, r*self.cell_size,
                               self.cell_size, self.cell_size)
    # Start
        p.setBrush(Qt.GlobalColor.green)
        sc = start
        p.drawRect(sc[0]*self.cell_size, sc[1]*self.cell_size,
                   self.cell_size, self.cell_size)
    # Meta
        p.setBrush(Qt.GlobalColor.red)
        ec = end
        p.drawRect(ec[0]*self.cell_size, ec[1]*self.cell_size,
                   self.cell_size, self.cell_size)
        p.end()

    def handle_press(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        x, y = event.position().toPoint().x(), event.position().toPoint().y()
        c, r = x // self.cell_size, y // self.cell_size
        # uruchamianie trybu rysowania
        if (c, r) == self.current["start"]:
            self.is_drawing = True
            self.last_pt = QPoint(x, y)
            self.start_time = QTime.currentTime()

    def handle_move(self, event: QMouseEvent):
        if not self.is_drawing:
            return
        x, y = event.position().toPoint().x(), event.position().toPoint().y()
        #przegrana
        if not (0 <= x < self.W and 0 <= y < self.H):
            self._finish(False)
            return

        #Kolizja ze ścianą
        col = self.base_pixmap.toImage().pixelColor(x, y)
        if col == QColor(Qt.GlobalColor.black):
            self._finish(False)
            return

        painter = QPainter(self.path_pixmap)
        pen = QPen(QColor(30, 144, 255), 4)  # dodawanie niebieskiej linii
        painter.setPen(pen)
        painter.drawLine(self.last_pt, QPoint(x, y))
        painter.end()
        self.last_pt = QPoint(x, y)
        self.label.setPixmap(self.path_pixmap)

        # meta 
        c, r = x // self.cell_size, y // self.cell_size
        if (c, r) == self.current["end"]:
            self._finish(True)

    def handle_release(self, event: QMouseEvent):   #puszczenie przycisku
        if self.is_drawing:
            self._finish(False)


    def _finish(self, won: bool):       #koniec, drukowanie wyniku
        self.is_drawing = False
        if won and self.start_time:
            elapsed = self.start_time.msecsTo(QTime.currentTime()) / 1000.0
            QMessageBox.information(
                self, "Zwyciestwo!",
                f"Gratulacje! Przeszedłeś labirynt w {elapsed:.2f} sek.")
        else:
            QMessageBox.warning(
                self, "Przegrana",
                "Niestety, dotknąłeś ściany lub pusściłeś przycisk myszy.\n"
                "Spróbuj ponownie.")
        



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MazeGame()
    window.show()
    sys.exit(app.exec())
