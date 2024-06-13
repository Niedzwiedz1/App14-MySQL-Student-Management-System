import sys
from PyQt6.QtWidgets import QWidget, QLabel, QApplication, QLineEdit, QPushButton, \
    QGridLayout, QLayout, QMainWindow, QTableWidgetItem, QTableWidget, QDialog, QVBoxLayout,\
    QComboBox, QToolBar, QStatusBar, QMessageBox

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import sqlite3
import mysql.connector


class DataBaseConnection:
    def __init__(self, host="localhost", user="root", password="pythoncourse", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setFixedWidth(500)
        self.setFixedHeight(500)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_bar = self.menuBar().addMenu("&Help")
        search_menu_bar = self.menuBar().addMenu("&Search")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        add_about_action = QAction("&About", self)
        help_menu_bar.addAction(add_about_action)
        add_about_action.setMenuRole(QAction.MenuRole.NoRole)
        add_about_action.triggered.connect(self.about)

        add_search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_menu_bar.addAction(add_search_action)
        search_menu_bar.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Add Toolbar to the main window
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(add_search_action)

        # Add status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.table.cellClicked.connect(self.clicked_cell)

    def clicked_cell(self):
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)



    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


    def load_data(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()


        self.table.setRowCount(0)
        for row_index, row_data in enumerate(result):
            self.table.insertRow(row_index)
            for column_index, cell_data in enumerate(row_data):
                self.table.setItem(row_index, column_index, QTableWidgetItem(str(cell_data)))

        connection.close()

    def insert(self):
        dialog = RegisterWindow()
        dialog.exec()

    def search(self):
        search = SearchDialog()
        search.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit the details")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Extracting student name from table
        self.index = student_management_system.table.currentRow()
        student_name = student_management_system.table.item(self.index, 1).text()

        # Extracting id of the student
        self.student_id = student_management_system.table.item(self.index, 0).text()

        # Extracting course name from the table
        course_name = student_management_system.table.item(self.index, 2).text()

        # Extracting mobile phone from the table
        mobile_phone = student_management_system.table.item(self.index, 3).text()

        # Create widgets
        # Set current name
        self.name_widget = QLineEdit(student_name)
        self.name_widget.setPlaceholderText("Name")

        self.course_combo_box = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]

        self.course_combo_box.addItems(courses)

        # Set current course name
        self.course_combo_box.setCurrentText(course_name)
        # Set current mobile phone
        self.mobile_widget = QLineEdit(mobile_phone)

        update_button = QPushButton("Update")
        update_button.clicked.connect(self.update)

        layout.addWidget(self.name_widget)
        layout.addWidget(self.course_combo_box)
        layout.addWidget(self.mobile_widget)
        layout.addWidget(update_button)

        self.setLayout(layout)

    def update(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id=%s",
                       (self.name_widget.text(),
                        self.course_combo_box.itemText(self.course_combo_box.currentIndex()),
                        self.mobile_widget.text(),
                        self.student_id
                       ))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh main window
        student_management_system.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.index = student_management_system.table.currentRow()
        self.student_id = student_management_system.table.item(self.index, 0).text()
        self.setWindowTitle("Warning")

        layout = QGridLayout()

        label = QLabel("Are you sure you want to delete record?")
        yes = QPushButton("Yes")
        yes.clicked.connect(self.yes_delete)

        no = QPushButton("No")
        no.clicked.connect(self.no_delete)

        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0, 1, 1)
        layout.addWidget(no, 1, 1, 1, 1)

        self.setLayout(layout)

    def yes_delete(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM students WHERE id = %s", (self.student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        student_management_system.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success!")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()
    def no_delete(self):
        self.close()





class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register New Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        # Create widgets
        self.name_widget = QLineEdit()
        self.name_widget.setPlaceholderText("Name")

        self.course_combo_box = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_combo_box.addItems(courses)

        self.mobile_widget = QLineEdit()
        self.mobile_widget.setPlaceholderText("Mobile")

        button_register = QPushButton("Register")
        button_register.clicked.connect(self.add_student)

        # Add widgets
        layout.addWidget(self.name_widget)
        layout.addWidget(self.course_combo_box)
        layout.addWidget(self.mobile_widget)
        layout.addWidget(button_register)

        self.setLayout(layout)

    def add_student(self):
        name = self.name_widget.text()
        course = self.course_combo_box.itemText(self.course_combo_box.currentIndex())
        mobile = self.mobile_widget.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        student_management_system.load_data()
        cursor.close()
        connection.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Window")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Create widgets
        self.name_box = QLineEdit()
        self.name_box.setPlaceholderText("Search...")
        layout.addWidget(self.name_box)

        button = QPushButton("Search")
        layout.addWidget(button)
        button.clicked.connect(self.search)

        self.setLayout(layout)

    def search(self):
        name = self.name_box.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        rows = list(result)
        print(rows)
        items = student_management_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            student_management_system.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """This App was created during Python course. It is great exercise to learn OOP.
        Feel free to leave any comments or review the code!"""
        self.setText(content)


app = QApplication(sys.argv)
student_management_system = MainWindow()
student_management_system.load_data()
student_management_system.show()
sys.exit(app.exec())

