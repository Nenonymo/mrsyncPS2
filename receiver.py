import os,filelist

#brouillon

def receive_local(dir,dic):
    os.chdir(dir)
    file_listr = filelist.parcours('.',dic)