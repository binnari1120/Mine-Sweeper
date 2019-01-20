from PyQt5.QtWidgets import *
from PyQt5.Qt import *
import sys
import numpy
import random

class BoardCell(QPushButton):
    def __init__(self, str, row, column):
        super().__init__(str)
        self.row = row
        self.column = column

        self.is_bomb = False

        self.is_visited = False
        self.number_of_bomb_cells_nearby = 0
        self.previous_cell = None
        self.are_bounded_bomb_cells_all_visited = False



class MineSweeper(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_board()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mine Sweeper")
        self.setGeometry(100, 100, 500, 500)

        table_layout = QHBoxLayout()
        table = QTableWidget()
        table.setRowCount(self.table_row_count)
        table.setColumnCount(self.table_column_count)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(table)
        for i in range(self.table_row_count):
            for j in range(self.table_column_count):
                table.setCellWidget(i, j, self.board[i][j])

        btns_layout = QHBoxLayout()
        show_btn = QPushButton("Show")
        self.is_show_btn_active = False
        show_btn.clicked.connect(self.is_show_btn_clicked)

        hide_btn = QPushButton("Hide")
        self.is_hide_btn_active = False
        hide_btn.clicked.connect(self.is_hide_btn_clicked)

        reload_btn = QPushButton("Reload")
        self.is_reload_btn_active = False
        reload_btn.clicked.connect(self.is_reload_btn_clicked)

        check_btn = QPushButton("Check")
        btns_layout.addWidget(show_btn)
        btns_layout.addWidget(hide_btn)
        btns_layout.addWidget(reload_btn)
        btns_layout.addWidget(check_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(table_layout)
        main_layout.addLayout(btns_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)
        self.show()

    def init_board(self):
        self.table_row_count = 9
        self.table_column_count = 9
        self.board = [None for i in range(self.table_row_count * self.table_column_count)]
        self.board = numpy.array(self.board).reshape(self.table_row_count, self.table_column_count)
        for i in range(self.table_row_count):
            for j in range(self.table_column_count):
                self.board[i][j] = BoardCell("", i, j)
                self.board[i][j].clicked.connect(self.is_cell_clicked)

        self.generate_bomb_cells()
        self.update_number_of_bomb_cells_nearby()


    def generate_bomb_cells(self):
        for i in range(self.table_row_count):
            rand_row = random.randint(0, self.table_row_count-1)
            rand_column = random.randint(0, self.table_column_count-1)
            if self.board[rand_row][rand_column].is_bomb == False:
                self.board[rand_row][rand_column].is_bomb = True
            else:
                i = i - 1

    def update_number_of_bomb_cells_nearby(self):
        for i in range(self.table_row_count):
            for j in range(self.table_column_count):
                if self.board[i][j].is_bomb == False:
                    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                    for direction in directions:
                        next_cell_row = self.board[i][j].row + direction[0]
                        if next_cell_row < 0 or next_cell_row == self.table_row_count:
                            continue
                        next_cell_column = self.board[i][j].column + direction[1]
                        if next_cell_column < 0 or next_cell_column == self.table_column_count:
                            continue
                        if self.board[next_cell_row][next_cell_column].is_bomb == True:
                            self.board[i][j].number_of_bomb_cells_nearby += 1

    def is_cell_clicked(self):
        sender = self.sender()
        if sender.is_bomb == True:
            sender.setText("◆")
            message = QMessageBox()
            message.question(self, "Mission Failed!", "Restarting the game!", QMessageBox.Yes)
            self.is_reload_btn_clicked()
            self.is_hide_btn_clicked()
        else:
            sender.setText(str(sender.number_of_bomb_cells_nearby))
            if sender.number_of_bomb_cells_nearby == 0:
                self.is_hide_btn_active = False
                print("Starting from: ", (sender.row, sender.column))
                current_cell = sender
                current_cell.is_visited = True
                current_cell.setText(str(current_cell.number_of_bomb_cells_nearby))
                initial_cell = sender
                while True:
                    next_cell = self.get_next_bounded_bomb_cell_unvisited(current_cell)
                    if next_cell == None:
                        if current_cell == initial_cell:
                            print("No any other cells to advance.. Now at initial point.. exiting the loop..")
                            break
                        else:
                            print("No any other cells to advance.. but not at initial point.. back to the previous cell..")
                            current_cell = current_cell.previous_cell
                            print("Backing to", (current_cell.row, current_cell.column))
                    else:
                        print("Advancing to", (next_cell.row, next_cell.column))
                        previous_cell = current_cell
                        current_cell = next_cell
                        current_cell.previous_cell = previous_cell
                        current_cell.is_visited = True
                        current_cell.setText(str(current_cell.number_of_bomb_cells_nearby))

    def is_show_btn_clicked(self):
        if self.is_show_btn_active == False:
            self.is_show_btn_active = True
            self.is_hide_btn_active = False
            for i in range(self.table_row_count):
                for j in range(self.table_column_count):
                    if self.board[i][j].is_bomb == True:
                        self.board[i][j].setText("◆")
                    else:
                        cnt = self.board[i][j].number_of_bomb_cells_nearby
                        self.board[i][j].setText(str(cnt))


    def is_hide_btn_clicked(self):
        if self.is_hide_btn_active == False:
            self.is_hide_btn_active = True
            self.is_show_btn_active = False
            print("Clicked!")
            for i in range(self.table_row_count):
                for j in range(self.table_column_count):
                    self.board[i][j].setText("")
                    if self.board[i][j].is_bomb == False:
                       self.board[i][j].is_visited = False
                       self.board[i][j].previous_cell = None 


    def is_reload_btn_clicked(self):
        self.clean_board_cells()
        self.generate_bomb_cells()
        self.update_number_of_bomb_cells_nearby()
        self.is_show_btn_active = False
        self.is_show_btn_clicked()


    def clean_board_cells(self):
        for i in range(self.table_row_count):
            for j in range(self.table_column_count):
                self.board[i][j].is_bomb = False
                self.board[i][j].number_of_bomb_cells_nearby = 0
                self.board[i][j].is_visited = False
                self.board[i][j].previous_cell = None


    def get_next_bounded_bomb_cell_unvisited (self, current_cell):
        directions = [(0, -1), (-1, 0), (0, 1), (1, 0)]
        for direction in directions:
            next_cell_row = current_cell.row + direction[0]
            next_cell_column = current_cell.column + direction[1]
            if next_cell_row < 0 or next_cell_row == self.table_row_count:
                continue
            if next_cell_column < 0 or next_cell_column == self.table_column_count:
                continue
            next_cell = self.board[next_cell_row][next_cell_column]
            print(" - Checking..", (next_cell_row, next_cell_column), " / # of bombs nearby: ", next_cell.number_of_bomb_cells_nearby, " / visited: ", next_cell.is_visited)
            if next_cell.number_of_bomb_cells_nearby == 0 and next_cell.is_visited == False:
                return next_cell
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ms = MineSweeper()
    app.exec()
    sys.exit()
