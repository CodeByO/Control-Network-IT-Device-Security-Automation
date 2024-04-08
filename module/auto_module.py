# [TITLE] 점검 모듈
# [DESC] 작성된 XML 스크립트를 이용하여 서버에 원격 접속 후 자동으로 취약점 점검하는 프로그램
# [Writer] CodeByO

import os
import sys
import signal
import subprocess
from pathlib import Path
from datetime import datetime
from netmiko import ConnectHandler
from smb.SMBConnection import SMBConnection
import telnetlib
import netmiko
import serial

import xml.etree.ElementTree as ET

import sqlite3

'''
from netmiko import ConnectHandler

cisco_881 = {
    'device_type': 'cisco_ios',
    'host':   '10.10.10.10',
    'username': 'test',
    'password': 'password',
    'port' : 8022,          # optional, defaults to 22
    'secret': 'secret',     # optional, defaults to ''
}

net_connect = ConnectHandler(**cisco_881)

output = net_connect.send_command('show ip int brief')
print(output)

'''
'''
import telnetlib

HOST = "192.168.1.1"

user = 'cisco'
password = 'cisco'

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Username: ")
tn.write(user.encode('ascii') + b"\n")
tn.read_until(b"Password: ")
tn.write(password.encode('ascii') + b"\n")

tn.write(b'terminal length 0\r\nsh version\n')
tn.write(b"exit\n")

print(tn.read_all().decode('ascii'))

'''
'''
import serial

#시리얼포트 객체 ser을 생성
#pc와 스위치 시리얼포트 접속정보
ser = serial.Serial(
    port = 'COM7', 
    baudrate=9600, 
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=8
    )

#시리얼포트 접속
ser.isOpen()

#시리얼포트 번호 출력
print(ser.name)

'''
''' samba
from smb.SMBConnection import SMBConnection
import smb
# Samba 서버 연결 정보 설정
server_name = 'testbed'
server_ip = '172.22.191.219'
server_share = 'Users'
user_name = 'etri'
password = '3070'
domain_name = 'WORKGROUP'  # Samba 서버의 도메인 이름 (일반적으로 WORKGROUP)

# Samba 서버에 연결
conn = SMBConnection(user_name, password, 'pysmb_test', server_name, domain=domain_name, use_ntlm_v2=True)
conn.connect(server_ip, 139)

# 공유 폴더 내의 파일 및 디렉토리 목록 가져오기
file_list = conn.listPath(server_share, '/')
for f in file_list:
    print(f.filename)

# 연결 종료
conn.close()

'''
# [Func] ConnectTarget
# [DESC] 보안 취약점 점검 대상 PC에 접속
# [TODO] 각 인자에 맞게 코드 구현
# [ISSUE] 1. sh를 통한 windows 연결, samba 통한 linux 연결 고려해야함
#         2. 예외처리 수정 및 추가 해야함
def ConnectTarget(ip:str, protocol:str, type:str):
    """
    보안 취약점 점검 대상 PC에 접속
    :param ip: 접속하고자 하는 대상 PC 주소
    :param protocol: 접속하고자 하는 프로토콜 (ssh or samba)
    :param type: 접속 프로토콜 지정 (linux or windows)
    :return: Not Yet
    """
    if type == "linux":
        if protocol == "ssh":
            # SSH 접속 로직 (예: netmiko 사용)
            device = {
                'device_type': 'linux',
                'host': ip,  # 리눅스 서버 IP 주소
                'username': '',  # 사용자 이름
                'password': '',  # 비밀번호
                'port': 22,  # 기본값은 22, 다른 포트를 사용하는 경우 변경
                'secret': '',
            }

            # SSH 연결
            try:
                net_connect = ConnectHandler(**device, timeout=100)
                net_connect.enable()
                print(f"Successfully connected to {device['host']}")

                # 명령 실행 예: 'ls'
                output = net_connect.send_command('ls')
                print(output)
                return net_connect
            except ValueError as e:
                print(f"Failed to connect to {ip}: {str(e)}")
            except ImportError as e:
                print(f"필요한 모듈을 찾을 수 없습니다: {str(e)}. 'pip install netmiko'을 실행하여 설치해주세요.")
            except KeyboardInterrupt:
                print("강제 종료 되었습니다.")
            except UnboundLocalError as e:
                print(f"잘못된 ip를 입력하셨습니다: {str(e)}.")
            except Exception as e:
                print(f"An unexpected error occurred while connecting to {device['host']}: {str(e)}")

            finally:
                # 연결 종료
                net_connect.disconnect()
        elif protocol == "smb":
            '''
            # Samba 접속 로직 (예: smbprotocol 사용)
            # Samba 서버 연결 정보 설정
            server_name = ''
            server_ip = ip
            server_share = ''
            user_name = ''
            password = ''

            # Samba 서버에 연결
            conn = SMBConnection(user_name, password, 'pysmb_test', server_name, use_ntlm_v2=True)
            conn.connect(server_ip, 139)

            # 공유 폴더 내의 파일 및 디렉토리 목록 가져오기
            file_list = conn.listPath(server_share, '/')
            for f in file_list:
                print(f.filename)

            # 연결 종료
            conn.close()
        else:
            raise ValueError("Invalid protocol. Supported protocols: 'ssh', 'smb'")
            '''
    elif type == "windows":
        if protocol == "ssh":
            '''
            # 윈도우에 SSH 연결
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, password=password, port=ssh_port, timeout=timeout)
            print(f"Successfully connected to {host} via SSH (Windows)")
            return ssh
            '''
        elif protocol == "smb":
            # 윈도우에 SMB 연결
            # Samba 접속 로직 (예: smbprotocol 사용)
            # Samba 서버 연결 정보 설정
            server_name = ''
            server_ip = ip
            server_share = ''
            user_name = ''
            password = ''

            try:
                # Samba 서버에 연결
                conn = SMBConnection(user_name, password, 'pysmb_test', server_name, use_ntlm_v2=True)
                conn.connect(server_ip, 139)

                # 공유 폴더 내의 파일 및 디렉토리 목록 가져오기
                file_list = conn.listPath(server_share, '/')
                for f in file_list:
                    print(f.filename)
                return conn
            except ValueError as e:
                return print(f"Failed to connect to {ip}: {str(e)}")
            except ImportError as e:
                return print(f"필요한 모듈을 찾을 수 없습니다: {e}. 'pip install smbprotocol'을 실행하여 설치해주세요.")

            except Exception as e:
                print(f"An unexpected error occurred while connecting to {server_ip}: {str(e)}")
                return None
            finally:
                # 연결 종료
                conn.close()
        else:
            raise ValueError("Invalid protocol. Supported protocols: 'ssh', 'smb'")
    else:
        raise ValueError("Invalid OS type. Supported types: 'linux', 'windows'")
    return None

