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
 QTabWidget, QPushButton, QWidget, QTabBar, QMessageBox, QStackedWidget, QDialog, QLabel,
 QCheckBox, QTableWidget, QHBoxLayout, QTableWidgetItem, QSpinBox, QTextEdit, QScrollArea,
 QHeaderView, QAbstractItemView, QGridLayout, QProgressBar, QGroupBox)
from PyQt5.QtCore import Qt, QRect, pyqtSlot
from PyQt5.QtGui import QPainter, QTransform, QFont

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
    # [Func] paintEvent
    # [DESC] 수직 탭 텍스트를 그리기 위한 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None
    def paintEvent(self, event):
        """
        각 탭의 텍스트를 그리는 이벤트 핸들러
        :param event: 이벤트 객체
        """
        painter = QPainter(self)
        
        for index in range(self.count()):
            tab_rect = self.tabRect(index) # 현재 탭의 위치와 크기 정보
            tab_text = self.tabText(index) # 현재 탭의 텍스트
            
            painter.save()
            
            # 탭의 텍스트를 수직으로 그리기 위한 변환 설정
            transform = QTransform()
            transform.translate(tab_rect.x() + tab_rect.width() / 2, tab_rect.y() + tab_rect.height() / 2)
            transform.translate(-tab_rect.height() / 2, -tab_rect.width() / 2)
            
            painter.setTransform(transform)
            painter.drawText(QRect(0, 0, tab_rect.height(), tab_rect.width()), Qt.AlignCenter, tab_text)
            
            painter.restore() 

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
        self.setGeometry(260, 150, 980, 700)  # 테이블 글자 짤림 현상때문에 크기를 키움

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
                height: 80px;
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
        
        system_line_edit = QLineEdit()
        system_line_edit.setPlaceholderText("시스템 명칭")
        input_layout.addWidget(system_line_edit, 0, 0)  # 위치 지정

        
        os_type_group_box = QGroupBox("대상 OS 선택")
        self.os_type_windows = QRadioButton("Windows")
        self.os_type_windows.clicked.connect(self.osTypeSelect)
        self.os_type_linux = QRadioButton("Linux")
        self.os_type_linux.clicked.connect(self.osTypeSelect)
        
        os_type_layout = QHBoxLayout()
        os_type_layout.addWidget(self.os_type_windows)
        os_type_layout.addWidget(self.os_type_linux) 
        os_type_group_box.setLayout(os_type_layout)
        
        input_layout.addWidget(os_type_group_box, 0, 1)
        
        ip_line_edit = QLineEdit()
        ip_line_edit.setPlaceholderText("시스템 IP 주소")
        input_layout.addWidget(ip_line_edit, 1, 0)

        connection_type_group_box = QGroupBox("접속 방식 선택")
        self.connection_type_ssh = QRadioButton("SSH")
        self.connection_type_ssh.clicked.connect(self.connectionTypeSelect)
        self.connection_type_samba = QRadioButton("Samba")
        self.connection_type_samba.clicked.connect(self.connectionTypeSelect)
        
        connection_type_layout = QHBoxLayout()
        connection_type_layout.addWidget(self.connection_type_ssh)
        connection_type_layout.addWidget(self.connection_type_samba)
        connection_type_group_box.setLayout(connection_type_layout)
        
        input_layout.addWidget(connection_type_group_box, 1, 1)

        port_line_edit = QLineEdit()
        port_line_edit.setPlaceholderText("포트 번호")
        input_layout.addWidget(port_line_edit, 2, 0)

        id_line_edit = QLineEdit()
        id_line_edit.setPlaceholderText("ID")
        input_layout.addWidget(id_line_edit, 2, 1)

        password_line_edit = QLineEdit()
        password_line_edit.setEchoMode(QLineEdit.Password)
        password_line_edit.setPlaceholderText("Password")
        input_layout.addWidget(password_line_edit, 3, 0)

        next_button = QPushButton("점검 대상 추가")
        next_button.setFixedSize(150, 30)
        next_button.clicked.connect(lambda: self.add_target_button_clicked( system_line_edit.text(),
            self.os_type, self.connection_type,
            ip_line_edit.text(), port_line_edit.text(),
            id_line_edit.text(), password_line_edit.text()))
        input_layout.addWidget(next_button, 3, 1)


        self.target_lists_table = QTableWidget()
        self.target_lists_table.setColumnCount(5)
        self.target_lists_table.setHorizontalHeaderLabels(['시스템 장치명', 'OS', '접속 방식', 'IP 주소', '삭제'])
        self.target_lists_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.target_lists_table.horizontalHeader().setStretchLastSection(True)
        
        self.main_layout.addWidget(self.target_lists_table)
        
        next_button = QPushButton(">")
        next_button.setFixedSize(30, 30)
        next_button.clicked.connect(lambda: self.on_next_button_clicked())
        input_layout.addWidget(next_button, 4, 1, Qt.AlignRight)

        # 입력칸들을 포함하는 레이아웃을 메인 레이아웃에 추가
        self.main_layout.addLayout(input_layout)

        
        return vulnerability_check_tab
    
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
        # os_type = "Windows"
        # connection_type = "SSH"
        # ip = "192.168.0.1"
        # port = "22"
        # id = "admin"
        # password = "password"
        
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
        msgBox.exec_()
        
    # [Func] create_inspection_history_tab
    # [DESC] 점검 이력 조회 탭을 생성하는 메서드
    # [TODO] 검색, 필터링 기능 구현
    # [ISSUE] None
    def create_inspection_history_tab(self):
        inspection_history_tab = QWidget()
        layout = QVBoxLayout(inspection_history_tab)

        topLayout = QHBoxLayout() # 상단 필터 및 검색 영역
        topLayout.addStretch(1)
        
        filter = QComboBox() # 필터링 드롭다운
        filter.addItem("전체")
        filter.addItem("Windows")
        filter.addItem("Linux")
        filter.setPlaceholderText("대상 OS 필터")
        filter.setFixedWidth(200)
        topLayout.addWidget(filter)

        search = QLineEdit() # 검색 필드
        search.setPlaceholderText("IP 주소 검색")
        search.setFixedWidth(200)
        topLayout.addWidget(search)

        layout.addLayout(topLayout)

        self.table = QTableWidget() # 테이블 생성
        self.table.setColumnCount(4) 
        self.table.setHorizontalHeaderLabels(["날짜", "대상 OS", "IP 주소", "상세 결과"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True) # 정렬 기능 활성화
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        self.LoadRecord() # 이력 불러오기

        return inspection_history_tab

    # [Func] LoadRecord
    # [DESC] 점검 이력을 불러오는 메서드
    # [TODO] db 연결
    # [ISSUE] None
    def LoadRecord(self):
        # 예시 데이터
        data = [
            {"date": "2024-01-01", "os": "Windows", "ip": "192.168.0.1"},
            {"date": "2024-01-02", "os": "Linux", "ip": "192.168.0.2"}
        ]
    
        for record in data:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
        
            # 날짜, 대상 OS, IP 주소 데이터 삽입
            self.table.setItem(row_position, 0, QTableWidgetItem(record['date']))
            self.table.setItem(row_position, 1, QTableWidgetItem(record['os']))
            self.table.setItem(row_position, 2, QTableWidgetItem(record['ip']))
        
            detail_result_btn = QPushButton('상세 결과') # '상세 결과' 버튼
            detail_result_btn.clicked.connect(lambda _, row=row_position: self.DetailResult(row))
        
            widget = QWidget() # 상세 결과 버튼 테이블에 배치
            btn_layout = QHBoxLayout(widget)
            btn_layout.addWidget(detail_result_btn)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            widget.setLayout(btn_layout)
        
            self.table.setCellWidget(row_position, 3, widget)
            
    # [Func] DetailResult
    # [DESC] 선택한 점검 이력의 상세 결과를 불러옴
    # [TODO] db 연결
    # [ISSUE] None      
    def DetailResult(self, row):
        # 선택된 행의 데이터 가져오기
        date = self.table.item(row, 0).text()  # 날짜
        os = self.table.item(row, 1).text()    # OS
        ip = self.table.item(row, 2).text()    # IP 주소

        dialog = QDialog(self) # 상세 결과 창
        dialog.setWindowTitle("상세 결과")
        dialog.resize(800, 600)
        layout = QVBoxLayout()

        header_label = QLabel(f"{date} | {os} | {ip}  점검 상세 결과") # 선택한 점검 이력의 정보 표시
        layout.addWidget(header_label)

        # 상세 점검 결과 테이블
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(5)
        self.detail_table.setHorizontalHeaderLabels(["점검 항목", "점검 내용", "결과 방식", "점검 결과", "세부 내용"])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
        # 예시 데이터
        data = [
            {"info": "백신 프로그램 업데이트", "description": "Windows Defender 백신 프로그램을 업데이트 합니다.", "result_type": "action", "result": "안전", "detail": True},
            {"info": "계정 잠금 임계값 변경", "description": "계정 잠금 임계값을 5로 설정", "result_type": "action", "result": "취약", "detail": True}
        ]
    
        for record in data:
            row_position = self.detail_table.rowCount()
            self.detail_table.insertRow(row_position)
        
            # 데이터 삽입
            self.detail_table.setItem(row_position, 0, QTableWidgetItem(record['info']))
            self.detail_table.setItem(row_position, 1, QTableWidgetItem(record['description']))
            self.detail_table.setItem(row_position, 2, QTableWidgetItem(record['result_type']))
            self.detail_table.setItem(row_position, 3, QTableWidgetItem(record['result']))
        
            detail_btn = QPushButton('세부 내용') # 세부 내용 버튼 배치
            detail_btn.clicked.connect(lambda _, row=row_position: self.ItemDetails(row))

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
    # [TODO] db 연결
    # [ISSUE] None    
    def ItemDetails(self, row):
        # 선택된 행의 데이터 가져오기
        info = self.detail_table.item(row, 0).text()  # 점검 항목
        description = self.detail_table.item(row, 1).text()     # 점검 내용
        result_type = self.detail_table.item(row, 2).text() # 결과 방식
        result = self.detail_table.item(row, 3).text()      # 점검 결과

        detail_dialog = QDialog(self)  # 세부 내용 창
        detail_dialog.setWindowTitle("세부 내용")
        detail_dialog.resize(800, 600)
        layout = QVBoxLayout()

        # 점검 항목
        info_label = QLabel("점검 항목")
        info_content = QLineEdit()
        info_content.setText(info)
        info_content.setReadOnly(True)
        layout.addWidget(info_label)
        layout.addWidget(info_content)

        # 점검 내용
        description_label = QLabel("점검 내용")
        description_content = QLineEdit()
        description_content.setText(description)
        description_content.setReadOnly(True)
        layout.addWidget(description_label)
        layout.addWidget(description_content)

        # 결과 방식
        result_type_label = QLabel("결과 방식")
        result_type_content = QLineEdit()
        result_type_content.setText(result_type)
        result_type_content.setReadOnly(True)
        layout.addWidget(result_type_label)
        layout.addWidget(result_type_content)

        # CommandName, CommandType, CommandString, 출력 메시지는 db에서 불러올 예정
        for label_text in ["CommandName", "CommandType", "CommandString", "출력 메시지"]:
            label = QLabel(label_text)
            content = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(content)

        # 점검 결과
        result_label = QLabel("점검 결과")
        result_content = QLineEdit()
        result_content.setText(result)
        result_content.setReadOnly(True)
        layout.addWidget(result_label)
        layout.addWidget(result_content)

        detail_dialog.setLayout(layout)
        detail_dialog.exec_()

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

        self.inspection_target_table.setColumnCount(5)
        self.inspection_target_table.setHorizontalHeaderLabels(['선택', '시스템 장치명', 'OS', '접속 방식', 'IP 주소'])
        self.inspection_target_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inspection_target_table.horizontalHeader().setStretchLastSection(True)
        
        
        self.inspection_list_table.setColumnCount(9)
        self.inspection_list_table.setHorizontalHeaderLabels(['선택', '운영체제', '이름', '설명', '실행 방식', '결과 방식', '삭제'])
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


        
        # 버튼 레이아웃 생성
        buttonLayout = QHBoxLayout()
        
        # 뒤로 가기 버튼 추가 및 버튼 레이아웃에 설정
        btnBack = QPushButton("<")
        btnBack.setFixedSize(30, 30)
        btnBack.clicked.connect(self.goBack)
        buttonLayout.addWidget(btnBack)  # 버튼 레이아웃에 뒤로 가기 버튼 추가

        # "점검 실행" 버튼 생성 및 버튼 레이아웃에 설정
        executeButton = QPushButton("점검 실행")
        executeButton.setFixedSize(100, 30)  # 버튼 크기 설정
        executeButton.clicked.connect(self.executeInspection)  # 클릭 시 executeInspection 메서드 호출
        
        # "규제 항목 추가" 버튼 생성 및 버튼 레이아웃에 설정
        add_btn = QPushButton("규제항목 추가") # '+' 버튼 생성 및 버튼 레이아웃에 설정
        add_btn.setFixedSize(30, 30)
        add_btn.clicked.connect(self.AddInspectionList) # 규제 지침 등록 창 열기
        buttonLayout.addWidget(add_btn)  # 버튼 레이아웃에 뒤로 가기 버튼 추가
        # 버튼을 가운데로 정렬하기 위해 빈 공간 추가
        buttonLayout.addStretch()
        buttonLayout.addWidget(executeButton)
        buttonLayout.addStretch()

        # 버튼 레이아웃을 메인 레이아웃에 추가하여 정렬
        layout.addLayout(buttonLayout)

        # 열 너비 설정
        self.inspection_list_table.setColumnWidth(0, 30)
        self.inspection_list_table.setColumnWidth(1, 210)
        self.inspection_list_table.setColumnWidth(2, 450)
        self.inspection_list_table.setColumnWidth(3, 90)
        self.inspection_list_table.setColumnWidth(4, 80)
        self.inspection_list_table.setColumnWidth(5, 30)
        
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

        for field, input_type in zip(fields, input_types):
            label = QLabel(field)
            if input_type == QTextEdit:  # TextEdit인 경우
                input_field = QScrollArea()  # 스크롤
                text_edit = QTextEdit()
                text_edit.setAcceptRichText(False)
                text_edit.setMinimumHeight(200)
                input_field.setWidget(text_edit)
                input_field.setWidgetResizable(True)
                self.input_fields[field] = text_edit  # QTextEdit을 딕셔너리에 저장
            else:
                input_field = input_type()
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
        save_btn.setFixedSize(40, 30)
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
        self.inspection_list_table.setItem(rowPosition, 1, QTableWidgetItem(input_values["TargetOS"]))
        self.inspection_list_table.setItem(rowPosition, 2, QTableWidgetItem(input_values["PluginName"]))
        self.inspection_list_table.setItem(rowPosition, 3, QTableWidgetItem(input_values["Description"]))
        self.inspection_list_table.setItem(rowPosition, 4, QTableWidgetItem(input_values["CommandType"]))
        self.inspection_list_table.setItem(rowPosition, 5, QTableWidgetItem(input_values["Result_Type"]))
        
        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        self.inspection_list_table.setCellWidget(rowPosition, 6, btnDelete)
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
        self.inspection_list_table.setCellWidget(rowPosition, 6, btnDelete)
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
        self.main_layout.addWidget(self.progressBar)  # main_layout에 프로그레스 바 추가

        
        self.progress_table = QTableWidget()

        self.progress_table.setColumnCount(5)
        self.progress_table.setHorizontalHeaderLabels(['시스템 장치명', '점검 항목', '점검 내용', '결과 방식', '점검 결과'])
        self.progress_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.progress_table.horizontalHeader().setStretchLastSection(True)
        
        self.main_layout.addWidget(self.progress_table)
        
        # 버튼 레이아웃 생성
        buttonLayout = QHBoxLayout()
        
        # 뒤로 가기 버튼 추가 및 버튼 레이아웃에 설정
        btnBack = QPushButton("<")
        btnBack.setFixedSize(30, 30)
        btnBack.clicked.connect(self.goBack)
        buttonLayout.addWidget(btnBack)  # 버튼 레이아웃에 뒤로 가기 버튼 추가

        # "홈으로" 버튼 생성 및 버튼 레이아웃에 설정
        homeButton = QPushButton("홈으로")
        homeButton.setFixedSize(50, 30)  # 버튼 크기 설정
        homeButton.clicked.connect(self.returnToHome)  # 클릭 시 returnToHome 메서드 호출
        buttonLayout.addWidget(homeButton)
        
        # "취소" 버튼 생성 및 버튼 레이아웃에 설정
        cancelButton = QPushButton("취소")
        cancelButton.setFixedSize(50, 30)  # 버튼 크기 설정
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
            self.progressBar.setValue(plugin_len)
            if len(result_data) != 0:
                self.addProgressTable(result_data)
            else:
                data = [None for i in range(plugin_len)]
                self.addProgressTable(data)
            
    def addProgressTable(self, result_data):
        
        # '시스템 장치명', '점검 항목', '점검 내용', '결과 방식', '점검 결과'
        # 나머지 데이터 추가
        for result in result_data:
            rowPosition = self.progress_table.rowCount()
            self.progress_table.insertRow(rowPosition)
            for i, data in enumerate(result):
                item = QTableWidgetItem(data)
                item.setFont(QFont("NanumBarunGothic", 8))  # 여기서 폰트와 크기 조절 가능
                item.setTextAlignment(Qt.AlignCenter)
                self.progress_table.setItem(rowPosition, i, item)
    
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