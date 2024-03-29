# [TITLE] 점검 모듈
# [DESC] 작성된 XML 스크립트를 이용하여 서버에 원격 접속 후 자동으로 취약점 점검하는 프로그램
# [Writer] CodeByO

import os
import sys
import signal
from pathlib import Path

import telnetlib
import netmiko
import serial

import xml.etree.ElementTree as ET

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

# [Func] ConnectTarget
# [DESC] 보안 취약점 점검 대상 PC에 접속
# [TODO] 각 인자에 맞게 코드 구현
# [ISSUE] None
def ConnectTarget(ip:str, port:str, type:str):
    """
    보안 취약점 점검 대상 PC에 접속
    :param ip: 접속하고자 하는 대상 PC 주소
    :param port: 접속하고자 하는 포트 번호
    :param type: 접속 프로토콜 지정 (telnet or ssh or serial)
    :return: Not Yet
    """
    pass


# [Func] ParseXml
# [DESC] XML 스크립트 로드 및 정리
# [TODO] 기능 구현
# [ISSUE] None
def ParseXml():
    """
    XML 스크립트 로드 및 정리
    출처 : https://king-rabbit.github.io/python/xml-parsing/
    
    :return: 스크립트 별로 점검할 수 있도록 정리된 자료구조
    """
    path_src = Path(__file__)
    path_script = path_src.parent / 'script'
    script_files = os.listdir(path_script)
    
    for script_file in script_files:
        script_path = path_script / script_file
        
        # xml 파일 불러오기
        tree = ET.parse(script_path)
        
        # root 데이터 가져오기
        root = tree.getroot()
        
        # tag, attrib 변수 가져오기
        print(root.tag)
        print(root.attrib)
        
        #attribute 값 가져오기
        for child in root:
            print(child.get(''))
            print(child.keys())
            print(child.items())

# [Func] InspectionAutomation
# [DESC] 정리된 스크립트를 이용하여 보안 취약점 점검
# [TODO] 기능 구현
# [ISSUE] None
def InspectionAutomation():
    '''
    정리된 스크립트를 이용하여 보안 취약점 점검
    
    :return: DB에 올리기 위한 점검 결과 자료구조
    '''
    pass

if __name__ == '__main__':
    # 특정 signal 입력 시 수행하는 동작 정의
    def SignalHandler(sig, frame):
        pass

    # SIGINT(Ctrl + C) 입력시 singal_handler 실행
    signal.signal(signal.SIGINT, SignalHandler)