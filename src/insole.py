#!/usr/bin/env python3

import rospy
import numpy as np

from std_msgs.msg import Float64MultiArray
from socket import *
import struct



TCP_IP = "192.168.50.51"
TCP_PORT = 2000

class KLib():
    def __init__(self,_server_ip = "192.168.50.96", _port = 3800):
        self.nrow = 0
        self.ncol = 0
        self.datasize = 0
        self.adc = None
        self.port = _port
        self.server_ip = _server_ip
        self.device = ""
        self.sensor = ""
        self.adc = []
        
        self.buf = None
        self.BufSize = 200
        self.addr = None
        self.client_socket = None
        self.result = None

        self.client_socket_connection = False


        self.pub_insole = rospy.Publisher('insole_data', Float64MultiArray, queue_size=10)

    #TcpIP 연결 시도
    def init(self):
        try:
            self.addr = (self.server_ip, self.port) #server address 정보
            self.client_socket = socket(AF_INET, SOCK_STREAM) #소켓 정보
            
            self.client_socket.connect(self.addr) # tcpip연결
        except Exception as e:
            print('Failed to connect TCP/IP!')
            self.client_socket_connection = False
            return False
        self.client_socket_connection = True

        resp = self.client_socket.recv(self.BufSize) #버퍼 받기

        self.buf = resp
        self.datasize = 5000
        self.BufSize = self.datasize +200
        sp = 0
        

        #header가 2개 이상이 아닌경우 패킷이 다안들어왔을 가능성이 있음
        while(1):
            if(len(self.buf) > self.BufSize):
                break
            resp = self.client_socket.recv(self.BufSize)
            self.buf = self.buf + resp

             #header 위치 찾기
            
            while(1):
                sp = self.buf.index(0x7e,sp)
                if(self.buf[sp+1] == 0x7e and self.buf[sp+2]== 0x7e and self.buf[sp+3] == 0x7e):
                    self.nrow = int.from_bytes(self.buf[88:91],byteorder='little')
                    self.ncol = int.from_bytes(self.buf[92:95],byteorder='little')
                    self.datasize = self.nrow * self.ncol
                    self.BufSize = self.datasize + 200
                    break
        
       
       

        self.device = self.buf[4:28]
        self.sensor = self.buf[28:52]
        self.nrow = int.from_bytes(self.buf[88:91],byteorder='little')
        self.ncol = int.from_bytes(self.buf[92:95],byteorder='little')
        self.datasize = self.nrow * self.ncol
        self.BufSize

         #header, tail을 뺀 버퍼를 result에 집어넣음
        self.result = self.buf[sp + 4 : sp + self.datasize]

        # rawdata array 생성
        for i in range(96,self.datasize+96):
            self.adc.append(int(self.buf[i]))
               

    def check_tcp_connection(self):
        if(self.client_socket_connection == True):
            return True
        else:
            return False
    #서버와 tcp 연결 시도
    def start(self):
        self.init()
    #서봐의 tcp 연결 끊기
    def stop(self):
        self.client_socket.close()
        self.client_socket_connection = False

    #패킷읽기
    def read(self):
        self.buf  = self.client_socket.recv(self.BufSize)

        #header가 2개 이상이 아닌경우 패킷이 다안들어왔을 가능성이 있음
        while(1):
            if(len(self.buf) > self.BufSize):
                break
            resp = self.client_socket.recv(self.BufSize)
            self.buf = self.buf + resp
        
        #header 위치 찾기
        sp = 0
        while(1):
            sp = self.buf.index(0x7e,sp)
            if(self.buf[sp+1] == 0x7e and self.buf[sp+2]== 0x7e and self.buf[sp+3] == 0x7e):
                break

        for i in range(96+sp,self.datasize+96+sp):
             self.adc[i-96-sp] = float(self.buf[i])

    def publish_insole(self):
        insole_array = Float64MultiArray()
        


        insole_array.data = self.adc
        print(np.array(self.adc).reshape(16,20))

        self.pub_insole.publish(insole_array)

        


def main():
    rospy.init_node('insole', anonymous=True)
    rate = rospy.Rate(10000)
    klib = KLib("192.168.50.96", 3800)
    klib.start()
    rospy.loginfo("insole node active")

    while not rospy.is_shutdown():
        klib.read()
        klib.publish_insole()
        rate.sleep()

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass