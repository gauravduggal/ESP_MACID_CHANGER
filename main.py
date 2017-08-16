import network,time,machine,ntptime
import ubinascii
SSID2='STUDENTS-M'
password2='I@netsec'
SSID1='Duggals'
password1='bubbles12'
#mac_str='6001941f87bd'
mac_str='C0EEFBDA0B3B'
gc.enable()

#gets local time and returns 2 strings in ef
def get_time():
    y=time.localtime()[0]
    m=time.localtime()[1]
    d=time.localtime()[2]
    h=time.localtime()[3]
    h=(h+5)%12
    mi=time.localtime()[4]
    h=int((mi+30)/60)+h
    mi=(mi+30)%60
    s=time.localtime()[5]
    date=str(d)+'/'+str(m)+'/'+str(y)
    utc=str(h)+'-'+str(mi)+'-'+str(s)
    return date,utc

def connect_ssid(S,p,m):
    flag=0
    ctr=0
    pin = machine.Pin(2,machine.Pin.OUT)
    pin.on()
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(S, p)
    sta_if.config(mac=ubinascii.unhexlify(mac_str))
    while sta_if.isconnected()!= True:
        ctr=ctr+1
        time.sleep(1)
        pin.value(not pin.value())
        print('Attempt '+str(ctr)+' to connect to '+S)
        if ctr>20:
            print('cannot connect to SSID '+S)
            flag = 1
            break
    return flag,sta_if,pin;

flag_home = 0;
sta_if = network.WLAN(network.STA_IF)
pin = machine.Pin(2,machine.Pin.OUT)
flag_home,sta_if,pin = connect_ssid(SSID1,password1,mac_str)

mac_ctr=0
if flag_home == 1:
    f = open("esp_data.txt","r")
    for line in f:
        mac_ctr=mac_ctr+1
        mac_str = line.replace('\n','')
        print(str(mac_ctr)+'. trying MAC ID: '+mac_str)
        mac_str = mac_str.replace(':','')
        flag,sta_if,pin = connect_ssid(SSID2,password2,mac_str)
        if flag==0: #if connected flag =0
            break
    f.close()

pin.off()
ip=sta_if.ifconfig()[0]
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('Connected to '+SSID1)
print('IP is: '+ip)
print('mac is: '+mac)
ntptime.settime()
date,utc=get_time()
print(date)
print(utc)

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP8266 Server</title> </head>
    <body> <h1>ESP8266 Server</h1>
        <table border="1"> <tr></tr> %s </table>
    </body>
</html>
"""

import socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)

print('listening on', addr)
ctr=0
while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    ctr=ctr+1
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    date,utc=get_time()
    rows = ['<tr><td>%s</td><td>%d</td><td>%s</td><td>%s</td></tr>' % ('pagevisits: ', int(ctr/2)+1,'time is: '+str(utc),'date is: '+date)]
    response = html % '\n'.join(rows)
    cl.send(response)
    cl.close()
