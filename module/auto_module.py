# [TITLE] 점검 모듈
# [DESC] 작성된 XML 스크립트를 이용하여 서버에 원격 접속 후 자동으로 취약점 점검하는 프로그램
# [Writer] CodeByO

import os
import sys
import signal
import subprocess
from pathlib import Path
from datetime import datetime


from smb.SMBConnection import SMBConnection
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import (
    SSHException,
    AuthenticationException,
    BadHostKeyException,
    NoValidConnectionsError
)

import xml.etree.ElementTree as ET

import sqlite3

# [Func] ConnectTarget
# [DESC] 보안 취약점 점검 대상 PC에 접속
# [TODO] 각 인자에 맞게 코드 구현
# [ISSUE] 1. sh를 통한 windows 연결, samba 통한 linux 연결 고려해야함
#         2. 예외처리 수정 및 추가 해야함
def ConnectTarget(ip:str, port:str, connection_type:str, username:str, password:str, servername:str = "")->classmethod:
    """
    보안 취약점 점검 대상 PC에 접속
    :param ip: 
        접속하고자 하는 대상 PC 주소
    :param port: 
        접속하고자 하는 포트 번호
    :param connection_type: 
        접속 프로토콜 지정 (ssh or samba)
    :param username: 
        접속을 위한 계정 이름
    :param password: 
        접속을 위한 비밀번호
    :param servername: 
        samba 연결을 위한 서버 컴퓨터 이름
    :return:
        각 접속 프로토콜 클래스 or None
    """
    if connection_type == "ssh":
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(hostname=ip, username=username, password=password, port=port, timeout=5.0)
            return ssh
        except (BadHostKeyException, AuthenticationException, OSError, NoValidConnectionsError, SSHException):
            return None
    elif connection_type == "samba":
        conn = SMBConnection(username, password, 'auto_inspection', servername, 'WORKGROUP', use_ntlm_v2=True)
        try:
            result = conn.connect(ip, port)
        except OSError:
            return None
        finally:
            if result:
                return conn
            else:
                return None

# [Func] ParseXml
# [DESC] XML 스크립트 로드 및 정리
# [TODO] 예외 처리 추가
# [ISSUE] None
def ParseXml(target:str, plugin_name: list)->list:
    """
    XML 스크립트 로드 및 정리
    출처 : https://king-rabbit.github.io/python/xml-parsing/
    
    :param target: 
        점검하고자 하는 운영체제(Windows or Linux)
    :param plugin_name: 
        UI에서 점검하고자 선택한 점검 항목 리스트
    :return: 
        XML 파일에서 파싱한 dict 데이터 리스트
    """
    path_src = Path(__file__)
    path_script = path_src.parent.parent / 'script'
    script_files = os.listdir(path_script)
    inspection_lists = []
    for script_file in script_files:
        script_path = path_script / script_file
        if script_path.suffix.lower() == ".xml":
            # xml 파일 불러오기
            tree = ET.parse(script_path)
            root = tree.getroot()
            target_os = root.find('TargetOS').text
            name = root.attrib.get('name')
            if target_os == target and name in plugin_name:
                
                # Result_Type 가져오기
                result_type = root.find('Result_Type').text
                print("Result_Type:", result_type)

                # Commands 추출하여 딕셔너리로 정리
                commands_dict = {}
                commands = root.find('Commands')
                command_count = commands.find('CommandCount').text
                for command in commands.findall('Command'):
                    command_name = command.find('CommandName').text
                    command_type = command.find('CommandType').text
                    command_string = command.find('CommandString').text
                    commands_dict[command_name] = {
                        'PluginName': name,
                        'ResultType': result_type,
                        'CommandCount': command_count,
                        'CommandType': command_type,
                        'CommandString': command_string
                    }
        inspection_lists.append(commands_dict)
    return inspection_lists

# [Func] InspectionAutomation
# [DESC] 정리된 스크립트를 이용하여 보안 취약점 점검
# [TODO] 기능 구현
# [ISSUE] None
def InspectionAutomation(target_os:str, ip:str, port:str, connection_type:str, username:str, password:str, plugin_list:list):
    '''
    점검 실행
    :param target_os: 
        접속하고자 하는 운영체제(Windows or Linux)
    :param ip: 
        접속하고자 하는 대상 PC 주소
    :param port: 
        접속하고자 하는 포트 번호
    :param connection_type: 
        접속 프로토콜 지정 (ssh or samba)
    :param username: 
        접속을 위한 계정 이름
    :param password: 
        접속을 위한 비밀번호
    :param plugin_list: 
        선택한 plugin 문자열 리스트 (ex, ['Anti_Virus_Update', 'Change_Account_Lockout_Threshold'])
    :return: 
        0(성공), 1(대상 접속 실패), 2(점검 실패) - 미확정

    '''
    session = ConnectTarget(target_os, ip, port, connection_type, username, password)
    
    # 예시, 원격 연결에 문제가 생겼다면 1, 점검에 문제가 발생하면 2
    if session is None:
        return 1
    
    # Result_Type - action, info, registry
    # CommandType - Powershell, cmd, terminal
    
    inspection_lists = ParseXml(connection_type, plugin_list)
    for command in inspection_lists:
        plugin_name = command.get("PluginName")
        result_type = command.get("ResultType")
        command_count = int(command.get("CommandCount"))
        command_type = command.get("CommandType")
        command_string = command.get("CommandString")
        print(plugin_name)
        print(result_type)
        for _ in range(command_count):
            if connection_type == "ssh":
                stdin, stdout, stderr = session.exec_command(command_string)
            elif connection_type == "samba":
                pass
        inspection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(inspection_time)
        print(stdout.read().decode('euc-kr'))
        
    # 세션 종료 시 사용(ssh, samba 동일)
    session.close()

    # UI에서 점검 실행 시 아래 코드 사용
    # process_info = Thread(target=InspectionAutomation, args=(arguments,))
    # process_info.start()
    
    # SQLite 사용 방법
    # con = sqlite3.connect("")
    # cursor = con.cursor()
    # insert_data = f"INSERT INTO table VALUES({""},{""},{""})"
    # cursor.execute(insert_data)
    # con.commit()
    # con.close()


if __name__ == '__main__':
    # 특정 signal 입력 시 수행하는 동작 정의
    def SignalHandler(sig, frame):
        pass

    # SIGINT(Ctrl + C) 입력시 singal_handler 실행
    signal.signal(signal.SIGINT, SignalHandler)