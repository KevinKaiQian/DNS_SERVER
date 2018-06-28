#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import struct  
import SocketServer
import binascii
import Parse_XML
 
class ParseFrame:  
    def __init__(self, data):  
        self.i = 0
        self.value=''
        self.name =''
        self.ptr = 0
        self.ptrvalue = ''
        self.domain = ''
        while True:  
            d = binascii.b2a_hex(data)[self.i:self.i+2]
            if(self.i == 0):
                self.ptr = int(d,16)
                self.ptrvalue = binascii.b2a_hex(data)[0:(self.ptr+1)*2]
            if d == '00':  
                self.domain = binascii.b2a_hex(data)[0:self.i+2]
                break;  
            elif ((int(d,16) < 30)and(self.i != 0)):
                self.name = self.name +'.'
            elif ((int(d,16) > 30)and(self.i != 0)):
                self.name = self.name +chr(int(int(d,16)))
            self.i = self.i + 2  
            
        self.querybytes = data[0:self.i/2 + 1]  
        (self.type, self.classify) = struct.unpack('>HH', data[self.i/2 + 1:self.i/2 + 5])  
        self.len = self.i/2 + 5  
        
    def Bytes(self):  
        return self.querybytes + struct.pack('>HH', self.type, self.classify)  
  
# DNS Answer RRS  
# this class is also can be use as Authority RRS or Additional RRS   
class GenerateAnswer:  
    def __init__(self, ip,ptr,ptr_value):  
        self.name = 49164  
        self.type = 1  
        self.classify = 1  
        self.timetolive = 3600
        self.datalength = 4  
        self.ip = ip  
        self.ptr=ptr
        self.ptr_value=ptr_value

    def Bytes(self,mode=1,domain=''): 
        if (int(mode) == 1):
            #1 www.bbb.com 
            res = struct.pack('>HHHLH',self.name, self.type, self.classify, self.timetolive, self.datalength)
        elif (int(mode) == 2):
            #2 bbb.comm
            self.name += (self.ptr+1)
            res = struct.pack('>HHHLH',self.name, self.type, self.classify, self.timetolive, self.datalength)
        elif (int(mode) == 3):
            #3 (www).bbb.com
            self.name += (self.ptr+1)
            res = struct.pack('>HHHLH',self.name, self.type, self.classify, self.timetolive, self.datalength)
            res = binascii.a2b_hex(self.ptr_value)+res
        elif(int(mode) == 4):
            #not ptr
            res = binascii.a2b_hex(domain)+struct.pack('>HHLH', self.type, self.classify, self.timetolive, self.datalength)   
        s = self.ip.split('.')  
        res = res + struct.pack('BBBB', int(s[0]), int(s[1]), int(s[2]), int(s[3]))  
        return res  
class Parseheader:
    def __init__(self,data):
        self.Parse(data)
        self.answers = 1  
        self.flags = 34176
    def Parse(self,data):
        (self.id, self.flags, self.quests, self.answers, self.author, self.addition) = struct.unpack('>HHHHHH', data[0:12])
    def Bytes(self):
        res = struct.pack('>HHHHHH', self.id, self.flags, self.quests, self.answers, self.author, self.addition) 
        return res
class DNSFrame:  
    def __init__(self, data,mode):  
        self.mode = mode 
        self.header=Parseheader(data[0:12])
        self.query = ParseFrame(data[12:]) 
    def Configure(self, ip):  
        self.answer = GenerateAnswer(ip,self.query.ptr,self.query.ptrvalue)  
    def Bytes(self):  
        res = self.header.Bytes() + self.query.Bytes()+self.answer.Bytes(self.mode,self.query.domain)    
        return res  

class DNSUDPHandler(SocketServer.BaseRequestHandler):  
    def handle(self):  
        data = self.request[0].strip()  
        dns = DNSFrame(data,DNSServer.parameter['mode'])  
        socket = self.request[1]  
        namemap = DNSServer.namemap        
        if(dns.query.type==1):  
            name = dns.query.name 
            if namemap.__contains__(name):    
                dns.Configure(namemap[name])  
                socket.sendto(dns.Bytes(), self.client_address)  
                print name+':'+namemap[name]
            elif namemap.__contains__('*'):  
                dns.Configure(namemap['*'])  
                socket.sendto(dns.Bytes(), self.client_address)  
            else:  
                socket.sendto(data, self.client_address)  
        else:  
            socket.sendto(data, self.client_address)  
class DNSServer: 
    def __init__(self):  
        xml = Parse_XML.Collect_entity()
        DNSServer.namemap = xml.entity()
        DNSServer.parameter=xml.Parameter()
    def start(self):  
        HOST, PORT = str(DNSServer.parameter['Address']), int(DNSServer.parameter['port']) 
        server = SocketServer.UDPServer((HOST, PORT), DNSUDPHandler)  
        server.serve_forever()  
if __name__ == "__main__":  
    sev = DNSServer()  
    sev.start() 