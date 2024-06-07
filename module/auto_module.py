# [TITLE] 점검 모듈
# [DESC] 작성된 XML 스크립트를 이용하여 서버에 원격 접속 후 자동으로 취약점 점검하는 프로그램
# [Writer] CodeByO

import os
from datetime import datetime
from tqdm import tqdm
import signal
import select
from smb.SMBConnection import SMBConnection, OperationFailure, NotConnectedError, NotReadyError, ProtocolError
from paramiko import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import (
    SSHException,
    AuthenticationException,
    BadHostKeyException,
    NoValidConnectionsError
)
from bs4 import BeautifulSoup as bf
import xml.etree.ElementTree as ET

import sqlite3

path_src = os.path.abspath(__file__)

# [Func] ConnectTarget
# [DESC] 보안 취약점 점검 대상 PC에 접속
# [TODO] 예외처리 추가
# [ISSUE] None
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
        samba 연결을 위한 서버 컴퓨터 이름 (리눅스는 불필요 하지만 윈도우는 필요)
    :return:
        각 접속 프로토콜 클래스 or None
    """
    if connection_type == "SSH":
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        try:
            ssh.connect(hostname=ip, username=username, password=password, port=int(port), timeout=10.0)
            return ssh
        except (BadHostKeyException, AuthenticationException, OSError, NoValidConnectionsError, SSHException) as e:
            return None
    elif connection_type == "Samba":
        conn = SMBConnection(username, password, 'auto_inspection', servername, 'WORKGROUP', use_ntlm_v2=True)
        try:
            result = conn.connect(ip, port)
        except (NotConnectedError, OSError, NotReadyError, ProtocolError):
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
def ParseXml(target_os:str, plugin_dict : dict)->list:
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
    path_script = os.path.join(os.path.dirname(os.path.dirname(path_src)), 'script')
    script_files = os.listdir(path_script)
    inspection_lists = []
    for script_file in script_files:
        script_path = os.path.join(path_script, script_file)
        if script_file.lower().endswith(".xml"):
            with open(script_path, 'r', encoding='utf-8') as file:
                xmlstring = file.read()
            soup = bf(xmlstring, features="xml")
            try:
                target = soup.find('TargetOS').text
                name = soup.find('Plugin').get('name')
                if target == target_os and name in plugin_dict.keys():
                    result_type = soup.find('Result_Type').text
                    commands_dict = {}
                    plugin_value = plugin_dict.get(name)
                    info = soup.find('Plugin').find("Info").text
                    description = soup.find('Plugin').find("Description").text
                    commands = soup.find('Plugin').find("Commands")
                    command_count = commands.find('CommandCount').text
                    for command in commands.find_all('Command'):
                        command_type = command.find('CommandType').text
                        command_string = command.find('CommandString').text
                        commands_dict[plugin_value[1]] = {
                            'PluginName': name,
                            'Info' : info,
                            'Description' : description,
                            'ResultType': result_type,
                            'CommandCount': command_count,
                            'CommandType': command_type,
                            'CommandString': command_string
                        }
                    inspection_lists.append(commands_dict)
            except AttributeError:
                continue
            
    
    return inspection_lists


# [Func] InspectionAutomation
# [DESC] 정리된 스크립트를 이용하여 보안 취약점 점검
# [TODO] result 타입에 따라 실행 구분 및 action 타입에 점검 항목이 정상적으로 동작하는지 파악
# [ISSUE] None
def InspectionAutomation(target_name:str, target_os:str, connection_type:str, ip:str, port:str, username:str, password:str, plugin_dict:dict):
    '''
    점검 실행
    :param target_name: 
        접속하고자 하는 점검 대상 이름
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
        선택한 규제 항목의 TargetID와 PluginName 딕셔너리 (ex, {1 : 'Anti_Virus_Update',  2: 'Change_Account_Lockout_Threshold'})
    :return: 
        0(성공), 1(대상 접속 실패), 2(점검 실패), 3(데이터베이스 접속 에러) - 미확정

    '''
    
    # # 특정 signal 입력 시 수행하는 동작 정의
    # def signal_handler(sig, frame):
    #     global interrupt_flag
    #     interrupt_flag = False

    # # SIGINT(Ctrl + C) 입력시 singal_handler 실행
    # signal.signal(signal.SIGINT, signal_handler)
    session = ConnectTarget(ip, port, connection_type, username, password)
    
    # 예시, 원격 연결에 문제가 생겼다면 1, 점검에 문제가 발생하면 2
    if session is None:
        return 1, []
    
    # Result_Type - action, info, registry
    # CommandType - Powershell, cmd, terminal
    path_database = os.path.join(os.path.dirname(os.path.dirname(path_src)), "interface", "AutoInspection.db")
   
    if os.path.exists(path_database):
        con = sqlite3.connect(path_database)
    else:
        session.close()
        return 3, []
    
    
    inspection_lists = ParseXml(target_os, plugin_dict)
    cursor = con.cursor()
    cursor.execute("INSERT INTO InspectionItems(TargetName, OSType, ConnectionType, IPAddress, PortNumber, RemoteID) VALUES(?,?,?,?,?,?)", (target_name, target_os, connection_type, ip, int(port), username))
    con.commit()
    
    items_id = cursor.lastrowid
    #items_id = 1
    result_data = list()
    for command in inspection_lists:
        inspection_status = 0
        for key, value in command.items():
            target_id = key
            plugin_name = value['Info']
            description = value['Description']
            result_type = value['ResultType']
            command_count = int(value['CommandCount'])
            command_type = value['CommandType']
            command_string = str(value['CommandString'])
        stdout, stderr = None, None
        if connection_type == "SSH":
            stdin, stdout, stderr = session.exec_command(command_string)
            stdout = stdout.read().decode('euc-kr').strip()
            stderr = stderr.read().decode('euc-kr').strip()

            if stdout is not None:  # stdout 변수가 None이 아닌지 확인
                if result_type == "action":
                    if 'True' in stdout:
                        inspection_status = 1
                        inspection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cursor.execute("INSERT INTO InspectionResults(TargetID, ItemsID, InspectionStatus, InspectionOutput, InspectionError, InspectionDate) VALUES(?,?,?,?,?,?)", (target_id, items_id, inspection_status, stdout, stderr, inspection_date))
                        con.commit()
                        result_id = cursor.lastrowid
                        #result_id = 1
                        result_data.append([result_id, target_name, plugin_name, description, result_type, inspection_status] )
                        stdout = None
                elif result_type == "info" and len(stderr) == 0:
                    inspection_status = 1
                    inspection_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO InspectionResults(TargetID, ItemsID, InspectionStatus, InspectionOutput, InspectionError, InspectionDate) VALUES(?,?,?,?,?,?)", (target_id, items_id, inspection_status, stdout, stderr, inspection_date))
                    con.commit()
                    result_id = cursor.lastrowid
                    #result_id = 1
                    result_data.append([result_id, target_name, plugin_name, description, result_type, inspection_status] )
                    stdout = None
                elif result_type == "registry" and len(stderr) == 0:
                    if stderr is not None:
                        inspection_status = 1
            else:
                inspection_status = 0
        elif connection_type == "samba":
            try:
                if result_type == "action":
                    if 'True' in stdout:
                        inspection_status = 1
                elif result_type == "info":
                    inspection_status = 1
                elif result_type == "registry":
                    inspection_status = 1
            except OperationFailure:
                pass
        
    
    con.close()
    # 세션 종료 시 사용(ssh, samba 동일)
    session.close()
    return 0, result_data