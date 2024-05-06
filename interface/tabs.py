# [Title] LoginWindow
# [DESC] 접속 정보 입력 위젯 생성
# [Writer] geonheek, yuu4172 

import re
import os
import sys
import sqlite3
from pathlib import Path

from PyQt5.QtWidgets import (QVBoxLayout, QComboBox, QLineEdit, QApplication, QMainWindow,
 QTabWidget, QPushButton, QWidget, QTabBar, QMessageBox, QStackedWidget,
 QCheckBox, QTableWidget, QHeaderView, QHBoxLayout, QTableWidgetItem)
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QTransform

sys.path.append(os.path.dirname( os.path.dirname( os.path.abspath(__file__) ) ))

from module.auto_module import InspectionAutomation

path_src = Path(__file__)
path_database = path_src.parent / "AutoInspection.db"

inspection_targets = list()
set_os_type = None
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
# [ISSUE] None
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
        self.setGeometry(260, 150, 800, 500)

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
        layout = QVBoxLayout(vulnerability_check_tab)
        OSTypeComboBox = QComboBox()
        OSTypeComboBox.addItem("대상 OS 선택") 
        OSTypeComboBox.addItem("Windows")
        OSTypeComboBox.addItem("Linux")
        OSTypeComboBox.setPlaceholderText("대상 OS 선택")  
        layout.addWidget(OSTypeComboBox)

        ConnectionTypeComboBox = QComboBox()
        ConnectionTypeComboBox.addItem("접속 방식 선택") 
        ConnectionTypeComboBox.addItem("SSH")
        ConnectionTypeComboBox.addItem("Samba")
        ConnectionTypeComboBox.setPlaceholderText("접속 방식 선택") 
        layout.addWidget(ConnectionTypeComboBox)

        ipLineEdit = QLineEdit()
        ipLineEdit.setPlaceholderText("시스템 IP 주소")  
        layout.addWidget(ipLineEdit)

        portLineEdit = QLineEdit()
        portLineEdit.setPlaceholderText("포트 번호")  
        layout.addWidget(portLineEdit)

        idLineEdit = QLineEdit()
        idLineEdit.setPlaceholderText("ID")
        layout.addWidget(idLineEdit)

        passwordLineEdit = QLineEdit()
        passwordLineEdit.setEchoMode(QLineEdit.Password)  
        passwordLineEdit.setPlaceholderText("Password")  
        layout.addWidget(passwordLineEdit)

        nextButton = QPushButton(">")
        nextButton.setFixedSize(30, 30)
        nextButton.clicked.connect(lambda: self.on_next_button_clicked(OSTypeComboBox.currentText(), ConnectionTypeComboBox.currentText(), ipLineEdit.text(), portLineEdit.text(), idLineEdit.text(), passwordLineEdit.text()))
        layout.addWidget(nextButton, alignment=Qt.AlignRight)
        return vulnerability_check_tab

    # [Func] create_inspection_history_tab
    # [DESC] 점검 이력 조회 탭을 생성하는 메서드
    # [TODO] 구현해야 함
    # [ISSUE] None
    def create_inspection_history_tab(self):
        return QWidget()

    # [Func] on_next_button_clicked
    # [DESC] 다음 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None
    def on_next_button_clicked(self, os_type, connection_type, ip, port, id, password):
        """
        다음 버튼 클릭 시 호출되는 메서드
        :param os_type: 대상 운영체제
        :param connection_type: 접속 방식
        :param ip: 시스템 IP 주소
        :param port: 포트 번호
        :param id: ID
        :param password: Password
        """
        # os_type = "Windows"
        # connection_type = "SSH"
        # ip = "192.168.0.1"
        # port = "22"
        # id = "admin"
        # password = "password"

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
        
        # ID 형식 검사
        id_reg = r'^[A-Za-z0-9_]{2,20}$'
        if not re.search(id_reg, id):
            self.ShowAlert("잘못된 형식의 ID 입니다")
            return

        # 비밀번호 형식 검사
        passwd_reg = r'^(?=.*[A-Za-z\dㄱ-ㅣ가-힣])[A-Za-z\dㄱ-ㅣ가-힣]{4,}$'
        if not re.search(passwd_reg, password):
            self.ShowAlert("잘못된 형식의 비밀번호 입니다")
            return
        
        # 대상 OS에 대한 검사 목록 초기화 및 확인
        global inspection_targets
        global set_os_type
        if len(inspection_targets) == 0 or set_os_type != os_type:
            global path_database
            set_os_type = os_type
            if not os.path.exists(path_database):
                self.ShowAlert("DB가 존재하지 않습니다.")
                return

            con = sqlite3.connect(path_database)
            cursor = con.cursor()

            try:
                cursor.execute("SELECT TargetID, PluginName, Info, Description, CommandType, ResultType from InspectionTargets WHERE TargetOS=? AND DeleteFlag=0", (os_type, ))
            except (sqlite3.OperationalError, sqlite3.ProgrammingError):
                self.ShowAlert("DB 실행 에러")
                return

            inspection_targets = cursor.fetchall()
            con.close()
            if len(inspection_targets) == 0:
                self.ShowAlert("대상 OS에 해당하는 규제 지침이 없습니다. 추가해주세요")
                return
        
        self.inspection_list_page.SetData(inspection_targets)
        self.inspection_list_page.SetTarget(os_type, connection_type, ip, port, id, password)
        self.stackedWidget.addWidget(self.inspection_list_page)
        self.stackedWidget.setCurrentIndex(1)
        
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

