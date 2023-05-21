import psycopg2
import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QTabWidget, QAbstractScrollArea, QVBoxLayout, QHBoxLayout,
                    QTableWidget, QGroupBox, QTableWidgetItem, QPushButton, QMessageBox, QScrollArea, QLabel)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Timetable")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._connect_to_db()
        self._create_timetable_tab()
        self._create_teacher_tab()
        self._create_subject_tab()

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="timetable_db", user="postgres", password="sysiskakolbosa",
                                     host="localhost", port="5432")
        self.cursor = self.conn.cursor()

    def _create_teacher_tab(self):
        self.teacher_tab = QWidget()
        self.tabs.addTab(self.teacher_tab, "Teacher")

        self.teacher_tab_vbox = QVBoxLayout()
        self.teacher_tab_hbox1 = QHBoxLayout()
        self.teacher_tab_hbox2 = QHBoxLayout()
        self.teacher_tab_hbox3 = QHBoxLayout()

        self.teacher_tab_vbox.addLayout(self.teacher_tab_hbox1)
        self.teacher_tab_vbox.addLayout(self.teacher_tab_hbox2)
        self.teacher_tab_vbox.addLayout(self.teacher_tab_hbox3)

        self._create_teacher_table()

        self._create_insert_into_teacher_table()

        self.update_teacher_button = QPushButton("Update")
        self.teacher_tab_hbox3.addWidget(self.update_teacher_button)
        self.update_teacher_button.clicked.connect(self._update_teacher_table)

        self.teacher_tab.setLayout(self.teacher_tab_vbox)

    def _create_teacher_table(self):
        self.teacher_table = QTableWidget()
        self.teacher_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.teacher_table.setColumnCount(4)
        self.teacher_table.setHorizontalHeaderLabels(["ID", "Full name", "", ""])

        self._update_teacher_table()

        self.teacher_tab_hbox1.addWidget(self.teacher_table)

    def _update_teacher_table(self):
        self.cursor.execute("SELECT * FROM teacher")
        records = list(self.cursor.fetchall())

        self.teacher_table.setRowCount(len(records))

        for i, r in enumerate(records):
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda ch, rownum=i, teacher_records=records: self._edit_teacher_table(
                                                                                            rownum, teacher_records))
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda ch, teacher_id=r[0]: self._delete_from_teacher_table(teacher_id))

            self.teacher_table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.teacher_table.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.teacher_table.setCellWidget(i, 2, edit_button)
            self.teacher_table.setCellWidget(i, 3, delete_button)

            self.teacher_table.resizeRowsToContents()
            self.teacher_table.resizeColumnsToContents()

    def _create_insert_into_teacher_table(self):
        self.insert_teacher_table = QTableWidget()
        self.insert_teacher_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.insert_teacher_table.setColumnCount(3)
        self.insert_teacher_table.setRowCount(1)
        self.insert_teacher_table.setHorizontalHeaderLabels(["ID", "Full name", ""])

        insert_button = QPushButton("Insert")
        insert_button.clicked.connect(self._insert_into_teacher_table)

        self.insert_teacher_table.setCellWidget(0, 2, insert_button)

        self.teacher_table.resizeRowsToContents()
        self.teacher_table.resizeColumnsToContents()

        self.teacher_tab_hbox2.addWidget(self.insert_teacher_table)

    def _insert_into_teacher_table(self):
        row = list()
        for i in range(self.insert_teacher_table.columnCount()-1):
            try:
                row.append(self.insert_teacher_table.item(0, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("INSERT INTO teacher (id, full_name) VALUES (%s, %s)", (int(row[0]), str(row[1])))
            self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "Enter all fields")

    def _edit_teacher_table(self, rownum, teacher_records):
        row = list()
        for i in range(self.teacher_table.columnCount()-2):
            try:
                row.append(self.teacher_table.item(rownum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("UPDATE teacher SET id=%s, full_name=%s WHERE id=%s", (int(row[0]), str(row[1]),
                                                                                int(teacher_records[rownum][0])))
            self.conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "No such record in the sub table")
        except psycopg2.errors.InvalidTextRepresentation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "Enter all fields")

    def _delete_from_teacher_table(self, teacher_id):
        try:
            self.cursor.execute("DELETE FROM teacher WHERE id=%s", str(teacher_id))
            self.conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "This record is used in another table")

    #######################################################################################

    def _create_subject_tab(self):
        self.subject_tab = QWidget()
        self.tabs.addTab(self.subject_tab, "Subject")

        self.subject_tab_vbox = QVBoxLayout()
        self.subject_tab_hbox1 = QHBoxLayout()
        self.subject_tab_hbox2 = QHBoxLayout()
        self.subject_tab_hbox3 = QHBoxLayout()

        self.subject_tab_vbox.addLayout(self.subject_tab_hbox1)
        self.subject_tab_vbox.addLayout(self.subject_tab_hbox2)
        self.subject_tab_vbox.addLayout(self.subject_tab_hbox3)

        self._create_subject_table()

        self._create_insert_into_subject_table()

        self.update_subject_button = QPushButton("Update")
        self.subject_tab_hbox3.addWidget(self.update_subject_button)
        self.update_subject_button.clicked.connect(self._update_subject_table)

        self.subject_tab.setLayout(self.subject_tab_vbox)

    def _create_subject_table(self):
        self.subject_table = QTableWidget()
        self.subject_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.subject_table.setColumnCount(5)
        self.subject_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "", ""])

        self._update_subject_table()

        self.subject_tab_hbox1.addWidget(self.subject_table)

    def _update_subject_table(self):
        self.cursor.execute("SELECT * FROM subject")
        records = list(self.cursor.fetchall())

        self.subject_table.setRowCount(len(records))

        for i, r in enumerate(records):
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda ch, rownum=i, subject_records=records: self._edit_subject_table(
                                                                                            rownum, subject_records))
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda ch, subject_id=r[0]: self._delete_from_subject_table(subject_id))

            self.subject_table.setItem(i, 0, QTableWidgetItem(str(r[0])))
            self.subject_table.setItem(i, 1, QTableWidgetItem(str(r[1])))
            self.subject_table.setItem(i, 2, QTableWidgetItem(str(r[2])))
            self.subject_table.setCellWidget(i, 3, edit_button)
            self.subject_table.setCellWidget(i, 4, delete_button)

            self.subject_table.resizeRowsToContents()
            self.subject_table.resizeColumnsToContents()

    def _create_insert_into_subject_table(self):
        self.insert_subject_table = QTableWidget()
        self.insert_subject_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.insert_subject_table.setColumnCount(4)
        self.insert_subject_table.setRowCount(1)
        self.insert_subject_table.setHorizontalHeaderLabels(["ID", "Name", "Type", ""])

        insert_button = QPushButton("Insert")
        insert_button.clicked.connect(self._insert_into_subject_table)

        self.insert_subject_table.setCellWidget(0, 3, insert_button)

        self.insert_subject_table.resizeRowsToContents()

        self.subject_tab_hbox2.addWidget(self.insert_subject_table)

    def _insert_into_subject_table(self):
        row = list()
        for i in range(self.insert_subject_table.columnCount()-1):
            try:
                row.append(self.insert_subject_table.item(0, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("INSERT INTO subject (id, name, type) VALUES (%s, %s, %s)", (int(row[0]),
                                                                                             str(row[1]), str(row[2])))
            self.conn.commit()
        except:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "Enter all fields")

    def _edit_subject_table(self, rownum, subject_records):
        row = list()
        for i in range(self.subject_table.columnCount() - 2):
            try:
                row.append(self.subject_table.item(rownum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("UPDATE subject SET id=%s, name=%s, type=%s WHERE id=%s", (str(row[0]), str(row[1]),
                                                                str(row[2]), str(subject_records[rownum][0])))
            self.conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "No such record in the sub table")
        except psycopg2.errors.InvalidTextRepresentation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "Enter all fields")

    def _delete_from_subject_table(self, subject_id):
        try:
            self.cursor.execute("DELETE FROM subject WHERE id=%s", str(subject_id))
            self.conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "This record is used in another table")

    ################################################################################################

    def _create_timetable_tab(self):
        self.timetable_tab_scroll = QScrollArea()
        self.tabs.addTab(self.timetable_tab_scroll, "Timetable")

        self.timetable_tab = QWidget()
        self.timetable_tab_scroll.setWidget(self.timetable_tab)

        self.timetable_tab_vbox = QVBoxLayout(self.timetable_tab)
        self.timetable_tab.setLayout(self.timetable_tab_vbox)

        self._create_timetable_table()
        self._create_insert_into_timetable_table()

        self.update_timetable_button = QPushButton("Update")
        self.timetable_tab_vbox.addWidget(self.update_timetable_button)
        self.update_timetable_button.clicked.connect(self._update_timetable_table)

        self.timetable_tab_scroll.setWidgetResizable(True)
        self.resize(900, 500)

    def _create_timetable_table(self):
        self.odd_label = QLabel("Нечетная неделя")
        self.even_label = QLabel("Четная неделя")

        self.table_odd_mon = QTableWidget()
        self.table_odd_tue = QTableWidget()
        self.table_odd_wed = QTableWidget()
        self.table_odd_thu = QTableWidget()
        self.table_odd_fri = QTableWidget()
        self.table_odd_sat = QTableWidget()
        self.table_odd_sun = QTableWidget()

        self.table_even_mon = QTableWidget()
        self.table_even_tue = QTableWidget()
        self.table_even_wed = QTableWidget()
        self.table_even_thu = QTableWidget()
        self.table_even_fri = QTableWidget()
        self.table_even_sat = QTableWidget()
        self.table_even_sun = QTableWidget()

        self.timetable_tab_vbox.addWidget(self.odd_label)

        self._create_weekday_table(self.table_odd_mon, "Понедельник")
        self._create_weekday_table(self.table_odd_tue, "Вторник")
        self._create_weekday_table(self.table_odd_wed, "Среда")
        self._create_weekday_table(self.table_odd_thu, "Четверг")
        self._create_weekday_table(self.table_odd_fri, "Пятница")
        self._create_weekday_table(self.table_odd_sat, "Суббота")
        self._create_weekday_table(self.table_odd_sun, "Воскресенье")

        self.timetable_tab_vbox.addWidget(self.even_label)

        self._create_weekday_table(self.table_even_mon, "Понедельник")
        self._create_weekday_table(self.table_even_tue, "Вторник")
        self._create_weekday_table(self.table_even_wed, "Среда")
        self._create_weekday_table(self.table_even_thu, "Четверг")
        self._create_weekday_table(self.table_even_fri, "Пятница")
        self._create_weekday_table(self.table_even_sat, "Суббота")
        self._create_weekday_table(self.table_even_sun, "Воскресенье")

        self._update_timetable_table()

    def _create_weekday_table(self, table, weekday):
        weekday_gbox = QGroupBox(weekday)
        weekday_vbox = QVBoxLayout()
        weekday_gbox.setLayout(weekday_vbox)

        weekday_gbox.setMinimumSize(800, 200)

        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(["ID", "Weekday", "Parity", "Time", "Subject", "Teacher", "Room", "", ""])

        weekday_vbox.addWidget(table)
        self.timetable_tab_vbox.addWidget(weekday_gbox)

    def _update_timetable_table(self):
        self._update_weekday_table(self.table_odd_mon, "Нечетная неделя", "Понедельник")
        self._update_weekday_table(self.table_odd_tue, "Нечетная неделя", "Вторник")
        self._update_weekday_table(self.table_odd_wed, "Нечетная неделя", "Среда")
        self._update_weekday_table(self.table_odd_thu, "Нечетная неделя", "Четверг")
        self._update_weekday_table(self.table_odd_fri, "Нечетная неделя", "Пятница")
        self._update_weekday_table(self.table_odd_sat, "Нечетная неделя", "Суббота")
        self._update_weekday_table(self.table_odd_sun, "Нечетная неделя", "Воскресенье")

        self._update_weekday_table(self.table_even_mon, "Четная неделя", "Понедельник")
        self._update_weekday_table(self.table_even_tue, "Четная неделя", "Вторник")
        self._update_weekday_table(self.table_even_wed, "Четная неделя", "Среда")
        self._update_weekday_table(self.table_even_thu, "Четная неделя", "Четверг")
        self._update_weekday_table(self.table_even_fri, "Четная неделя", "Пятница")
        self._update_weekday_table(self.table_even_sat, "Четная неделя", "Суббота")
        self._update_weekday_table(self.table_even_sun, "Четная неделя", "Воскресенье")

    def _update_weekday_table(self, table, parity, weekday):
        time_row = ['9:30-11:05', '11:20-12:55', '13:10-14:45', '15:25-17:00', '17:15-18:50']
        row_counter = 0

        self.cursor.execute("SELECT * FROM timetable WHERE parity=%s AND weekday=%s", (parity, weekday))
        records = list(self.cursor.fetchall())
        table.setRowCount(len(records))

        for i, time in enumerate(time_row):
            self.cursor.execute("SELECT * FROM timetable WHERE parity=%s AND weekday=%s AND time=%s",
                                                                                        (parity, weekday, time))
            records = list(self.cursor.fetchall())
            if records:
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda ch, rownum=row_counter, t=table, id=records[0][0]:
                                                                    self._edit_timetable_table(rownum, t, id))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda ch, timetable_id=records[0][0]:
                                                                    self._delete_from_timetable_table(timetable_id))
                table.setItem(row_counter, 0, QTableWidgetItem(str(records[0][0])))
                table.setItem(row_counter, 1, QTableWidgetItem(str(records[0][1])))
                table.setItem(row_counter, 2, QTableWidgetItem(str(records[0][2])))
                table.setItem(row_counter, 3, QTableWidgetItem(str(records[0][3])))
                table.setItem(row_counter, 4, QTableWidgetItem(str(records[0][4])))
                table.setItem(row_counter, 5, QTableWidgetItem(str(records[0][5])))
                table.setItem(row_counter, 6, QTableWidgetItem(str(records[0][6])))
                table.setCellWidget(row_counter, 7, edit_button)
                table.setCellWidget(row_counter, 8, delete_button)

                table.resizeRowsToContents()
                table.resizeColumnsToContents()

                row_counter += 1

    def _create_insert_into_timetable_table(self):
        self.insert_timetable_table = QTableWidget()
        self.insert_timetable_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.insert_timetable_table.setColumnCount(8)
        self.insert_timetable_table.setRowCount(1)
        self.insert_timetable_table.setHorizontalHeaderLabels(["ID", "Weekday", "Parity", "Time", "Subject",
                                                               "Teacher", "Room", ""])

        insert_button = QPushButton("Insert")
        insert_button.clicked.connect(self._insert_into_timetable_table)

        self.insert_timetable_table.setCellWidget(0, 7, insert_button)

        self.insert_timetable_table.resizeRowsToContents()

        self.timetable_tab_vbox.addWidget(self.insert_timetable_table)

    def _edit_timetable_table(self, rownum, table, id):
        row = list()
        for i in range(table.columnCount() - 2):
            try:
                row.append(table.item(rownum, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("UPDATE timetable SET id=%s, weekday=%s, parity=%s, time=%s, subject=%s, "
                                "teacher=%s, room=%s WHERE id=%s", (str(row[0]), str(row[1]), str(row[2]),
                                                                    str(row[3]), str(row[4]), str(row[5]),
                                                                    str(row[6]), str(id)))
            self.conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "No such record in the sub table")
        except psycopg2.errors.InvalidTextRepresentation:
            self.cursor.execute("ROLLBACK")
            QMessageBox.about(self, "Error", "Enter all fields")

    def _delete_from_timetable_table(self, timetable_id):
        try:
            self.cursor.execute("DELETE FROM timetable WHERE id=%s", str(timetable_id))
            self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "No such record")

    def _insert_into_timetable_table(self):
        row = list()
        for i in range(self.insert_timetable_table.columnCount() - 1):
            try:
                row.append(self.insert_timetable_table.item(0, i).text())
            except:
                row.append(None)
        try:
            self.cursor.execute("INSERT INTO timetable (id, weekday, parity, time, subject, teacher, room) VALUES "
                                "(%s, %s, %s, %s, %s, %s, %s)", (str(row[0]), str(row[1]), str(row[2]), str(row[3]),
                                                                 str(row[4]), str(row[5]), str(row[6])))
            self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "Enter all fields")


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
