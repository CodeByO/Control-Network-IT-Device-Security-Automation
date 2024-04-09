# [Title] LoginWindow
# [DESC] 접속 정보 입력 위젯 생성
# [Writer] geonheek, yuu4172

import re
import os
import sys
import sqlite3
from pathlib import Path

from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QLineEdit, QApplication, QMainWindow, QTabWidget, QPushButton, QWidget, QTabBar, QMessageBox
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QTransform

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

# [Func] VulnerabilityCheckTab
# [DESC] 취약점 점검 탭 위젯 생성
# [TODO] 입력 화면, 규제 지침 조회/선택 화면, 진행/결과 화면 구현
# [ISSUE] None
def VulnerabilityCheckTab():
    """
    취약점 점검 탭 위젯 생성, 접속 정보 입력 UI 추가
    :return: 생성된 취약점 점검 탭 위젯
    """
    vulnerability_check_tab = QWidget()
    layout = QVBoxLayout(vulnerability_check_tab)
    
    # OS 선택 드롭다운
    OSTypeComboBox = QComboBox()
    OSTypeComboBox.addItem("대상 OS 선택") 
    OSTypeComboBox.addItem("Windows")
    OSTypeComboBox.addItem("Linux")
    OSTypeComboBox.setPlaceholderText("대상 OS 선택")  
    layout.addWidget(OSTypeComboBox)
    

    # 접속 방식 선택 드롭다운
    ConnectionTypeComboBox = QComboBox()
    ConnectionTypeComboBox.addItem("접속 방식 선택") 
    ConnectionTypeComboBox.addItem("SSH")
    ConnectionTypeComboBox.addItem("Samba")
    ConnectionTypeComboBox.setPlaceholderText("접속 방식 선택") 
    layout.addWidget(ConnectionTypeComboBox)
    
    # 시스템 IP 주소 입력
    ipLineEdit = QLineEdit()
    ipLineEdit.setPlaceholderText("시스템 IP 주소")  
    layout.addWidget(ipLineEdit)
    
    # 포트 번호 입력
    portLineEdit = QLineEdit()
    portLineEdit.setPlaceholderText("포트 번호")  
    layout.addWidget(portLineEdit)
    
    # ID 입력
    idLineEdit = QLineEdit()
    idLineEdit.setPlaceholderText("ID")
    layout.addWidget(idLineEdit)
    
    # Password 입력
    passwordLineEdit = QLineEdit()
    passwordLineEdit.setEchoMode(QLineEdit.Password)  
    passwordLineEdit.setPlaceholderText("Password")  
    layout.addWidget(passwordLineEdit)
    
    
    # '>' 버튼 추가
    nextButton = QPushButton(">")
    nextButton.setFixedSize(30, 30)
    nextButton.clicked.connect(lambda: onNextButtonClicked(OSTypeComboBox.currentText(), ConnectionTypeComboBox.currentText(), ipLineEdit.text(),portLineEdit.text(), idLineEdit.text(), passwordLineEdit.text()))  # '>' 버튼 클릭 시 호출될 함수
    
    # 버튼을 오른쪽으로 정렬하여 레이아웃에 추가
    layout.addWidget(nextButton, alignment=Qt.AlignRight)
    
    
    return vulnerability_check_tab

# onNextButtonClicked 함수 정의
def onNextButtonClicked(os_type, connection_type, ip, port, user_id, password):
    print(os_type, connection_type, ip, port, user_id, password)

def setupUI(main_window):
    # '>' 버튼 생성
    button = QPushButton(">")
    # 버튼 클릭 시 onNextButtonClicked 함수 호출
    # 여기서 os_type, connection_type, ip, port, id, password는 사용자 입력을 통해 얻은 값입니다.
    # 실제 사용 시 이 값들을 적절히 얻어와야 합니다. 예제에서는 임시 값으로 대체합니다.
    os_type = "Windows"
    connection_type = "SSH"
    ip = "192.168.0.1"
    port = 22
    user_id = "admin"
    password = "password"
    
    button.clicked.connect(lambda: onNextButtonClicked(os_type, connection_type, ip, port, user_id, password))
    
    layout = QVBoxLayout()
    layout.addWidget(button)
    
    central_widget = QWidget()
    central_widget.setLayout(layout)
    
    main_window.setCentralWidget(central_widget)


