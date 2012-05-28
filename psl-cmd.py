#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket 
import time
import binascii
import pprint
import struct
import random
import sys
import ipaddr
import argparse

def unpack_string(v):
  return v
  
def unpack_ipv4(v):
  a=struct.unpack(">I",v)[0]
#  return a
  print "ip=",a
  return "%s" % ipaddr.IPv4Address(a)
  
def unpack_boolean(v):
  return (v==0x01)

def unpack_mac(v):
  mac=binascii.hexlify(v)
  return mac[0:2]+":"+mac[2:4]+":"+mac[4:6]+":"+mac[6:8]+":"+mac[8:10]+":"+mac[10:12]

def unpack_null(v):
  return v
  

def pack_string(v):
  return v

def pack_ipv4(v):
  i=(int)(ipaddr.IPv4Address(v))
  print "ip=",i
  r=struct.pack(">I",i)
  print  binascii.hexlify(r)
  return r

def pack_boolean(v):
  if (v):
    return struct.pack(">b",0x01)
  else:
    return struct.pack(">b",0x00)

def pack_mac(v):
   if (len(v)==17):
        return binascii.unhexlify(v[0:2]+v[3:5]+v[6:8]+v[9:11]+v[12:14]+v[15:17])
   if (len(v)==12):
	return binascii.unhexlify(v)
   raise "unkown mac format="+v
    
def pack_null(v):
  return v

class psl:
	CMD_MODEL    = 0x0001
	CMD_FIMXE2   = 0x0002
	CMD_NAME     = 0x0003
	CMD_MAC      = 0x0004
	CMD_FIMXE5   = 0x0005
	CMD_IP       = 0x0006
	CMD_NETMASK  = 0x0007
	CMD_GATEWAY  = 0x0008
	CMD_NEW_PASSWORD = 0x0009
	CMD_PASSWORD = 0x000a
	CMD_DHCP     = 0x000b
	CMD_FIXMEC   = 0x000c
	CMD_FIRMWAREV= 0x000d
	CMD_FIMXEE   = 0x000e
	CMD_FIXMEF   = 0x000f
	CMD_REBOOT   = 0x0013
	CMD_FACTORY_RESET = 0x0400
	CMD_PORT_STAT= 0x1000
	CMD_VLAN_SUPP= 0x2000
	CMD_VLAN_ID  = 0x2400
	CMD_FIMXE3400= 0x3400	
	CMD_FIMXE3800= 0x3800	
	CMD_FIMXE4c00= 0x4c00	
	CMD_FIXME5000= 0x5000
	CMD_FIXME5400= 0x5400
	CMD_FIXME5800= 0x5800
	CMD_FIXME5c00= 0x5c00
	CMD_FIXME6800= 0x6800
	CMD_FIXME6c00= 0x6c00
	CMD_FIXME7000= 0x7000
	CMD_FIXME7400= 0x7400
	CMD_END	     = 0xffff
	CTYPE_QUERY_REQUEST= 0x0101
	CTYPE_QUERY_RESPONSE= 0x0102
	CTYPE_TRANSMIT_REQUEST = 0x103
	CTYPE_TRANSMIT_RESPONSE = 0x104
	TYP_STRING={0:pack_string, 1: unpack_string}
	TYP_MAC={0:pack_mac, 1: unpack_mac}
	TYP_IPV4={0:pack_ipv4, 1: unpack_ipv4}
	TYP_BOOLEAN={0:pack_boolean, 1: unpack_boolean}
	FLAG_PASSWORD_ERROR=0x000a        
	TYPHASH= {
		CMD_MODEL:TYP_STRING,
		CMD_NAME:TYP_STRING,
		CMD_MAC:TYP_MAC,
		CMD_IP:TYP_IPV4,
		CMD_NETMASK:TYP_IPV4,
		CMD_GATEWAY:TYP_IPV4,
		CMD_NEW_PASSWORD:TYP_STRING,
		CMD_PASSWORD:TYP_STRING,
		CMD_DHCP:TYP_BOOLEAN,
		CMD_FIRMWAREV:TYP_STRING,
		CMD_REBOOT:TYP_BOOLEAN,
		CMD_FACTORY_RESET:TYP_BOOLEAN,
		}
	RECPORT=63321
	SENDPORT=63322
	def __init__(self,host,srcmac):
		self.myhost = host
		self.myport = self.RECPORT
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
		self.socket.bind(("255.255.255.255", self.myport))
  		
		self.seq = random.randint(100,2000)
