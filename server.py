import os, sender, receiver


def server_local(dirs,dirr,dic,sr_r,rs_w):
    receiver.receive_local(dirr,dic,sr_r,rs_w)