class InspectionListPage(QWidget):

    # [Func] __init__
    # [DESC] 점검 목록 페이지 클래스 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def __init__(self, stackedWidget):
        super(InspectionListPage, self).__init__()
        
        self.stackedWidget = stackedWidget
        
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setHorizontalHeaderLabels(['선택', '이름', '설명', '실행 방식', '결과 방식', '삭제'])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.os_type = None
        self.connection_type = None
        self.ip = None
        self.port = None
        self.id = None
        self.password = None
        
        self.initUI()
    
    # [Func] initUI
    # [DESC] UI 초기화 메서드
    # [TODO] None
    # [ISSUE] None
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.tableWidget)

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
       
        # 버튼을 가운데로 정렬하기 위해 빈 공간 추가
        buttonLayout.addStretch()
        buttonLayout.addWidget(executeButton)
        buttonLayout.addStretch()

        # 버튼 레이아웃을 메인 레이아웃에 추가하여 정렬
        layout.addLayout(buttonLayout)
            
    # [Func] goBack
    # [DESC] 뒤로 가기 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None        
    def goBack(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.stackedWidget.setCurrentIndex(0)  # 첫 번째 페이지로 돌아가기
        
    # [Func] executeInspection
    # [DESC] 점검 실행 버튼 클릭 이벤트 핸들러
    # [TODO] None
    # [ISSUE] None
    def executeInspection(self):
        plugin_dict = {}
        for row in range(self.tableWidget.rowCount()):
            chkBoxWidget = self.tableWidget.cellWidget(row, 0)
            chkBox = chkBoxWidget.findChild(QCheckBox)
            if chkBox.isChecked():
                plugin_dict[self.tableWidget.item(row, 6).text()] = int(self.tableWidget.item(row, 7).text())
        InspectionAutomation(self.os_type, self.ip, self.port, self.connection_type, self.id, self.password, plugin_dict)
    
    # [Func] addRow
    # [DESC] 테이블에 새로운 행 추가
    # [TODO] None
    # [ISSUE] None
    def addRow(self, TargetID, plugin, name, description, tool, action):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

        # 체크박스 추가
        chkBoxWidget = QWidget()
        chkBox = QCheckBox()
        chkBoxLayout = QHBoxLayout(chkBoxWidget)
        chkBoxLayout.addWidget(chkBox)
        chkBoxLayout.setAlignment(Qt.AlignCenter)
        chkBoxLayout.setContentsMargins(0,0,0,0)
        self.tableWidget.setCellWidget(rowPosition, 0, chkBoxWidget)
        # 나머지 데이터 추가
        self.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(name))
        self.tableWidget.setItem(rowPosition, 2, QTableWidgetItem(description))
        self.tableWidget.setItem(rowPosition, 3, QTableWidgetItem(tool))
        self.tableWidget.setItem(rowPosition, 4, QTableWidgetItem(action))
        # 삭제 버튼 추가
        btnDelete = QPushButton("삭제")
        btnDelete.clicked.connect(lambda: self.deleteRow(btnDelete))
        self.tableWidget.setCellWidget(rowPosition, 5, btnDelete)
        self.tableWidget.setItem(rowPosition, 6, QTableWidgetItem(plugin))
        self.tableWidget.setColumnHidden(6, True)
        self.tableWidget.setItem(rowPosition, 7, QTableWidgetItem(str(TargetID)))
        self.tableWidget.setColumnHidden(7, True)

    # [Func] deleteRow
    # [DESC] 선택한 행을 삭제하는 메서드
    # [TODO] None
    # [ISSUE] None
    def deleteRow(self, button):
        index = self.tableWidget.indexAt(button.pos())
        if index.isValid():
            self.tableWidget.removeRow(index.row())
            target_id = self.tableWidget.item(index.row(), 7).text()
            global inspection_targets
            global path_database
            con = sqlite3.connect(path_database)
            cursor = con.cursor()
            cursor.execute("SELECT TargetID from InspectionTargets WHERE TargetID=", (target_id, ))
            
            target_index = cursor.fetchone()
            target_index = target_index[0]
            
            inspection_targets.pop(target_index)
            
            cursor.execute("UPDATE from InsectionTargets SET DeleteFlag=1 WHERE TargetID=?", (target_id, ))
            
            con.close()

    # [Func] SetData
    # [DESC] 테이블에 점검 데이터를 설정하는 메서드
    # [TODO] None
    # [ISSUE] None
    def SetData(self, inspection_data):
        for item in inspection_data:
            self.addRow(item[0], item[1], item[2], item[3], item[4], item[5])
    
    # [Func] SetTarget
    # [DESC] 대상 OS 및 접속 정보를 설정하는 메서드
    # [TODO] None
    # [ISSUE] None
    def SetTarget(self, os_type, connection_type, ip, port, id, password):
        self.os_type = os_type
        self.connection_type = connection_type
        self.ip = ip
        self.port = port
        self.id = id
        self.password = password
    
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