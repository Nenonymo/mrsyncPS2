import os, sender, receiver

def child_local(): #send
    os.close(rfds)
    os.close(wfdr)


def father_local(): #receive
    os.close(rfdr)
    os.close(wfds)
    


def server_local(dirs,dirr,dict):
    rfds,wfdr = os.pipe()
    rfdr,wfds = os.pipe()
    file_list_sender = send_local(dirs,dict)
    file_list_receiver = receive_local(dirr,dict)
    childpid = os.fork()
    if childpid == 0 :
        child_local()
    else :
        father_local()