# 사용 예시
# ConnectTarget("xxx.xxx.xxx.xxx", "ssh", "linux")
# ConnectTarget("xxx.xxx.xxx.xxx", "smb", "windows")


# [Func] ParseXml
# [DESC] XML 스크립트 로드 및 정리
# [TODO] 예외 처리 추가
# [ISSUE] None
def ParseXml(target:str, plugin_name: list)->list:
    """
    XML 스크립트 로드 및 정리
    출처 : https://king-rabbit.github.io/python/xml-parsing/
    
    :param target: 점검하고자 하는 운영체제(Windows or Linux)
    :param plugin_name: UI에서 점검하고자 선택한 점검 항목 리스트
    :return: XML 파일에서 파싱한 dict 데이터 리스트
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
def InspectionAutomation(target_os:str, ip:str, port:str, type:str, username:str, password:str, plugin_list:list):
    '''
    점검 실행
    :param target_os: 접속하고자 하는 운영체제(Windows or Linux)
    :param ip: 접속하고자 하는 대상 PC 주소
    :param port: 접속하고자 하는 포트 번호
    :param type: 접속 프로토콜 지정 (telnet or ssh or serial)
    :param username: 접속을 위한 계정 이름
    :param password: 접속을 위한 비밀번호
    :param plugin_list: 선택한 plugin 문자열 리스트 (ex, ['Anti_Virus_Update', 'Change_Account_Lockout_Threshold'])
    :return: 0(성공), 1(대상 접속 실패), 2(점검 실패) - 미확정

    '''
    session = ConnectTarget(target_os, ip, port, type, username, password)
    
    # 예시, 원격 연결에 문제가 생겼다면 1, 점검에 문제가 발생하면 2
    if session is None:
        return 1
    
    inspection_lists = ParseXml(type, plugin_list)
    result = None
    for command in inspection_lists:
        plugin_name = command.get("PluginName")
        result_type = command.get("ResultType")
        command_count = int(command.get("CommandCount"))
        command_type = command.get("CommandType")
        command_string = command.get("CommandString")
        print(plugin_name)
        print(result_type)
        for _ in range(command_count):
            if command_type == "cmd":
                result = session.send_command(command_string)
        inspection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(inspection_time)
        print(result)
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