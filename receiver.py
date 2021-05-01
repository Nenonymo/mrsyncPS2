import os,filelist,message,generator, pidManagement

#brouillon

def receive_local(dirs,dirr,dic,gs_g,sr_r):
    if dirr[-1] != '/':
        dirr = dirr + '/'
    file_listr = filelist.filelist([dirr],dic)
    file_lists=[]
    tag = ['','l',(0,1)]
    while tag[2][0]<=tag[2][1]:  #file_lists ne peut pas etre vide
        tag,data = message.recoit(sr_r)
        print(data)
        file_lists.append(data)
    pid=os.fork()
    if pid != 0: #père, générateur
        generator.generator_local(dirs,dirr,file_lists,file_listr,dic,gs_g)
    else: #fils, receiver
        pidManagement.appToFile('pid', 're:{}'.format(os.getpid()))#enregistrement du pid
        tag,data = message.recoit(sr_r)
        nbr_file = tag[2][1]
        print(nbr_file)
        '''
        i = 1
        while i <= nbr_file:
            tag,data = message.recoit(sr_r)
            #ecrit les donnes dans le fichier + cree les repertoires
            i+=1
        '''