# 알림창을 띄우는 함수
def showAlert(message):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(message)
    msgBox.setWindowTitle("경고")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.exec_()

#GUI 애플리케이션에 대한 기본 객체
app = QApplication(sys.argv)

def onNextButtonClicked(os_type, connection_type, ip, port, id, password):
    """
    '>' 버튼 클릭 시 호출될 함수
    """
 
    if os_type == None or os_type == "대상 OS 선택":
        showAlert("점검할 OS를 선택해 주세요")
        return  # exit 대신 return 사용
        
    if connection_type == None or connection_type == "접속 방식 선택":
        showAlert("접속할 방식을 선택해 주세요")
        return
    ip_reg = r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'
    if not re.search(ip_reg, ip):
        showAlert("잘못된 형식의 IP 입니다")
        return

    if not port.isdigit():
        showAlert("숫자만 입력해 주세요")
        return

    id_reg = r'^[A-Za-z0-9_]{2,20}$'
    if not re.search(id_reg, id):
        showAlert("잘못된 형식의 ID 입니다")
        return
    
    passwd_reg = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$'
    if not re.search(passwd_reg, password):
        showAlert("잘못된 형식의 비밀번호 입니다")
        return
        
    path_src = Path(__file__)
    path_database = path_src.parent / "AutoInspection.db"
    
    if not os.path.exists(path_database):
        showAlert("DB가 존재하지 않습니다.")
        return

    VulnerabilityCheckTab()
    
    con = sqlite3.connect(path_database)
    cursor = con.cursor()

    try:
        cursor.execute("SELECT PluginName, Info, Description, CommandType, ResultType from InspectionTargets WHERE TargetOS=?", (os_type, )) # SQL 명령어 실행
    except (sqlite3.OperationalError, sqlite3.ProgrammingError):
        showAlert("DB 실행 에러")
        return
    
    inspection_targets = cursor.fetchall()
    
    if len(inspection_targets) == 0:
        showAlert("대상 OS에 해당하는 규제 지침이 없습니다. 추가해주세요")
        return
        
    print(inspection_targets)
    
    
    con.close() # DB 연결 종료
    
    # 규제 지침 선택 화면 함수를 호출할 시 inspection_targets 를 인자로 주기 -> 작업 필요
    # inspection_target에 있는 내용으로 체크 박스 선택 화면 구현 -> 작업 필요
    
    showAlert("규제 지침 선택 화면으로 넘어가는 로직 구현")

# [Func] InspectionHistoryTab
# [DESC] 점검 이력 조회 탭 위젯 생성
# [TODO] 점검 이력 조회 화면 구현
# [ISSUE] None
def InspectionHistoryTab():
    """
    점검 이력 조회 탭 위젯 생성
    :return: 생성된 점검 이력 조회 탭 위젯
    """
    inspection_history_tab = QWidget()
    return inspection_history_tab

# [Func] SetUpTabs
# [DESC] 애플리케이션 내 탭 위젯 구성 및 스타일 설정
# [TODO] 탭별 추가 기능 구현
# [ISSUE] None
def SetUpTabs():
    """
    애플리케이션 내 탭 위젯의 구성
    :return: 구성된 QTabWidget 객체
    """
    # 탭 위젯 구성
    tab_widget = QTabWidget()
    tab_widget.setTabBar(VerticalTabWidget()) 
    vulnerability_check_tab = VulnerabilityCheckTab()
    inspection_history_tab = InspectionHistoryTab()
    tab_widget.addTab(vulnerability_check_tab, "취약점\n점검")
    tab_widget.addTab(inspection_history_tab, "점검 이력\n조회")
    tab_widget.setTabPosition(QTabWidget.West)
    
    # 탭 위젯 스타일 설정
    tab_widget.setStyleSheet("""
        QTabBar::tab {
            height: 80px; /* 탭의 높이 조정 */
            width: 100px; /* 탭의 너비 조정 */ 
            } 
        """)
    return tab_widget

# [Func] main
# [DESC] 애플리케이션 메인 함수
# [TODO] None
# [ISSUE] None
def main():
    """
    애플리케이션의 메인 함수(애플리케이션의 초기 설정 실행)
    """
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle('취약점 점검 시스템')
    main_window.setGeometry(260, 150, 800, 500)

    setupUI(main_window)

    tab_widget = SetUpTabs()
    main_window.setCentralWidget(tab_widget)
    main_window.show()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main()