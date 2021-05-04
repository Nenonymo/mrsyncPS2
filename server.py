import os, receiver, socket


def server_local(dirs,dirr,dic,gs_g,sr_r):
    receiver.receive_local(dirs,dirr,dic,gs_g,sr_r)

def server_daemon(dic):
    port = 10873
    if dic['--port'] != '':
        port = int(dic['--port'])
    servsoc = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0) #???
    serv.connect((localhost, port)) #localhost??
    