import os, sender, receiver

#brouillon, pas construit

def child_local(): #send
    os.close(rfds)
    os.close(wfdr)


def father_local(): #receive
    os.close(rfdr)
    os.close(wfds)
    


def server_local(dirs,dirr,dic):
    rfds,wfdr = os.pipe()
    rfdr,wfds = os.pipe()
    file_list_sender = send_local(dirs,dic)
    file_list_receiver = receive_local(dirr,dic)
    childpid = os.fork()
    if childpid == 0 :
        child_local()
    else :
        father_local()