#		self.srcmac = 0x00218698da1e
		self.srcmac = 0x00163e19e1e1


	def unpackValue(self,cmd,value):
	         try:
		   f=self.TYPHASH[cmd][1]
		   return f(value)
		 except:
		   return binascii.hexlify(value)
		
	def packValue(self,cmd,value):
	         try:
		   f=self.TYPHASH[cmd][0]
		   return f(value)
		 except:
		   return binascii.unhexlify(value)
		
	def recv(self,recvfunc,maxlen=8192,timeout=0.005):
		self.socket.settimeout(timeout)
		try:
			message, address = self.socket.recvfrom(maxlen)
		except socket.timeout:
			return None
		print "recv="+binascii.hexlify(message)
		if recvfunc is not None:	
		   recvfunc(message,address)
		self.recv(recvfunc,maxlen,timeout)

	def parse_packet(self,p):
		data = {}
		data["seq"]= struct.unpack(">H",p[22:24])[0]
		data["ctype"]= struct.unpack(">H",p[0:2])[0]
		data["flags"]= struct.unpack(">H",p[4:6])[0]
		data["mymac"]= binascii.hexlify(p[8:14])
		data["theirmac"]= binascii.hexlify(p[14:20])
                pos=32
		cmd=0
		while(cmd!=0xffff):
		  cmd= struct.unpack(">H",p[pos:(pos+2)])[0]
		  pos=pos+2
		  len=struct.unpack(">H",p[pos:(pos+2)])[0]
		  pos=pos+2
		  value = self.unpackValue(cmd,p[pos:(pos+len)])
		  data[cmd]=value
		     
		  #print "cmd=",cmd," len=",len," data=",binascii.hexlify(p[pos:(pos+len)])
		  pos=pos+len
		#pprint.pprint(data)
		return data

	def discoverfunc(self,m,a):
		#print "==FOUND SWITCH=="
		data = self.parse_packet(m)
		dhcpstr=""
		if (data[self.CMD_DHCP]):
		   dhcpstr=" DHCP=on"
		print " * %s\t%s\t%s\t%s\t%s" % (data[self.CMD_MAC],data[self.CMD_IP],data[self.CMD_MODEL],data[self.CMD_NAME],dhcpstr)

	def transfunc(self,m,a):
		#print "==FOUND SWITCH=="
		data = self.parse_packet(m)
		pprint.pprint(data)
		if data["flags"]==self.FLAG_PASSWORD_ERROR:
		   print "wrong password"
		if data["flags"]==0:
  		   print "success"


	def send(self,host,port,data):
		print "send="+binascii.hexlify(data)
		self.socket.sendto(data,(host,port))
		self.seq+=1

	def baseudp(self,ctype,destmac=6*"\x00"):
		reserved = "\x00"
		data = struct.pack(">h",ctype) + 6* reserved + struct.pack('>LH', self.srcmac >> 16, self.srcmac & 0xffff)+destmac + 2*reserved  
		data += struct.pack(">h",self.seq)
		data +=  "NSDP" + 4 * reserved 
		return data

	def addudp(self,cmd,datain=None):
	        data = struct.pack(">H",cmd)
		if (datain):
		  pdata=self.packValue(cmd,datain);
		  data += struct.pack(">H", len(pdata))
		  data += pdata
		else:
		  data += struct.pack(">H", 0)
		return data

	def query(self,cmd_arr,func):
		data = self.baseudp(ctype=self.CTYPE_QUERY_REQUEST)
		for cmd in cmd_arr:
	            data+=self.addudp(cmd);
                data+=self.addudp(self.CMD_END)
		self.send("255.255.255.255",self.SENDPORT, data)
		time.sleep(0.7)
		self.recv(func)


	def transmit(self,cmd_arr,mac,func):
		data = self.baseudp(destmac=mac,ctype=self.CTYPE_TRANSMIT_REQUEST)
		for cmd,pdata in cmd_arr.items():
	            data+=self.addudp(cmd,pdata);
                data+=self.addudp(self.CMD_END)
		self.send("255.255.255.255",self.SENDPORT, data)
		time.sleep(0.7)
		self.recv(func)

	def passwd(self,mac,old,new,func):
		# The Order of the CMD_PASSWORD and CMD_NEW_PASSWORD is important
		data = self.baseudp(destmac=mac,ctype=self.CTYPE_TRANSMIT_REQUEST)
	        data+=self.addudp(self.CMD_PASSWORD,old);
	        data+=self.addudp(self.CMD_NEW_PASSWORD,new);
                data+=self.addudp(self.CMD_END)
		self.send("255.255.255.255",self.SENDPORT, data)
		time.sleep(0.7)
		self.recv(func)


	def discover(self):
		query_arr=[self.CMD_MODEL,
			   self.CMD_NAME,
			   self.CMD_MAC,
			   self.CMD_DHCP,
			   self.CMD_IP];
		self.query(query_arr,self.discoverfunc)


