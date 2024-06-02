# [Title] LoginWindow
# [DESC] 접속 정보 입력 위젯 생성
# [Writer] geonheek, yuu4172 

import re
import os
import sys
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PyQt5.QtWidgets import (QVBoxLayout, QRadioButton, QComboBox, QLineEdit, QApplication, QMainWindow,
 QTabWidget, QPushButton, QWidget, QTabBar, QMessageBox, QStackedWidget, QDialog, QLabel, QFrame,
 QCheckBox, QTableWidget, QHBoxLayout, QTableWidgetItem, QSpinBox, QTextEdit, QScrollArea,
 QHeaderView, QAbstractItemView, QGridLayout, QProgressBar, QGroupBox, QStyledItemDelegate)
from PyQt5.QtCore import Qt, QRect, pyqtSlot, QRect
from PyQt5.QtGui import QPainter, QTransform, QFont, QBrush, QColor, QPixmap

sys.path.append(os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ))

from module.auto_module import InspectionAutomation

path_src = Path(__file__)
path_database = path_src.parent / "AutoInspection.db"
path_script = path_src.parent.parent / 'script'

windows_inspection_targets = list()
linux_inspection_targets = list()
# [CLASS] VerticalTabWidget
# [DESC] 수직 탭 위젯을 위한 커스텀 QTabBar 구현
# [TODO] None
# [ISSUE] None
class VerticalTabWidget(QTabBar):
    """
    수직 탭 위젯을 위한 커스텀 QTabBar
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # 마우스 트래킹 활성화

        self.hoveredIndex = -1  # 마우스가 올라간 탭의 인덱스
        self.pressedIndex = -1  # 클릭된 탭의 인덱스
        self.selectedIndex = -1  # 선택된 탭의 인덱스

    def paintEvent(self, event):
        """
        각 탭의 텍스트를 그리는 이벤트 핸들러
        :param event: 이벤트 객체
        """
        painter = QPainter(self)
        font = QFont("NanumBarunGothic", 11, QFont.Bold)  # 폰트 이름과 크기 설정
        painter.setFont(font)
        
        for index in range(self.count()):
            tab_rect = self.tabRect(index)  # 현재 탭의 위치와 크기 정보
            tab_text = self.tabText(index)  # 현재 탭의 텍스트
            
            painter.save()
            
            # 탭의 텍스트를 수직으로 그리기 위한 변환 설정
            transform = QTransform()
            transform.translate(tab_rect.x() + tab_rect.width() / 2, tab_rect.y() + tab_rect.height() / 2)
            transform.translate(-tab_rect.height() / 2, -tab_rect.width() / 2)
            painter.setTransform(transform)
            
            # 마우스 오버 및 클릭 상태에 따라 색상 변경
            if index == self.selectedIndex:
                painter.fillRect(QRect(0, 0, tab_rect.height(), tab_rect.width()), QColor('white'))
            elif index == self.hoveredIndex:
                painter.fillRect(QRect(0, 0, tab_rect.height(), tab_rect.width()), QColor('lightgray'))
            
            painter.drawText(QRect(0, 0, tab_rect.height(), tab_rect.width()), Qt.AlignCenter, tab_text)
            painter.restore()

    def mouseMoveEvent(self, event):
        index = self.tabAt(event.pos())
        if index != self.hoveredIndex:
            self.hoveredIndex = index
            self.update()

    def leaveEvent(self, event):
        self.hoveredIndex = -1
        self.update()

    def mousePressEvent(self, event):
        self.pressedIndex = self.tabAt(event.pos())
        self.update() 
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.selectedIndex = self.tabAt(event.pos())
        self.pressedIndex = -1
        self.update()
        super().mouseReleaseEvent(event)

# [CLASS] MainWindow
# [DESC] 메인 창 클래스
# [TODO] None
# [ISSUE] 점검 진행 후 "홈으로" 버튼 클릭 후 MainPage에서 ">" 버튼을 클릭 시 점검 진행 페이지로 넘어감
class MainWindow(QMainWindow):
    """
    메인 창 클래스
    """
    # [Func] __init__
    # [DESC] 취약점 점검 시스템의 메인 창을 초기화합니다.
    # [TODO] None
    # [ISSUE] None
    def __init__(self):
        """
        메인 페이지 클래스
        """
        super().__init__()
        self.setWindowTitle('취약점 점검 시스템')
        self.setGeometry(260, 150, 1035, 700)  # 테이블 글자 짤림 현상때문에 크기를 키움  

        self.setStyleSheet("background-color: white;")
        
        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        self.mainPage = MainPage(self.stackedWidget)

        self.stackedWidget.addWidget(self.mainPage)
        
        
# [CLASS] MainPage
# [DESC] 메인 페이지 클래스
# [TODO] None
# [ISSUE] None
class MainPage(QWidget):
    """
    메인 페이지 클래스
    """
    # [Func] __init__
    # [DESC] 메인 페이지 클래스 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def __init__(self, stackedWidget):
        """
        메인 페이지 클래스 초기화 메서드 
        """
        super().__init__()
        self.input_target_lists = list()
        self.os_type = None
        self.connection_type = None
        self.stackedWidget = stackedWidget
        self.inspection_list_page = InspectionListPage(stackedWidget)        
        self.setup_ui()


    # [Func] setup_ui
    # [DESC] 메인 페이지 UI를 설정하는 메서드
    # [TODO] 디자인적인 요소 
    # [ISSUE] None    
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        tab_widget = QTabWidget()
        tab_widget.setTabBar(VerticalTabWidget())
        vulnerability_check_tab = self.create_vulnerability_check_tab()
        inspection_history_tab = self.create_inspection_history_tab()
        tab_widget.addTab(vulnerability_check_tab, "취약점\n점검")
        tab_widget.addTab(inspection_history_tab, "점검 이력\n조회")
        tab_widget.setTabPosition(QTabWidget.West) 
        tab_widget.setStyleSheet("""
            QTabBar::tab {
                height: 100px;
                width: 100px;
            }
            """)
        layout.addWidget(tab_widget)

    # [Func] create_vulnerability_check_tab
    # [DESC] 취약점 점검 탭을 생성하는 메서드
    # [TODO] None
    # [ISSUE] None    
    def create_vulnerability_check_tab(self):
        vulnerability_check_tab = QWidget()
        self.main_layout = QVBoxLayout(vulnerability_check_tab)  # 전체 위젯을 위한 QVBoxLayout        

        # 입력칸들을 위한 QGridLayout 생성
        input_layout = QGridLayout()
        
        # 대상 OS 선택 박스
        os_type_group_box = QGroupBox("대상 OS 선택")
        # NanumBarunGothic 폰트로 설정하고 볼드 처리
        title_font = QFont("NanumBarunGothic")
        title_font.setBold(True)
        os_type_group_box.setFont(title_font)
        os_type_layout = QHBoxLayout()
        self.os_type_windows = QRadioButton("Windows")
        self.os_type_linux = QRadioButton("Linux")
        self.os_type_windows.clicked.connect(self.osTypeSelect)
        self.os_type_linux.clicked.connect(self.osTypeSelect)
        self.os_type_windows.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        self.os_type_linux.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        os_type_layout.addWidget(self.os_type_windows)
        os_type_layout.addWidget(self.os_type_linux)
        os_type_group_box.setLayout(os_type_layout)
        os_type_group_box.setFixedHeight(60)  # 고정된 높이 설정

        # 접속 방식 선택 박스
        connection_type_group_box = QGroupBox("접속 방식 선택")
        # 접속 방식 선택 박스
        connection_type_group_box = QGroupBox("접속 방식 선택")
        # NanumBarunGothic 폰트로 설정하고 볼드 처리
        title_font = QFont("NanumBarunGothic")
        title_font.setBold(True)
        connection_type_group_box.setFont(title_font)
        connection_type_layout = QHBoxLayout()
        self.connection_type_ssh = QRadioButton("SSH")
        self.connection_type_samba = QRadioButton("Samba")
        self.connection_type_ssh.clicked.connect(self.connectionTypeSelect)
        self.connection_type_samba.clicked.connect(self.connectionTypeSelect)
        self.connection_type_ssh.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        self.connection_type_samba.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        connection_type_layout.addWidget(self.connection_type_ssh)
        connection_type_layout.addWidget(self.connection_type_samba)
        connection_type_group_box.setLayout(connection_type_layout)
        connection_type_group_box.setFixedHeight(60)  # 고정된 높이 설정  
        
        # 선택 박스를 같은 줄에 배치
        input_layout.addWidget(os_type_group_box, 0, 0)
        input_layout.addWidget(connection_type_group_box, 0, 1)

        port_line_edit = QLineEdit()
        port_line_edit.setPlaceholderText("포트 번호")
        port_line_edit.setFixedHeight(30)  # 고정된 높이 설정
        port_line_edit.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        input_layout.addWidget(port_line_edit, 1, 0, 1, 2)

        system_line_edit = QLineEdit()
        system_line_edit.setPlaceholderText("시스템 명칭")
        system_line_edit.setFixedHeight(30)  # 고정된 높이 설정
        system_line_edit.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        input_layout.addWidget(system_line_edit, 2, 0, 1, 2)

        # 시스템 IP 주소 입력칸
        ip_line_edit = QLineEdit()
        ip_line_edit.setPlaceholderText("시스템 IP 주소")
        ip_line_edit.setFixedHeight(30)  # 고정된 높이 설정
        ip_line_edit.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        input_layout.addWidget(ip_line_edit, 3, 0, 1, 2)

        # ID 및 포트 번호 입력칸
        id_line_edit = QLineEdit()
        id_line_edit.setPlaceholderText("ID")
        id_line_edit.setFixedHeight(30)  # 고정된 높이 설정
        id_line_edit.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        input_layout.addWidget(id_line_edit, 4, 0, 1, 2)

        # 비밀번호 입력칸
        password_line_edit = QLineEdit()
        password_line_edit.setEchoMode(QLineEdit.Password)
        password_line_edit.setPlaceholderText("Password")
        password_line_edit.setFixedHeight(30)  # 고정된 높이 설정
        password_line_edit.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        input_layout.addWidget(password_line_edit, 5, 0, 1, 2)

        # 입력칸 배경 하얀색으로 설정
        os_type_group_box.setStyleSheet("background-color: white;")
        connection_type_group_box.setStyleSheet("background-color: white;")
        port_line_edit.setStyleSheet("background-color: white;")
        system_line_edit.setStyleSheet("background-color: white;")
        ip_line_edit.setStyleSheet("background-color: white;")
        id_line_edit.setStyleSheet("background-color: white;")
        password_line_edit.setStyleSheet("background-color: white;")

        # 전체 버튼 레이아웃 생성
        button_layout = QHBoxLayout()
        
        # '점검 대상 추가' 버튼
        add_target_button = QPushButton("점검 대상 추가")
        add_target_button.setFixedSize(140, 30)
        # 버튼 폰트 설정
        button_font = QFont("NanumBarunGothic")
        button_font.setBold(True)
        add_target_button.setFont(button_font)
        add_target_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: #1A73E8;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #B9B9B9;
                background-color: #1256B0;
            }
            QPushButton:pressed {
                color: #B9B9B9;
                background-color: #1256B0;
            }
        """)
        # 테스트용 점검 대상 추가 - 추후 필수 삭제
        add_target_button.clicked.connect(lambda:self.testTarget())
        
        # add_target_button.clicked.connect(lambda: self.add_target_button_clicked(system_line_edit,
        #                                                                          self.os_type, self.connection_type,
        #                                                                          ip_line_edit, port_line_edit,
        #                                                                          id_line_edit, password_line_edit))
        # '점검 대상 추가' 버튼을 레이아웃에 추가하고 양쪽에 Stretch를 추가하여 중앙에 위치하도록 함
        button_layout.addStretch(1)
        button_layout.addWidget(add_target_button)
        button_layout.addStretch(1)

        # '>' 버튼
        next_button = QPushButton(">")
        next_button.setFixedSize(30, 30)
        next_button.setFont(QFont("MalgunGothic", 18, QFont.Bold))  # NanumBarunGothic 폰트로 설정
        next_button.setStyleSheet("""
                                     QPushButton {
                                         color: #A6A6A6;
                                         background-color: #FFFFFF;
                                         border: none;}
                                     QPushButton:hover {
                                         color: #787878;
                                         background-color: #FFFFFF; }
                                    QPushButton:pressed {
                                         color: #787878;
                                         background-color: #FFFFFF; }
                                    """)
        next_button.clicked.connect(lambda: self.on_next_button_clicked())
        button_layout.addWidget(next_button)  # '>' 버튼을 레이아웃의 오른쪽에 추가
        # '>' 버튼 오른쪽의 여백을 최소화하기 위해 Stretch를 추가하지 않음

        # 버튼 레이아웃을 input_layout에 추가, Qt.AlignBottom | Qt.AlignRight 옵션은 필요 없음
        input_layout.addLayout(button_layout, 6, 0, 1, 2, Qt.AlignBottom)

        # QTableWidget 설정
        self.target_lists_table = QTableWidget()
        self.target_lists_table.setColumnCount(5)
        self.target_lists_table.setHorizontalHeaderLabels(['시스템 장치명', 'OS', '접속 방식', 'IP 주소', '삭제'])
        self.target_lists_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.target_lists_table.horizontalHeader().setStretchLastSection(True)

        # 헤더 레이블의 폰트를 설정합니다.
        header_font = QFont("NanumBarunGothic")
        header_font.setBold(True)

        # 헤더 뷰에 폰트를 적용합니다.
        header = self.target_lists_table.horizontalHeader()
        header.setFont(header_font)

        # 최대 높이를 설정합니다.
        maxHeight = 330
        self.target_lists_table.setMaximumHeight(maxHeight)
    
        # 각 열 너비 조정
        self.target_lists_table.setColumnWidth(0, 170)  # 시스템 장치명 열 너비
        self.target_lists_table.setColumnWidth(1, 170)  # OS 열 너비
        self.target_lists_table.setColumnWidth(2, 200)  # 접속 방식 열 너비
        self.target_lists_table.setColumnWidth(3, 200)  # IP 주소 열 너비
        self.target_lists_table.setColumnWidth(4, 40)   # 삭제 열 너비

        self.main_layout.addWidget(self.target_lists_table)

        # 입력칸들을 포함하는 레이아웃을 메인 레이아웃에 추가
        self.main_layout.addLayout(input_layout)

        return vulnerability_check_tab
    # 테스트용 함수 -> 추후 필수 삭제
    def testTarget(self):
        ipAddr = "172.26.245.114"
        rowPosition = self.target_lists_table.rowCount()
        self.target_lists_table.insertRow(rowPosition)
        self.target_lists_table.setItem(rowPosition, 0, QTableWidgetItem("test"))
        self.target_lists_table.setItem(rowPosition, 1, QTableWidgetItem("Windows"))
        self.target_lists_table.setItem(rowPosition, 2, QTableWidgetItem("SSH"))
        self.target_lists_table.setItem(rowPosition, 3, QTableWidgetItem(ipAddr))

        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        btnDelete.setFixedSize(55, 25)
        btnDelete.setFont(QFont("NanumBarunGothic", 8))  # NanumBarunGothic 폰트로 설정
        btnDelete.setStyleSheet("""
                                QPushButton {
                                    color: #EA4335;
                                    background-color: #FFFFFF;
                                    border: 1px solid #EA4335;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #CB2215;
                                    background-color: #B9B9B9;
                                    border: 1px solid #CB2215;}
                                QPushButton:pressed {
                                    color: #CB2215;
                                    background-color: #B9B9B9;
                                    border: 1px solid #CB2215;}
                                """)
        # 버튼을 중앙 정렬하기 위해 QWidget을 생성하고 레이아웃 설정
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btnDelete)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        self.target_lists_table.setCellWidget(rowPosition, 4, widget)
        
        # 글자 크기 조절
        for column in range(self.target_lists_table.columnCount()):
            item = self.target_lists_table.item(rowPosition, column)
            if item is not None:
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)
        
        self.input_target_lists.append(["test", "Windows", "SSH", ipAddr, "22", "etri", "2345"])
    @pyqtSlot()
    def osTypeSelect(self):
        if self.os_type_windows.isChecked():
            self.os_type = "Windows"
        elif self.os_type_linux.isChecked():
            self.os_type = "Linux"
            
    @pyqtSlot()
    def connectionTypeSelect(self):
        if self.connection_type_ssh.isChecked():
            self.connection_type = "SSH"
        elif self.connection_type_samba.isChecked():
            self.connection_type = "Samba"
    # [Func] add_target_button_clicked
    # [DESC] 점검 대상 추가 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None
    """
    def add_target_button_clicked(self, target_name, os_type, connection_type, ip, port, id, password):
        if target_name in self.input_target_lists:
            self.ShowAlert("이미 해당 시스템 장치명을 가진 점검 대상이 존재합니다.")
            return
         # 대상 OS가 선택되지 않았을 경우 경고 메시지 출력 후 종료
        if os_type == None or os_type == "대상 OS 선택":
            self.ShowAlert("점검할 OS를 선택해 주세요")
            return

        # 접속 방식이 선택되지 않았을 경우 경고 메시지 출력 후 종료
        if connection_type == None or connection_type == "접속 방식 선택":
            self.ShowAlert("접속할 방식을 선택해 주세요")
            return
        
        # IP 주소 형식 검사
        ip_reg = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
        if not re.search(ip_reg, ip):
            self.ShowAlert("잘못된 형식의 IP 입니다")
            return

        # 포트 번호가 숫자로 이루어져 있는지 확인
        if not port.isdigit():
            self.ShowAlert("숫자만 입력해 주세요")
            return
        
        rowPosition = self.target_lists_table.rowCount()
        self.target_lists_table.insertRow(rowPosition)
        self.target_lists_table.setItem(rowPosition, 0, QTableWidgetItem(target_name))
        self.target_lists_table.setItem(rowPosition, 1, QTableWidgetItem(os_type))
        self.target_lists_table.setItem(rowPosition, 2, QTableWidgetItem(connection_type))
        self.target_lists_table.setItem(rowPosition, 3, QTableWidgetItem(ip))
        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        self.target_lists_table.setCellWidget(rowPosition, 4, btnDelete)
        
        # 글자 크기 조절
        for column in range(self.target_lists_table.columnCount()):
            item = self.target_lists_table.item(rowPosition, column)
            if item is not None:
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)
        
        self.input_target_lists.append([target_name, os_type, connection_type, ip, port, id, password])
"""
    def add_target_button_clicked(self, target_name, os_type, connection_type, ip, port, id, password):
        _target_name = target_name.text()
        _ip = ip.text()
        _port = port.text()

        if _target_name in self.input_target_lists:
            self.ShowAlert("이미 해당 시스템 장치명을 가진 점검 대상이 존재합니다.")
            return
         # 대상 OS가 선택되지 않았을 경우 경고 메시지 출력 후 종료
        if os_type == None or os_type == "대상 OS 선택":
            self.ShowAlert("점검할 OS를 선택해 주세요")
            return

        # 접속 방식이 선택되지 않았을 경우 경고 메시지 출력 후 종료
        if connection_type == None or connection_type == "접속 방식 선택":
            self.ShowAlert("접속할 방식을 선택해 주세요")
            return
        
        # IP 주소 형식 검사
        ip_reg = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
        if not re.search(ip_reg, _ip):
            self.ShowAlert("잘못된 형식의 IP 입니다")
            return

        # 포트 번호가 숫자로 이루어져 있는지 확인
        if not _port.isdigit():
            self.ShowAlert("숫자만 입력해 주세요")
            return
        
        rowPosition = self.target_lists_table.rowCount()
        self.target_lists_table.insertRow(rowPosition)
        self.target_lists_table.setItem(rowPosition, 0, QTableWidgetItem(_target_name))
        self.target_lists_table.setItem(rowPosition, 1, QTableWidgetItem(os_type))
        self.target_lists_table.setItem(rowPosition, 2, QTableWidgetItem(connection_type))
        self.target_lists_table.setItem(rowPosition, 3, QTableWidgetItem(_ip))
        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        self.target_lists_table.setCellWidget(rowPosition, 4, btnDelete)

        
        # 글자 크기 조절
        for column in range(self.target_lists_table.columnCount()):
            item = self.target_lists_table.item(rowPosition, column)
            if item is not None:
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)
        
        target_name.clear()
        ip.clear()
        id.clear()
        password.clear()

        self.input_target_lists.append([_target_name, os_type, connection_type, _ip, _port, id, password])


    # [Func] deleteRow
    # [DESC] 점검 대상 테이블 삭제 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None
    def deleteRow(self, button):
        index = self.target_lists_table.indexAt(button.pos())
        if index.isValid():
            self.target_lists_table.removeRow(index.row())

            self.input_target_lists.pop(index.row())

    # [Func] on_next_button_clicked
    # [DESC] 다음 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] 점검 진행 후 "홈으로" 버튼 클릭 후 MainPage에서 ">" 버튼을 클릭 시 점검 진행 페이지로 넘어감
    def on_next_button_clicked(self):
        """
        다음 버튼 클릭 시 호출되는 메서드
        """
        
        # 대상 OS에 대한 검사 목록 초기화 및 확인
        if len(self.input_target_lists) == 0:
            self.ShowAlert("최소 한개 이상의 점검 대상을 추가해 주세요.")
            return 
        
        global windows_inspection_targets
        global linux_inspection_targets
        if len(windows_inspection_targets) == 0 or len(linux_inspection_targets) == 0:
            if not os.path.exists(path_database):
                self.ShowAlert("DB가 존재하지 않습니다.")
                return

            con = sqlite3.connect(path_database)
            cursor = con.cursor()

            #db에서 내용불러오기
            try:
                cursor.execute("SELECT TargetID, PluginName, TargetOS, Info, Description, CommandType, ResultType from InspectionTargets WHERE TargetOS=? AND DeleteFlag=0", ("Windows", ))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                self.ShowAlert("DB 실행 에러")
                return

            windows_inspection_targets = cursor.fetchall()
            
            #db에서 내용불러오기
            try:
                cursor.execute("SELECT TargetID, PluginName, TargetOS, Info, Description, CommandType, ResultType from InspectionTargets WHERE TargetOS=? AND DeleteFlag=0", ("Linux", ))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                self.ShowAlert("DB 실행 에러")
                return
            linux_inspection_targets = cursor.fetchall()
            
            con.close()
        
        self.inspection_list_page.SetData(windows_inspection_targets, linux_inspection_targets)
        self.inspection_list_page.SetTarget(self.input_target_lists)
        for i in range(self.stackedWidget.count()):
            if self.stackedWidget.widget(i) == self.inspection_list_page:
                # 스택에 페이지가 이미 존재할 경우 그냥 이동
                self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.inspection_list_page))
        self.stackedWidget.addWidget(self.inspection_list_page)
        self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.inspection_list_page))
        
        # 입력란 초기화
        #self.system_line_edit.clear()
        #self.ip_line_edit.clear()
        #self.id_line_edit.clear()
        #self.port_line_edit.clear()
        #self.password_line_edit.clear()

        #self.ShowAlert("규제 지침 선택 화면으로 넘어가는 로직 구현")

    # [Func] ShowAlert
    # [DESC] 경고창을 표시하는 메서드
    # [TODO] None
    # [ISSUE] None
    def ShowAlert(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle("경고")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        msgBox.exec_()
        
    # [Func] create_inspection_history_tab
    # [DESC] 점검 이력 조회 화면
    # [TODO] None
    # [ISSUE] None    
    def create_inspection_history_tab(self):
        inspection_history_tab = QWidget()
        layout = QVBoxLayout(inspection_history_tab)

        topLayout = QHBoxLayout() # 상단 필터 및 검색 영역
        topLayout.addStretch(1)
        
        self.filter = QComboBox()  # 클래스 속성으로 변경
        self.filter.addItem("대상 OS 필터")
        self.filter.addItem("전체")
        self.filter.addItem("Windows")
        self.filter.addItem("Linux")
        self.filter.setFixedWidth(200)
        self.filter.setFont(QFont("NanumBarunGothic", 9))
        topLayout.addWidget(self.filter) 
        self.filter.currentIndexChanged.connect(self.FilterTable)

        search = QLineEdit() # 검색 필드
        search.setPlaceholderText("IP 주소 검색")
        search.setFixedWidth(200)
        search.setFont(QFont("NanumBarunGothic", 9))
        search.returnPressed.connect(lambda: self.SearchIP(search.text()))
        topLayout.addWidget(search)

        layout.addLayout(topLayout)
        
        self.history_table = QTableWidget() # 테이블 생성
        self.history_table.setColumnCount(5) 
        self.history_table.setHorizontalHeaderLabels(["날짜", "시스템 장치명", "대상 OS", "IP 주소", "상세 결과"])     
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.horizontalHeader().setFont(QFont("NanumBarunGothic", 8, QFont.Bold))
        self.history_table.setFont(QFont("NanumBarunGothic"))
        self.history_table.setSortingEnabled(True) # 정렬 기능
        self.history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.history_table)

        self.LoadRecord() # 이력 불러오기

        return inspection_history_tab
    
    # [Func] FilterTable
    # [DESC] 선택한 대상 OS별로 필터링 해주는 함수
    # [TODO] None
    # [ISSUE] None
    def FilterTable(self):
        current_filter = self.filter.currentText() 
        for row in range(self.history_table.rowCount()):
            os_item = self.history_table.item(row, 2) 
            if os_item is not None:
                show_row = (current_filter in ["전체", "대상 OS 필터"] or current_filter == os_item.text())
                self.history_table.setRowHidden(row, not show_row)
                
    # [Func] SearchIP
    # [DESC] 입력한 IP 주소에 해당하는 이력을 보여주는 함수
    # [TODO] None
    # [ISSUE] 키를 눌렀을때만 기능이 작동하도록 할지 -> 키와 엔터 입력 처리가 좋을듯 합니다.
    def SearchIP(self, searchText):
        for row in range(self.history_table.rowCount()):
            ip_item = self.history_table.item(row, 3) 
            if ip_item and searchText in ip_item.text():
                self.history_table.setRowHidden(row, False)
            else:
                self.history_table.setRowHidden(row, True)
                
    # [Func] LoadRecord
    # [DESC] 점검 이력을 불러오는 메서드
    # [TODO] 에러 테스트
    # [ISSUE] None
    def LoadRecord(self):
        
        global path_database
        
        if not os.path.exists(path_database):
            self.ShowAlert("DB가 존재하지 않습니다.")
            return 

        con = sqlite3.connect(path_database)
        cursor = con.cursor()

        #db에서 내용불러오기
        try:
            cursor.execute("SELECT * FROM InspectionResults")
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            self.ShowAlert("DB 실행 에러")
            return 

        inspection_result_list = cursor.fetchall()
        if len(inspection_result_list) != 0:
            self.result_dict = dict()
            for result in inspection_result_list:
                items_id = result[2]
                if items_id not in self.result_dict:
                    self.result_dict[items_id] = {
                        "items" : [],
                        "targets": [],
                        "date": result[6].split()[0]
                    }
                self.result_dict[items_id]["targets"].append({result[1]: [result[3], result[4],  result[5]]})
            for item in self.result_dict.keys():
                try:
                    cursor.execute("SELECT * from InspectionItems WHERE ItemsID=?",(item,))
                except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                    self.ShowAlert("DB 실행 에러")
                    return
                self.result_dict[item]["items"] = list(cursor.fetchone())
                target_result = dict()
                for target in self.result_dict[item]["targets"]:
                    for target_id, value in target.items():
                        try:
                            cursor.execute("SELECT Info, Description, ResultType, CommandName, CommandType, CommandString  from InspectionTargets WHERE TargetID=?",(target_id,))
                        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                            self.ShowAlert("DB 실행 에러")
                            return
                        target_select_list = list(cursor.fetchone())
                        new_value = [target_select_list[i] for i in range(1, len(target_select_list))] + value
                        target_result[target_select_list[0]] = new_value
                
                self.result_dict[item]["targets"] = target_result
        
        con.close()
            
        for item_id, item_data in self.result_dict.items():
            # 날짜, 대상 OS, IP 주소 데이터 삽입
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)
            self.history_table.setItem(row_position, 0, QTableWidgetItem(item_data['date']))  # 날짜
            self.history_table.setItem(row_position, 1, QTableWidgetItem(item_data['items'][1]))  # 장치 이름
            self.history_table.setItem(row_position, 2, QTableWidgetItem(item_data['items'][2]))  # 대상 OS
            self.history_table.setItem(row_position, 3, QTableWidgetItem(item_data['items'][4]))  # IP 주소
            
            

            # '상세 결과' 버튼 추가
            detail_result_btn = QPushButton('상세 결과')
            btn_font = QFont("NanumBarunGothic", 8)
            detail_result_btn.setFont(btn_font)
            detail_result_btn.setFixedSize(57, 27)
            detail_result_btn.clicked.connect(lambda _, row=row_position: self.DetailResult(row, item_data['targets']))
            detail_result_btn.setStyleSheet("""
                                QPushButton {
                                    color: #1A73E8;
                                    background-color: #FFFFFF;
                                    border: 1px solid #1A73E8;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                QPushButton:pressed {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                """)
            widget = QWidget()
            btn_layout = QHBoxLayout(widget)
            btn_layout.addWidget(detail_result_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(btn_layout)

            self.history_table.setCellWidget(row_position, 4, widget)
            
            # 글자 크기 조절
            for column in range(self.history_table.columnCount()):
                item = self.history_table.item(row_position, column)
                if item is not None:
                    item.setFont(QFont("NanumBarunGothic", 8)) 
                    item.setTextAlignment(Qt.AlignCenter)

            
    # [Func] DetailResult
    # [DESC] 선택한 점검 이력의 상세 결과를 불러옴
    # [TODO] 에러 테스트
    # [ISSUE] None      
    def DetailResult(self, row, targets_data):

        # 선택된 행의 데이터 가져오기
        date = self.history_table.item(row, 0).text()  # 날짜
        os = self.history_table.item(row, 1).text()    # OS
        ip = self.history_table.item(row, 2).text()    # IP 주소

        dialog = QDialog(self) # 상세 결과 창
        dialog.setWindowTitle("상세 결과")
        dialog.resize(925, 600)
        dialog.setStyleSheet("background-color: #FFFFFF;")
        layout = QVBoxLayout()

        header_label = QLabel(f"{date}  /  {os}  /  {ip}  점검 상세 결과") # 선택한 점검 이력의 정보 표시
        font = QFont("NanumBarunGothic", 10, QFont.Bold) 
        header_label.setFont(font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        line = QFrame() # 선
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line)

        # 상세 점검 결과 테이블
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(5)
        self.detail_table.setHorizontalHeaderLabels(["점검 항목", "점검 내용", "결과 방식", "점검 결과", "세부 내용"])
        self.detail_table.setFont(QFont("NanumBarunGothic"))
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 테이블 초기화
        self.detail_table.setRowCount(0)

        
        table_font = QFont("NanumBarunGothic", 8)
        header_font = QFont("NanumBarunGothic", 8, QFont.Bold)
        header = self.detail_table.horizontalHeader()
        header.setFont(header_font)
        
        # 열 길이 설정
        self.detail_table.setColumnWidth(0, 200) # 점검 항목
        self.detail_table.setColumnWidth(1, 440) # 점검 내용
        self.detail_table.setColumnWidth(2, 80) # 결과 방식
        self.detail_table.setColumnWidth(3, 80) # 점검 결과
        self.detail_table.setColumnWidth(4, 80) # 세부 내용
        
        # self.result_dict 순회하며 테이블에 데이터 추가
        for target_id, target_info in targets_data.items():
            # 세부 내용 데이터 추가
            row_position = self.detail_table.rowCount()
            self.detail_table.insertRow(row_position)

            # 데이터 삽입
            item_0 = QTableWidgetItem(target_id)
            item_0.setFont(table_font)
            item_0.setTextAlignment(Qt.AlignCenter)
            self.detail_table.setItem(row_position, 0, item_0)

            item_1 = QTableWidgetItem(target_info[0])  # 설명
            item_1.setFont(table_font)
            item_1.setTextAlignment(Qt.AlignCenter)
            self.detail_table.setItem(row_position, 1, item_1)

            item_2 = QTableWidgetItem(target_info[1])  # 결과 유형
            item_2.setFont(table_font)
            item_2.setTextAlignment(Qt.AlignCenter)
            self.detail_table.setItem(row_position, 2, item_2)

            item_3 = QTableWidgetItem(target_info[5])  # 결과
            item_3.setFont(header_font)
            item_3.setTextAlignment(Qt.AlignCenter)
            if item_3 == "성공":
                item_3.setForeground(QBrush(QColor("#00B050")))
            elif item_3 == "실패":
                item_3.setForeground(QBrush(QColor("#EA4335")))
            self.detail_table.setItem(row_position, 3, item_3)

            # 세부 내용 버튼 추가
            detail_btn = QPushButton('세부 내용')
            btn_font = QFont("NanumBarunGothic", 8)
            detail_btn.setFont(btn_font)
            detail_btn.setFixedSize(60, 27)
            detail_btn.setStyleSheet("""
                                QPushButton {
                                    color: #1A73E8;
                                    background-color: #FFFFFF;
                                    border: 1px solid #1A73E8;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                QPushButton:pressed {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                """)
            detail_btn.clicked.connect(lambda _, row=row_position: self.ItemDetails(row, target_info))

            widget = QWidget()
            btn_layout = QHBoxLayout(widget)
            btn_layout.addWidget(detail_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(btn_layout)

            self.detail_table.setCellWidget(row_position, 4, widget)
        
        layout.addWidget(self.detail_table)

        dialog.setLayout(layout)
        dialog.exec_()

    # [Func] ItemDetails
    # [DESC] 점검 항목의 세부 내용을 보여줌
    # [TODO] 에러 테스트
    # [ISSUE] None    
    def ItemDetails(self, row, target_info):
        # 선택된 행의 데이터 가져오기
        info = self.detail_table.item(row, 0).text()        # 점검 항목
        description = self.detail_table.item(row, 1).text() # 점검 내용
        result_type = self.detail_table.item(row, 2).text() # 결과 방식
        result = self.detail_table.item(row, 3).text()      # 점검 결과

        detail_dialog = QDialog(self)  # 세부 내용 창
        detail_dialog.setWindowTitle("세부 내용")
        detail_dialog.resize(730, 680)

        font = QFont("NanumBarunGothic", 9)
        bold_font = QFont("NanumBarunGothic", 9, QFont.Bold)
        result_font = QFont("NanumBarunGothic", 18, QFont.Bold)
        layout = QVBoxLayout()

        # 점검 결과에 따른 이미지와 글씨색 설정
        if result == "성공":
            result_icon = QLabel()
            result_icon.setPixmap(QPixmap("interface/o.png").scaled(30, 30, Qt.KeepAspectRatio))
            result_content = QLabel(result)
            result_content.setFont(result_font)
            result_content.setStyleSheet("color: #00B050;")
        else: # 실패
            result_icon = QLabel()
            result_icon.setPixmap(QPixmap("interface/x.png").scaled(30, 30, Qt.KeepAspectRatio))
            result_content = QLabel(result)
            result_content.setFont(result_font)
            result_content.setStyleSheet("color: #EA4335;")

        result_content.setFixedHeight(50)
        result_layout = QHBoxLayout()
        result_layout.setContentsMargins(0, 20, 0, 10)
        result_layout.addStretch()
        result_layout.addWidget(result_icon)
        result_layout.addWidget(result_content)
        result_layout.addStretch()
        layout.addLayout(result_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line1)
        
        # 점검 결과, 점검 항목, 점검 내용, 결과 방식
        labels_texts = ["점검 항목", "점검 내용", "결과 방식"]
        contents = [info, description, result_type]

        for label_text, content_text in zip(labels_texts, contents):
            item_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(bold_font)
            content = QLabel(content_text)
            content.setFont(font)
            content.setText(content_text)
            content.setFixedWidth(580)
            item_layout.addWidget(label)
            item_layout.addWidget(content)
    
            layout.addLayout(item_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line2)

        # CommandName, CommandType, CommandString의 정보 표시
        for label_text, content_text in zip(["CommandName", "CommandType", "CommandString"], [target_info[i] for i in [2, 3, 4]]):
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 10, 0, 10)
            label = QLabel(label_text)
            label.setFont(bold_font)
            if label_text == "CommandString":
                content = QTextEdit()
                content.setFont(font)
                content.setReadOnly(True)
                content.setFixedHeight(70)
                content.setFixedWidth(585)
                content.setStyleSheet("QTextEdit {border: 1px solid #FFFFFF;}")
            else:
                content = QLabel(content_text)
                content.setFont(font)
                content.setFixedWidth(580)
            content.setText(content_text)
    
            item_layout.addWidget(label)
            item_layout.addWidget(content)
    
            layout.addLayout(item_layout)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        line3.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line3)
        
        # 출력 메시지, 에러 메시지 정보 표시
        for label_text, content_text in zip(["출력 메시지", "에러 메시지"], [target_info[i] for i in [6, 7]]):
            item_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(bold_font)
            content = QLabel(content_text)
            content.setFont(font)
            content.setFixedWidth(580)
            content.setText(content_text)
    
            item_layout.addWidget(label)
            item_layout.addWidget(content)
    
            layout.addLayout(item_layout)

        detail_dialog.setLayout(layout)
        detail_dialog.exec_()


class CenterAlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(CenterAlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = Qt.AlignCenter

class InspectionListPage(QWidget):
    # [Func] __init__
    # [DESC] 점검 목록 페이지 클래스 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def __init__(self, stackedWidget):
        super(InspectionListPage, self).__init__()

        self.stackedWidget = stackedWidget
        self.inspection_progress_page = InspectionProgressPage(stackedWidget)
        self.inspection_list_table = QTableWidget()
        self.inspection_target_table = QTableWidget()
        self.target_lists = list()

        # 헤더 레이블의 폰트를 설정합니다.
        header_font = QFont("NanumBarunGothic")
        header_font.setBold(True)

        # 헤더 뷰에 폰트를 적용합니다.
        header = self.inspection_target_table.horizontalHeader()
        header.setFont(header_font)
        header = self.inspection_list_table.horizontalHeader()
        header.setFont(header_font)

        self.inspection_target_table.setColumnCount(5)
        self.inspection_target_table.setHorizontalHeaderLabels(['선택', '시스템 장치명', 'OS', '접속 방식', 'IP 주소'])
        self.inspection_target_table.setFont(QFont("NanumBarunGothic"))
        self.inspection_target_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inspection_target_table.horizontalHeader().setStretchLastSection(True)
        self.inspection_target_table.setItemDelegate(CenterAlignDelegate(self)) # 중앙 정렬 델리게이트 설정
        
        
        self.inspection_list_table.setColumnCount(9)
        self.inspection_list_table.setHorizontalHeaderLabels(['선택', '운영체제', '점검 항목', '점검 내용', '실행 방식', '결과 방식', '삭제'])
        self.inspection_list_table.setFont(QFont("NanumBarunGothic"))
        self.inspection_list_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inspection_list_table.horizontalHeader().setStretchLastSection(True)

        
        self.initUI()

    
    # [Func] initUI
    # [DESC] UI 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(self.inspection_target_table)
        layout.addWidget(self.inspection_list_table)
        # inspection_list_table 정렬 설정 
        self.inspection_list_table.horizontalHeader().setDefaultAlignment(Qt.AlignHCenter)
        self.inspection_list_table.verticalHeader().setDefaultAlignment(Qt.AlignVCenter)
        
        # 버튼 레이아웃 생성
        buttonLayout = QHBoxLayout()
        
        # 뒤로 가기 버튼 추가 및 버튼 레이아웃에 설정
        btnBack = QPushButton("<")
        btnBack.setFixedSize(30, 30)
        btnBack.setFont(QFont("MalgunGothic", 18, QFont.Bold))
        btnBack.setStyleSheet("""
                                     QPushButton {
                                         color: #A6A6A6;
                                         background-color: #FFFFFF;
                                         border: none;}
                                     QPushButton:hover {
                                         color: #787878;
                                         background-color: #FFFFFF; }
                                    QPushButton:pressed {
                                         color: #787878;
                                         background-color: #FFFFFF; }
                                    """)
        btnBack.clicked.connect(self.goBack)
        buttonLayout.addWidget(btnBack)  # 버튼 레이아웃에 뒤로 가기 버튼 추가
        
        # "점검 실행" 버튼 생성 및 버튼 레이아웃에 설정
        executeButton = QPushButton("점검 실행")
        executeButton.setFixedSize(110, 30)  # 버튼 크기 설정
        # 버튼 폰트 설정
        button_font = QFont("NanumBarunGothic")
        button_font.setBold(True)
        executeButton.setFont(button_font)
        executeButton.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: #1A73E8;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #B9B9B9;
                background-color: #1A73E8;
            }
            QPushButton:pressed {
                color: #B9B9B9;
                background-color: #1A73E8;
            }
        """)
        executeButton.clicked.connect(self.executeInspection)  # 클릭 시 executeInspection 메서드 호출

        # "규제 지침 등록" 버튼 생성 및 버튼 레이아웃에 설정
        add_btn = QPushButton("규제 지침 등록")
        add_btn.setFixedSize(110, 30)
        add_btn.setFont(QFont("NanumBarunGothic", 9, QFont.Bold))  
        add_btn.setStyleSheet("""
                                QPushButton {
                                    color: #1A73E8;
                                    background-color: #FFFFFF;
                                    border: 1px solid #1A73E8;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                QPushButton:pressed {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                """)
        add_btn.clicked.connect(self.AddInspectionList) # 규제 지침 등록 창 열기
        buttonLayout.addWidget(add_btn) # 버튼 레이아웃에 뒤로 가기 버튼 추가
        buttonLayout.addStretch()
        # 버튼을 가운데로 정렬하기 위해 빈 공간 추가
        buttonLayout.addWidget(executeButton)
        buttonLayout.addStretch()
        
        dummy = QLabel("")
        dummy.setFixedSize(140, 30)
        dummy.setStyleSheet("background-color: white")
        buttonLayout.addWidget(dummy, alignment=Qt.AlignmentFlag.AlignRight)

        # 버튼 레이아웃을 메인 레이아웃에 추가하여 정렬
        layout.addLayout(buttonLayout)

        # 각 열 너비 조정
        self.inspection_target_table.setColumnWidth(0, 50)  
        self.inspection_target_table.setColumnWidth(1, 222)  
        self.inspection_target_table.setColumnWidth(2, 222)  
        self.inspection_target_table.setColumnWidth(3, 222)  
        self.inspection_target_table.setColumnWidth(4, 222)

        # 열 너비 설정
        self.inspection_list_table.setColumnWidth(0, 40)
        self.inspection_list_table.setColumnWidth(1, 70)
        self.inspection_list_table.setColumnWidth(2, 190)
        self.inspection_list_table.setColumnWidth(3, 440)
        self.inspection_list_table.setColumnWidth(4, 80)
        self.inspection_list_table.setColumnWidth(5, 80)
        self.inspection_list_table.setColumnWidth(6, 30)
        
    # [Func] AddInspectionList
    # [DESC] 규제 지침 등록 화면
    # [TODO] 예외 처리
    # [ISSUE] None        
    def AddInspectionList(self):
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("규제 지침 등록")
        self.dialog.resize(600, 600)

        layout = QVBoxLayout()
        self.dialog.setLayout(layout)

        fields = ["PluginName", "TargetOS", "Result_Type", "Info", "Description", "CommandCount", "CommandName",
                "CommandType", "CommandString"]
        input_types = [QLineEdit, QComboBox, QComboBox, QLineEdit, QTextEdit, QSpinBox, QLineEdit, QComboBox, QTextEdit]  # Description, CommandString을 QTextEdit로 변경

        options = {
            "TargetOS": ["Windows", "Linux"],
            "Result_Type": ["action", "info", "registry"],
            "CommandType": ["Powershell", "cmd", "Bash"]
        }

        self.input_fields = {}  # 입력 필드를 저장할 딕셔너리

        # 폰트 설정
        font = QFont("NanumBarunGothic")
        bold_font = QFont("NanumBarunGothic", 9, QFont.Bold)

        for field, input_type in zip(fields, input_types):
            label = QLabel(field)
            label.setFont(bold_font)
            if input_type == QTextEdit:  # TextEdit인 경우
                input_field = QScrollArea()  # 스크롤
                text_edit = QTextEdit()
                text_edit.setFont(font) 
                text_edit.setAcceptRichText(False)
                text_edit.setMinimumHeight(200)
                input_field.setWidget(text_edit)
                input_field.setWidgetResizable(True)
                self.input_fields[field] = text_edit  # QTextEdit을 딕셔너리에 저장
            else:
                input_field = input_type()
                input_field.setFont(font)
                if isinstance(input_field, QComboBox):
                    if field in options:
                        for option in options[field]:
                            input_field.addItem(option)
                self.input_fields[field] = input_field  # 다른 입력 필드를 딕셔너리에 저장
            layout.addWidget(label)
            layout.addWidget(input_field)

        btn_layout = QHBoxLayout()  # 버튼 레이아웃
        btn_layout.addStretch()
        save_btn = QPushButton('저장')  # '저장' 버튼 추가
        save_btn.setFont(bold_font) 
        save_btn.setFixedSize(50, 30)
        save_btn.setStyleSheet("""
            QPushButton {
                color: #747474;
                background-color: #FFFFFF;
                border-radius: 4px;
                border: 1px solid #747474;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #545454;
                background-color: #B9B9B9;
                border: 1px solid #545454;
            }
            QPushButton:pressed {
                color: #545454;
                background-color: #B9B9B9;
                border: 1px solid #545454;
            }
            """)
        save_btn.clicked.connect(self.addNewPlugin)  # 클릭 이벤트에 함수 연결
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.dialog.exec_()
        
    # [Func] addNewPlugin
    # [DESC] 규제지침 등록 "저장" 버튼 클릭 이벤트
    # [TODO] None
    # [ISSUE] None
    def addNewPlugin(self):
        input_values = {field: input_field.text() if isinstance(input_field, QLineEdit) else 
                        input_field.toPlainText() if isinstance(input_field, QTextEdit) else 
                        input_field.value() if isinstance(input_field, QSpinBox) else 
                        input_field.currentText() if isinstance(input_field, QComboBox) else 
                        None
                        for field, input_field in self.input_fields.items()}
        
        required_fields = ["PluginName", "TargetOS", "Result_Type", "Info", "Description", "CommandCount", "CommandName", "CommandType", "CommandString"]
        if any(input_values[field] in [None, ""] for field in required_fields):
            self.ShowAlert("모든 항목을 입력해주세요.")
            return
        
        if input_values['CommandType'] == 'Powershell':
            value = input_values.get("CommandString")
            input_values['CommandString'] = f"powershell.exe -Command \"{value}\""
        
        global path_script, path_database
        
        xml_path = path_script / f"{input_values['PluginName']}.xml"
        
        if os.path.exists(xml_path):
            self.ShowAlert("동일한 이름의 규제 지침이 존재합니다.")
            self.dialog.reject()
        
        root = ET.Element("Plugin", name=input_values["PluginName"])

        plugin_version = ET.SubElement(root, "PluginVersion")
        plugin_version.text = "1" 

        plugin_name = ET.SubElement(root, "PluginName")
        plugin_name.text = f"{input_values['PluginName']}.xml"

        for key in ["TargetOS", "Result_Type", "Info", "Description"]:
            element = ET.SubElement(root, key)
            element.text = input_values[key]

        commands = ET.SubElement(root, "Commands")

        command_count = ET.SubElement(commands, "CommandCount")
        command_count.text = str(input_values["CommandCount"])

        command = ET.SubElement(commands, "Command")

        for key in ["CommandName", "CommandType", "CommandString"]:
            element = ET.SubElement(command, key)
            element.text = input_values[key]
        
        
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml_as_string = reparsed.toprettyxml(indent="    ")
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(pretty_xml_as_string)

        if os.path.exists(path_database):
            con = sqlite3.connect(path_database)
        else:
            self.ShowAlert("DB를 찾을 수 없습니다.")
            self.dialog.reject()
        
        cursor = con.cursor()
        cursor.execute("INSERT INTO InspectionTargets(PluginName, PluginVersion, TargetOS, ResultType, Info, Description, CommandCount, CommandName, CommandType, CommandString, XmlFilePath) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (input_values["PluginName"], "1", input_values["TargetOS"], input_values["Result_Type"], input_values["Info"], input_values["Description"], input_values["CommandCount"], input_values["CommandName"], input_values["CommandType"], input_values["CommandString"], str(xml_path)))
        con.commit()
        targets_id = cursor.lastrowid
        con.close()
        
        global windows_inspection_targets, linux_inspection_targets
        target_entry = (
            targets_id,
            input_values["PluginName"],
            input_values["TargetOS"],
            input_values["Info"],
            input_values["Description"],
            input_values["CommandType"],
            input_values["Result_Type"]
        )

        if input_values['TargetOS'] == "Windows":
            windows_inspection_targets.append(list(target_entry))
        else:
            linux_inspection_targets.append(list(target_entry))
            
        rowPosition = self.inspection_list_table.rowCount()
        self.inspection_list_table.insertRow(rowPosition)
        
        # 체크박스 추가
        chkBoxWidget = QWidget()
        chkBox = QCheckBox()
        chkBoxLayout = QHBoxLayout(chkBoxWidget)
        chkBoxLayout.addWidget(chkBox)
        chkBoxLayout.setAlignment(Qt.AlignCenter)
        chkBoxLayout.setContentsMargins(0,0,0,0)
        self.inspection_list_table.setCellWidget(rowPosition, 0, chkBoxWidget)
        # 나머지 데이터 추가
        data_fields = ["TargetOS", "PluginName", "Description", "CommandType", "Result_Type"]
        for col, field in enumerate(data_fields, start=1):
            item = QTableWidgetItem(input_values[field])
            item.setTextAlignment(Qt.AlignCenter)  # 중앙 정렬 설정
            self.inspection_list_table.setItem(rowPosition, col, item)
        
        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        btnDelete.setFixedSize(55, 25)
        btnDelete.setFont(QFont("NanumBarunGothic", 8))  # NanumBarunGothic 폰트로 설정
        btnDelete.setStyleSheet("""
                                QPushButton {
                                    color: #EA4335;
                                    background-color: #FFFFFF;
                                    border: 1px solid #EA4335;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #CB2215;
                                    background-color: #B9B9B9;
                                    border: 1px solid #CB2215;}
                                QPushButton:pressed {
                                    color: #CB2215;
                                    background-color: #B9B9B9;
                                    border: 1px solid #CB2215;}
                                """)
        # 버튼을 중앙 정렬하기 위해 QWidget을 생성하고 레이아웃 설정
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btnDelete)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        self.inspection_list_table.setCellWidget(rowPosition, 6, widget)
        self.inspection_list_table.setItem(rowPosition, 7, QTableWidgetItem(input_values["PluginName"]))
        self.inspection_list_table.setColumnHidden(7, True)
        self.inspection_list_table.setItem(rowPosition, 8, QTableWidgetItem(str(targets_id)))
        self.inspection_list_table.setColumnHidden(8, True)
        
        # 글자 크기 조절
        for column in range(self.inspection_list_table.columnCount()):
            item = self.inspection_list_table.item(rowPosition, column)
            if item is not None:
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)
        self.dialog.accept()
        
    # [Func] goBack
    # [DESC] 뒤로 가기 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None        
    def goBack(self):
        self.inspection_list_table.clearContents()
        self.inspection_list_table.setRowCount(0)
        self.stackedWidget.setCurrentIndex(0)  # 첫 번째 페이지로 돌아가기
        
    # [Func] executeInspection
    # [DESC] 점검 실행 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None
    def executeInspection(self):
        plugin_dict = {}
        selected_targets_list = list()
        for row in range(self.inspection_target_table.rowCount()):
            chkBoxWidget = self.inspection_target_table.cellWidget(row, 0)
            chkBox = chkBoxWidget.findChild(QCheckBox)
            if chkBox.isChecked():
                selected_targets_list.append(self.target_lists[row])
                
        if len(selected_targets_list) == 0:
            self.ShowAlert("최소한 하나의 점검 대상을 선택해 주세요")
            return
        for row in range(self.inspection_list_table.rowCount()):
            chkBoxWidget = self.inspection_list_table.cellWidget(row, 0)
            chkBox = chkBoxWidget.findChild(QCheckBox)
            if chkBox.isChecked():
                plugin_dict[self.inspection_list_table.item(row, 7).text()] = [self.inspection_list_table.item(row, 1).text() ,int(self.inspection_list_table.item(row, 8).text())]
        
        if len(plugin_dict) == 0:
            self.ShowAlert("최소한 하나의 규제 지침을 선택해 주세요")
            return 
        self.inspection_progress_page.setInspectionData(selected_targets_list, plugin_dict)
        for i in range(self.stackedWidget.count()):
            if self.stackedWidget.widget(i) == self.inspection_progress_page:
                self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.inspection_progress_page))
                self.inspection_progress_page.runInspection()
        
        self.stackedWidget.addWidget(self.inspection_progress_page)
        self.stackedWidget.setCurrentIndex(self.stackedWidget.indexOf(self.inspection_progress_page))
        self.inspection_progress_page.runInspection()
        #InspectionAutomation(self.os_type, self.ip, self.port, self.connection_type, self.id, self.password, plugin_dict)
        
    # [Func] addInspectionListRow
    # [DESC] 테이블에 새로운 행 추가
    # [TODO] None
    # [ISSUE] None
    def addTargetListRow(self, target_name, os_type, connection_type, ip):
        rowPosition = self.inspection_target_table.rowCount()
        self.inspection_target_table.insertRow(rowPosition)

        # 체크박스 추가
        chkBoxWidget = QWidget()
        chkBox = QCheckBox()
        chkBoxLayout = QHBoxLayout(chkBoxWidget)
        chkBoxLayout.addWidget(chkBox)
        chkBoxLayout.setAlignment(Qt.AlignCenter)
        chkBoxLayout.setContentsMargins(0,0,0,0)
        self.inspection_target_table.setCellWidget(rowPosition, 0, chkBoxWidget)
        # 나머지 데이터 추가
        self.inspection_target_table.setItem(rowPosition, 1, QTableWidgetItem(target_name))
        self.inspection_target_table.setItem(rowPosition, 2, QTableWidgetItem(os_type))
        self.inspection_target_table.setItem(rowPosition, 3, QTableWidgetItem(connection_type))
        self.inspection_target_table.setItem(rowPosition, 4, QTableWidgetItem(ip))
        
        # 글자 크기 조절
        for column in range(self.inspection_list_table.columnCount()):
            item = self.inspection_list_table.item(rowPosition, column)
            if item is not None:
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)    
    # [Func] addInspectionListRow
    # [DESC] 테이블에 새로운 행 추가
    # [TODO] None
    # [ISSUE] None
    def addInspectionListRow(self, TargetID, plugin, os_type, name, description, tool, action):
        rowPosition = self.inspection_list_table.rowCount()
        self.inspection_list_table.insertRow(rowPosition)

        # 체크박스 추가
        chkBoxWidget = QWidget()
        chkBox = QCheckBox()
        chkBoxLayout = QHBoxLayout(chkBoxWidget)
        chkBoxLayout.addWidget(chkBox)
        chkBoxLayout.setAlignment(Qt.AlignCenter)
        chkBoxLayout.setContentsMargins(0,0,0,0)
        self.inspection_list_table.setCellWidget(rowPosition, 0, chkBoxWidget)
        # 나머지 데이터 추가
        self.inspection_list_table.setItem(rowPosition, 1, QTableWidgetItem(os_type))
        self.inspection_list_table.setItem(rowPosition, 2, QTableWidgetItem(name))
        self.inspection_list_table.setItem(rowPosition, 3, QTableWidgetItem(description))
        self.inspection_list_table.setItem(rowPosition, 4, QTableWidgetItem(tool))
        self.inspection_list_table.setItem(rowPosition, 5, QTableWidgetItem(action))
        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        btnDelete.setFixedSize(55, 25)
        btnDelete.setFont(QFont("NanumBarunGothic", 8))  # NanumBarunGothic 폰트로 설정
        btnDelete.setStyleSheet("""
                                QPushButton {
                                    color: #EA4335;
                                    background-color: #FFFFFF;
                                    border: 1px solid #EA4335;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #CB2215;
                                    background-color: #B9B9B9;
                                    border: 1px solid #CB2215;}
                                QPushButton:pressed {
                                    color: #CB2215;
                                    background-color: #B9B9B9;
                                    border: 1px solid #CB2215;}
                                """)
        # 버튼을 중앙 정렬하기 위해 QWidget을 생성하고 레이아웃 설정
        widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(btnDelete)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        self.inspection_list_table.setCellWidget(rowPosition, 6, widget)
        self.inspection_list_table.setItem(rowPosition, 7, QTableWidgetItem(plugin))
        self.inspection_list_table.setColumnHidden(7, True)
        self.inspection_list_table.setItem(rowPosition, 8, QTableWidgetItem(str(TargetID)))
        self.inspection_list_table.setColumnHidden(8, True)
        
        # 글자 크기 조절
        for column in range(self.inspection_list_table.columnCount()):
            item = self.inspection_list_table.item(rowPosition, column)
            if item is not None:
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)

    # [Func] deleteRow
    # [DESC] 선택한 행을 삭제하는 메서드
    # [TODO] None
    # [ISSUE] None
    def deleteRow(self, button):
        index = self.inspection_list_table.indexAt(button.pos())
        if index.isValid():
            self.inspection_list_table.removeRow(index.row())
            target_id = self.inspection_list_table.item(index.row(), 7).text()
            os_type = self.inspection_list_table.item(index.row(), )
            global windows_inspection_targets
            global linux_inspection_targets
            global path_database
            con = sqlite3.connect(path_database)
            cursor = con.cursor()
            cursor.execute("SELECT TargetID from InspectionTargets WHERE TargetID=", (target_id, ))
            
            target_index = cursor.fetchone()
            target_index = target_index[0]
            
            if os_type == "Windows":
                windows_inspection_targets.pop(target_index)
            else:
                linux_inspection_targets.pop(target_index)
            
            cursor.execute("UPDATE from InsectionTargets SET DeleteFlag=1 WHERE TargetID=?", (target_id, ))
            
            con.close()

    # [Func] SetData
    # [DESC] 테이블에 점검 데이터를 설정하는 메서드
    # [TODO] None
    # [ISSUE] None
    def SetData(self, windows_inspection_data, linux_inspection_data):
        # for item in inspection_data:
        #     self.addRow(item[0], item[1], item[2], item[3], item[4], item[5])
        inspection_data = windows_inspection_data + linux_inspection_data
        for item in inspection_data:
            self.addInspectionListRow(item[0], item[1], item[2], item[3], item[4], item[5], item[6])
        
        
    # [Func] SetTarget
    # [DESC] 대상 OS 및 접속 정보를 설정하는 메서드
    # [TODO] None
    # [ISSUE] None
    def SetTarget(self, target_lists):
       self.target_lists = target_lists
       for item in target_lists:
           self.addTargetListRow(item[0], item[1], item[2], item[3])
           
    
    # [Func] ShowAlert
    # [DESC] 경고 메시지를 표시하는 메서드
    # [TODO] None
    # [ISSUE] None
    def ShowAlert(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle("경고")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setFont(QFont("NanumBarunGothic"))
        msgBox.exec_()

# [CLASS] InspectionProgressPage
# [DESC] 점검 진행 페이지
# [TODO] None
# [ISSUE] 점검 대상 등록 페이지에서 ">" 버튼 클릭 시 해당 페이지로 넘어가는 버그 발생 시 "<" 버튼이 동작하지 않음
class InspectionProgressPage(QWidget):
    
    # [Func] __init__
    # [DESC] 점검 목록 페이지 클래스 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def __init__(self, stackedWidget):
        super(InspectionProgressPage, self).__init__()

        self.stackedWidget = stackedWidget
        
        self.target_list = list()
        self.plugin_dict = dict()
        
        self.main_layout = QVBoxLayout()  # QVBoxLayout 인스턴스 생성
        self.setLayout(self.main_layout)  # 위젯의 레이아웃을 main_layout으로 설정
        
        self.initUI()

    
    # [Func] initUI
    # [DESC] UI 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def initUI(self):
        
        # 프로그레스 바 초기화 및 레이아웃에 추가
        self.progressBar = QProgressBar()
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setMaximum(100)  # 프로그레스 바의 최대 값을 100으로 설정
        self.progressBar.setValue(0)  # 초기 프로그레스 바 값 설정
        self.progressBar.setFixedSize(1010, 33)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                color: white;
                font-family: 'NanumBarunGothic';
                font-weight: bold;
                background-color: #C0C0C0;  /* 배경색 유지 */
                border: 1px solid #1A73E8;  /* 테두리 색상 추가 */
                border-radius: 5px;  /* 테두리 둥글게 */
                text-align: center;  /* 텍스트 가운데 정렬 */
                padding: 1px;  /* 패딩 추가 */
            }
            QProgressBar::chunk {
                background-color: #1A73E8;  /* 진행 부분 색상 유지 */
                border-radius: 5px;  /* 진행 부분도 둥글게 */
                margin: 0.5px;  /* 진행 부분의 간격 추가 */
            }
        """)


        self.main_layout.addWidget(self.progressBar)  # main_layout에 프로그레스 바 추가

        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(7)
        self.progress_table.setHorizontalHeaderLabels(['시스템 장치명', '점검 항목', '점검 내용', '결과 방식', '점검 결과', '세부 내용'])
        self.progress_table.horizontalHeader().setStretchLastSection(True)

        # 헤더 레이블의 폰트를 설정합니다.
        header_font = QFont("NanumBarunGothic")
        header_font.setBold(True)

        # 헤더 뷰에 폰트를 적용합니다.
        header = self.progress_table.horizontalHeader()
        header.setFont(header_font)

        # 각 열 너비 조정
        self.progress_table.setColumnWidth(0, 100)  # 시스템 장치명 열 너비
        self.progress_table.setColumnWidth(1, 200)  # 점검 항목 열 너비
        self.progress_table.setColumnWidth(2, 430)  # 점검 내용 열 너비
        self.progress_table.setColumnWidth(3, 80)  # 결과 방식 열 너비
        self.progress_table.setColumnWidth(4, 80)  # 점검 결과 열 너비
        self.progress_table.setColumnWidth(5, 80)  # 상세 결과 열 너비    
        self.main_layout.addWidget(self.progress_table)
        
        # 버튼 레이아웃 생성
        buttonLayout = QHBoxLayout()
        
        # 뒤로 가기 버튼 추가 및 버튼 레이아웃에 설정
        btnBack = QPushButton("<")
        btnBack.setFixedSize(30, 30)
        btnBack.clicked.connect(self.goBack)
        btnBack.setFont(QFont("MalgunGothic", 18, QFont.Bold))  # NanumBarunGothic 폰트로 설정
        btnBack.setStyleSheet("""
                                     QPushButton {
                                         color: #A6A6A6;
                                         background-color: #FFFFFF;
                                         border: none;}
                                     QPushButton:hover {
                                         color: #787878;
                                         background-color: #FFFFFF; }
                                    QPushButton:pressed {
                                         color: #787878;
                                         background-color: #FFFFFF; }
                                    """)
        btnBack.clicked
        buttonLayout.addWidget(btnBack)  # 버튼 레이아웃에 뒤로 가기 버튼 추가

        # "홈으로" 버튼 생성 및 버튼 레이아웃에 설정
        homeButton = QPushButton("홈으로")
        homeButton.setFixedSize(60, 30)  # 버튼 크기 설정
        homeButton.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        homeButton.setStyleSheet("""
                                QPushButton {
                                    color: #1A73E8;
                                    background-color: #FFFFFF;
                                    border: 1px solid #1A73E8;
                                    border-radius: 4px;
                                    font-size: 13px;}
                                QPushButton:hover {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                QPushButton:pressed {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                """)
        homeButton.clicked.connect(self.returnToHome)  # 클릭 시 returnToHome 메서드 호출
        buttonLayout.addWidget(homeButton)
        
        # "취소" 버튼 생성 및 버튼 레이아웃에 설정
        cancelButton = QPushButton("취소")
        cancelButton.setFixedSize(50, 30)  # 버튼 크기 설정
        cancelButton.setFont(QFont("NanumBarunGothic"))  # NanumBarunGothic 폰트로 설정
        cancelButton.setStyleSheet("""
            QPushButton {
                color: #747474;
                background-color: #FFFFFF;
                border-radius: 4px;
                border: 1px solid #747474;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #545454;
                background-color: #B9B9B9;
                border: 1px solid #545454;
            }
            QPushButton:pressed {
                color: #545454;
                background-color: #B9B9B9;
                border: 1px solid #545454;
            }
            """)
        cancelButton.clicked.connect(self.cancelInspection)  # 클릭 시 cancelInspection메서드 호출
       
        # 버튼을 가운데로 정렬하기 위해 빈 공간 추가
        buttonLayout.addStretch()
        buttonLayout.addWidget(cancelButton)


        # 버튼 레이아웃을 메인 레이아웃에 추가하여 정렬
        self.main_layout.addLayout(buttonLayout)
        
    # [Func] runInspection
    # [DESC] 점검 수행 모듈
    # [TODO] None
    # [ISSUE] None
    def runInspection(self):
        for target in self.target_list:
            target_plugin = dict()
            plugin_len = 0
            for key, value in self.plugin_dict.items():
                if target[1] == value[0]:
                    target_plugin[key] = value
                    plugin_len += 1

            result_value, result_data = InspectionAutomation(target[0], target[1], target[2], target[3], target[4], target[5], target[6], target_plugin)
           
            if result_value != 0:
                self.ShowAlert(f"에러 발생! ErrorCode:{result_value}")
                self.goBack()
                return
            
            if result_data is not None and len(result_data) != 0:
                self.addProgressTable(result_data)
            else:
                # Creating a default structure with empty strings for each column
                data = [['' for _ in range(5)] for _ in range(plugin_len)]
                self.addProgressTable(data)
            
            # Update progress bar for each target processed
            self.progressBar.setValue(self.progressBar.value() + plugin_len)

            
    def addProgressTable(self, result_data):
        if result_data is None or len(result_data) == 0:
            return
        
        # '시스템 장치명', '점검 항목', '점검 내용', '결과 방식', '점검 결과'
        # 나머지 데이터 추가
        for result in result_data:
            rowPosition = self.progress_table.rowCount()
            self.progress_table.insertRow(rowPosition)
            result_id = result.pop(0)
            for i, data in enumerate(result):
                
                if str(data).isdigit():
                    item = QTableWidgetItem("성공" if data else "실패")
                    item.setFont(QFont("NanumBarunGothic", 8, QFont.Bold))  # 여기서 폰트와 크기 조절 가능
                    item.setTextAlignment(Qt.AlignCenter)
                    if data:  # 성공일 때
                        item.setForeground(QBrush(QColor("#00B050")))
                    else:  # 실패일 때
                        item.setForeground(QBrush(QColor("#EA4335")))
                    self.progress_table.setItem(rowPosition, i, item)
                else:
                    item = QTableWidgetItem(data if data else "")
                    item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(QBrush(QColor(0 , 0, 0)))
                    self.progress_table.setItem(rowPosition, i, item)
            detail_result_btn = QPushButton("세부 내용")
            detail_result_btn.setFixedSize(65, 25)
            detail_result_btn.setStyleSheet("""
                                QPushButton {
                                    color: #1A73E8;
                                    background-color: #FFFFFF;
                                    border: 1px solid #1A73E8;
                                    border-radius: 4px;}
                                QPushButton:hover {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                QPushButton:pressed {
                                    color: #1256B0;
                                    background-color: #B9B9B9;
                                    border: 1px solid #1256B0;}
                                """)
            detail_result_btn.setFont(QFont("NanumBarunGothic", 8))  # NanumBarunGothic 폰트로 설정
            detail_result_btn.clicked.connect(lambda: self.ItemDetails(detail_result_btn))
            # 버튼을 중앙 정렬하기 위해 QWidget을 생성하고 레이아웃 설정
            widget = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(detail_result_btn)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(layout)
            self.progress_table.setCellWidget(rowPosition, 5, widget)
            self.progress_table.setItem(rowPosition, 6, QTableWidgetItem(str(result_id)))
            self.progress_table.setColumnHidden(6, True)
            
    # [Func] ItemDetails
    # [DESC] 점검 항목의 세부 내용을 보여줌
    # [TODO] 에러 테스트
    # [ISSUE] None    
    def ItemDetails(self, button):
        item = self.progress_table.indexAt(button.pos())
        result_id = self.progress_table.item(item.row(), 6).text()
        
        detail_dialog = QDialog(self)  # 세부 내용 창
        detail_dialog.setWindowTitle("세부 내용")
        detail_dialog.resize(730, 680)
        
        font = QFont("NanumBarunGothic", 9)
        bold_font = QFont("NanumBarunGothic", 9, QFont.Bold)
        result_font = QFont("NanumBarunGothic", 18, QFont.Bold)
        layout = QVBoxLayout()
        
        global path_database
        
        if not os.path.exists(path_database):
            self.ShowAlert("DB가 존재하지 않습니다.")
            return

        con = sqlite3.connect(path_database)
        cursor = con.cursor()

        #db에서 내용불러오기
        try:
            cursor.execute("SELECT * FROM InspectionResults WHERE ResultID=?", (result_id, ))
        except (sqlite3.OperationalError, sqlite3.ProgrammingError):
            self.ShowAlert("DB 실행 에러")
            return 

        inspection_results = list(cursor.fetchone())
        if len(inspection_results) != 0:
            target_id = inspection_results[1]
            items_id = inspection_results[2]
            try:
                cursor.execute("SELECT * from InspectionItems WHERE ItemsID=?",(items_id,))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                self.ShowAlert("DB 실행 에러")
                return
            inspection_items = list(cursor.fetchone())
            try:
                cursor.execute("SELECT CommandName, CommandType, CommandString  from InspectionTargets WHERE TargetID=?",(target_id,))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                self.ShowAlert("DB 실행 에러")
                return
            inspection_targets = list(cursor.fetchone())
        
        con.close()
        # '시스템 장치명', '점검 항목', '점검 내용', '결과 방식', '점검 결과'
        # 선택된 행의 데이터 가져오기
        info = self.progress_table.item(item.row(), 1).text()        # 점검 항목
        description = self.progress_table.item(item.row(), 2).text() # 점검 내용
        result_type = self.progress_table.item(item.row(), 3).text() # 결과 방식
        result = self.progress_table.item(item.row(), 4).text()      # 점검 결과
        
        # 점검 결과에 따른 이미지와 글씨색 설정
        if result == "성공":
            result_icon = QLabel()
            result_icon.setPixmap(QPixmap("interface/o.png").scaled(30, 30, Qt.KeepAspectRatio))
            result_content = QLabel(result)
            result_content.setFont(result_font)
            result_content.setStyleSheet("color: #00B050;")
        else: # "실패"
            result_icon = QLabel()
            result_icon.setPixmap(QPixmap("interface/x.png").scaled(30, 30, Qt.KeepAspectRatio))
            result_content = QLabel(result)
            result_content.setFont(result_font)
            result_content.setStyleSheet("color: #FF0000;")

        result_content.setFixedHeight(50)
        result_layout = QHBoxLayout()
        result_layout.setContentsMargins(0, 20, 0, 10)
        result_layout.addStretch()
        result_layout.addWidget(result_icon)
        result_layout.addWidget(result_content)
        result_layout.addStretch()
        layout.addLayout(result_layout)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        line1.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line1)
                
        # 점검 결과, 점검 항목, 점검 내용, 결과 방식
        labels_texts = ["점검 항목", "점검 내용", "결과 방식"]
        contents = [info, description, result_type]

        for label_text, content_text in zip(labels_texts, contents):
            item_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(bold_font)
            content = QLabel(content_text)
            content.setFont(font)
            content.setText(content_text)
            content.setFixedWidth(580)
            item_layout.addWidget(label)
            item_layout.addWidget(content)
    
            layout.addLayout(item_layout)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        line2.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line2)

        inspection_targets = inspection_targets + [inspection_results[4], inspection_results[5]]
        # CommandName, CommandType, CommandString, 출력 메시지는 db에서 불러올 예정
        for label_text, content_text in zip(["CommandName", "CommandType", "CommandString"], inspection_targets[:3]):
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(0, 10, 0, 10)
            label = QLabel(label_text)
            label.setFont(bold_font)
            if label_text == "CommandString":
                content = QTextEdit()
                content.setFont(font)
                content.setReadOnly(True)
                content.setFixedHeight(70)
                content.setFixedWidth(585)
                content.setStyleSheet("QTextEdit {border: 1px solid #FFFFFF;}")
            else:
                content = QLabel(content_text)
                content.setFont(font)
                content.setFixedWidth(580)
            content.setText(content_text)
    
            item_layout.addWidget(label)
            item_layout.addWidget(content)
    
            layout.addLayout(item_layout)

        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        line3.setStyleSheet("color: #A6A6A6;")
        layout.addWidget(line3)
        
        # 출력 메시지, 에러 메시지
        for label_text, content_text in zip(["출력 메시지", "에러 메시지"], inspection_targets[3:5]):
            item_layout = QHBoxLayout()
            label = QLabel(label_text)
            label.setFont(bold_font)
            content = QLabel(content_text)
            content.setFont(font)
            content.setFixedWidth(580)
            content.setText(content_text)
    
            item_layout.addWidget(label)
            item_layout.addWidget(content)
    
            layout.addLayout(item_layout)

        detail_dialog.setLayout(layout)
        detail_dialog.exec_()
    
    # [Func] goBack
    # [DESC] 뒤로 가기 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None        
    def goBack(self):
        self.progress_table.clearContents()
        self.progress_table.setRowCount(0)
        self.stackedWidget.setCurrentIndex(1)  # 점검 항목 선택 페이지로 돌아가기 
    
    
    def returnToHome(self):
        self.progress_table.clearContents()
        self.progress_table.setRowCount(0)
        self.stackedWidget.setCurrentIndex(0) # 점검 대상 등록 페이지로 돌아가기
    
    # [Func] cancelInspection
    # [DESC] 점검 취소 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None        
    def cancelInspection(self):
        return
    
    # [Func] setInspectionData
    # [DESC] 점검 진행을 위한 데이터 정리
    # [TODO] None
    # [ISSUE] None      
    def setInspectionData(self, target_list:list, plugin_dict:dict):
        self.target_list = target_list
        self.plugin_dict = plugin_dict
        progress_bar_len = 0
        for target in target_list:
            for plugin in plugin_dict.values():
                if target[1] == plugin[0]:
                    progress_bar_len += 1
        self.progressBar.setMaximum(progress_bar_len)
    # [Func] ShowAlert
    # [DESC] 경고 메시지를 표시하는 메서드
    # [TODO] None
    # [ISSUE] None
    def ShowAlert(self, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle("경고")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setFont(QFont("NanumBarunGothic"))
        msgBox.exec_()   
# [Func] main
# [DESC] 프로그램 진입점
# [TODO] None
# [ISSUE] None
def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()