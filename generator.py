import os
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
        if os.path.isdir(dir[i]):
            j=i+1
            while os.path.isdir(dir[j]) and j < len(dir):
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
        if not elt in file_list_sender:
            if os.path.isdir(elt):
                os.rmdir(elt)
            else:
                os.unlink(elt)

def skip(file,file_list_receiver):
    for elt in file_list_receiver:
        if elt == file :
            if os.path.isdir(elt) or os.path.islink(elt):
                return True
            elif os.path.isfile(elt):
            #on skip pas si date de modification ou taille du fichier differents
#gestion des fichiers spéciaux (device node) ?
    return False

def generator_local(dirs,dirr,file_list_sender,file_list_receiver,dict):
    if dict["--delete"]:
        delete_files(file_list_receiver,file_list_sender)
    send_list=[]
    for elt in file_list_receiver:
        if not skip(elt):
            send_list.append(elt)