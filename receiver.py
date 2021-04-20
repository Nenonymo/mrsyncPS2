import os,filelist,message

#brouillon

def receive_local(dir,dic,sr_r,rs_w):
    file_listr = filelist.parcours(dir,dic)
    #recoit la liste de l'envoyeur et crée le generateur
    tag,file_lists = recoit(sr_r)