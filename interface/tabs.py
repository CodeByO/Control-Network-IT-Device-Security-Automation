import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget

# [Func] VulnerabilityCheckTab
# [DESC] 취약점 점검 탭 위젯 생성
# [TODO] 입력 화면, 규제 지침 조회/선택 화면, 진행/결과 화면 구현
# [ISSUE] None
def VulnerabilityCheckTab():
    """
    취약점 점검 탭 위젯 생성
    :return: 생성된 취약점 점검 탭 위젯
    """
    vulnerability_check_tab = QWidget()
    return vulnerability_check_tab

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
# [ISSUE] 탭 레이블 회전
def SetUpTabs():
    """
    애플리케이션 내 탭 위젯의 구성
    :return: 구성된 QTabWidget 객체
    """
    # 탭 위젯 구성
    tab_widget = QTabWidget()
    vulnerability_check_tab = VulnerabilityCheckTab()
    inspection_history_tab = InspectionHistoryTab()
    tab_widget.addTab(vulnerability_check_tab, "취약점\n점검")
    tab_widget.addTab(inspection_history_tab, "점검 이력\n조회")
    tab_widget.setTabPosition(QTabWidget.West)
    
    # 탭 위젯 스타일 설정
    tab_widget.setStyleSheet("""
        QTabBar::tab {
            height: 80px; /* 탭의 높이 조정 */
            width: 70px; /* 탭의 너비 조정 */ 
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

    tab_widget = SetUpTabs()
    main_window.setCentralWidget(tab_widget)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()