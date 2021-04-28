import os,filelist,message,generator

#brouillon

def receive_local(dirs,dirr,dic,gs_g,sr_r):
    if dirr[-1] != '/':
        dirr = dirr + '/'
    file_listr = filelist.filelist(dirr,{'-r':False})
    #recoit la liste de l'envoyeur et crée le generateur
    tag,file_lists = message.recoit(sr_r)
    pid=os.fork()
    if pid == 0:
        generator.generator_local(dirs,dirr,file_lists,file_listr,dic,gs_g)
    else:
        while True : #que mettre ?
            tag,data = message.recoit(sr_r)
            #ecrit les donnes dans le fichier + cree les repertoires