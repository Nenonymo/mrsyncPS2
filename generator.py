import os
    #si --delete : supprime les fic+rep de receiver pas dans sender

    #on parcours file_list_sender et on retient les fichiers qui ne sont pas dans receiver
    #(modification time and size differs dans la plupart des cas)
    #si --checksum, a file-level checksum will be cerated and compared
    #on crée les repertoires et on ne skip pas les repertoires, symlink et device nodes
    
    #si --whole-file on réenvoit le fichier entier(empty block checksum)
    #sinon on compare le fichier dans le rep de receiver et e fichier dans le rep de sender 
    #en local on fair avec whole-file par defaut

def delete_files(file_list_receiver,file_list_sender):
#receiver trié avec les fichiers avant les repertoires, avec noms de fichiers absolu
    for elt in file_list_receiver:
        if not elt in file_list_sender:
            if os.path.isdir(elt):
                os.rmdir(elt)
            else:
                os.unlink(elt)

def generator_local(dirs,dirrfile_list_sender,file_list_receiver,dict):
    if dict["--delete"]:
        