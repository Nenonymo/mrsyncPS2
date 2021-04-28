import os, message
    #si --delete : supprime les fic+rep de receiver pas dans sender

    #on parcours file_list_sender et on retient les fichiers qui ne sont pas dans receiver
    #(modification time and size differs dans la plupart des cas)
    #si --checksum, a file-level checksum will be cerated and compared
    #on crée les repertoires et on ne skip pas les repertoires, symlink et device nodes
    
    #si --whole-file on réenvoit le fichier entier(empty block checksum)
    #sinon on compare le fichier dans le rep de receiver et e fichier dans le rep de sender 
    #en local on fair avec whole-file par defaut

def sort_receiver(dir):
    i=0
    while i < len(dir):
        if os.path.isdir(dir[i]['name']):
            j=i+1
            while os.path.isdir(dir[j]['name']) and j < len(dir):
                j=j+1
            if j == len(dir):
                i = j
            else:
                tmp = dir[i]
                dir[i]=dir[j]
                dir[j]=tmp


def delete_files(file_list_receiver,file_list_sender):
    sort_receiver(file_list_receiver)  #receiver trié avec le repertoires à la fin
    for elt in file_list_receiver:
        test = True
        for e in file_list_sender:
            if elt['name'] == e['name']:
                test = False
                break
        if test:
            if os.path.isdir(elt['name']):
                os.rmdir(elt['name'])
            else:
                os.unlink(elt['name'])

def no_skip(file,file_list_receiver):
    for elt in file_list_receiver:
        if elt['name'] == file['name'] :
            if os.path.isdir(elt['name']) or os.path.islink(elt['name']):
                return False
            elif os.path.isfile(elt['name']):
                if elt['size'] == file['size'] and elt['modtime'] == file['modtime']:
                    return False
#gestion des fichiers spéciaux (device node) ?
    return True

def generator_local(dirs,dirr,file_list_sender,file_list_receiver,dic,gs_g):
    if dic["--delete"]:
        delete_files(file_list_receiver,file_list_sender)
    send_list=[]
    for elt in file_list_receiver:
        if no_skip(elt,file_list_receiver):
            send_list.append(elt)
    for i in range(len(send_list)):
        tag = "liste"
        if i == len(send_list)-1:
            tag += "f"
        message.envoit(gs_g,tag,send_list[i])
        #envoit la sendlist au sender, envoyer les noms pas absolus


#A faire : gérer les options perm et time