parser = argparse.ArgumentParser(description='Manage Netgear ProSafe Plus switches under linux.')
subparsers = parser.add_subparsers(help='operation',dest="operation")

discover_parser=subparsers.add_parser('discover', help='Find all switches in all subnets')
passwd_parser=subparsers.add_parser("passwd",help="Change Password of a switch")
passwd_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
passwd_parser.add_argument("--old",nargs=1,help="old password",required=True)
passwd_parser.add_argument("--new",nargs=1,help="new password",required=True)

query_parser=subparsers.add_parser("query",help="Query values from the switch")
query_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
query_parser.add_argument("--passwd",nargs=1,help="password",required=True)
query_parser.add_argument("query",nargs="+",help="What to query for",choices=['ip','mac','model','gateway','netmask']);

reboot_parser=subparsers.add_parser("reboot",help="Reboot the switch")
reboot_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
reboot_parser.add_argument("--passwd",nargs=1,help="password",required=True)

reset_parser=subparsers.add_parser("factory-reset",help="Reset the switch")
reset_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
reset_parser.add_argument("--passwd",nargs=1,help="password",required=True)

set_parser=subparsers.add_parser("set",help="Set values to the switch")
set_parser.add_argument("--mac",nargs=1,help="Hardware adresse of the switch",required=True)
set_parser.add_argument("--passwd",nargs=1,help="password",required=True)
set_parser.add_argument("--ip",nargs=1,help="Change IP")
set_parser.add_argument("--name",nargs=1,help="Change Name")
set_parser.add_argument("--dhcp",nargs=1,help="DHCP?",choices=["on","off"])

g = psl('192.168.11.21',0x00163e19e1e1)
args = parser.parse_args()

if args.operation=="discover":
  print "Searching for ProSafe Plus Switches ...\n"
  g.discover()

if args.operation=="reboot":
  print "Rebooting Switch...\n";
  cmd={g.CMD_PASSWORD:args.passwd[0],
       g.CMD_REBOOT:True}
  g.transmit(cmd,pack_mac(args.mac[0]),g.transfunc)

if args.operation=="factory-reset":
  print "Reseting Switch to factory defaults...\n";
  cmd={g.CMD_PASSWORD:args.passwd[0],
       g.CMD_FACTORY_RESET:True}
  g.transmit(cmd,pack_mac(args.mac[0]),g.transfunc)

#g.passwd(0xe091f5936b94, 'kat', 'hemmeligt')


if args.operation=="passwd":
  print "Changing Password...\n";
  g.passwd(pack_mac(args.mac[0]),args.old[0],args.new[0],g.transfunc)

if args.operation=="set":
  print "Changing Values..\n"
  cmd={g.CMD_PASSWORD:args.passwd[0]}
  if (args.ip):
      cmd[g.CMD_IP]=args.ip[0]
  if (args.dhcp):
      cmd[g.CMD_DHCP]=(args.dhcp[0]=="on")
  if (args.name):
      cmd[g.CMD_NAME]=args.name[0]

  g.transmit(cmd,pack_mac(args.mac[0]),g.transfunc)