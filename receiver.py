import os,filelist

def receive_local(dir,dict):
    os.chdir(dir)
    file_listr = filelist.parcours('.',dict)