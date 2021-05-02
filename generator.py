import os, sys, message
    #(modification time and size differs dans la plupart des cas)
    #si --checksum, a file-level checksum will be cerated and compared
    #on crée les repertoires et on ne skip pas les repertoires, symlink et device nodes
    
    #si --whole-file on réenvoit le fichier entier(empty block checksum)
    #sinon on compare le fichier dans le rep de receiver et e fichier dans le rep de sender 
    #en local on fair avec whole-file par defaut

#tri avec repertoire a la fin
#actuellement sort_receiver ne sert a rien je le garde au cas ou mais si on l'utilise pas poubelle
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

def supprimer(rep):
    cur_dir=os.listdir(rep)
    for elt in cur_dir:
        elt = os.path.join(rep,elt)
        if os.path.isdir(elt):
            supprimer(elt)
        else:
            os.unlink(elt)
    os.rmdir(rep)


def delete_files(file_list_receiver,file_list_sender):
    for elt in file_list_receiver:
        test = True
        for e in file_list_sender:
            if elt['name_loc'] == e['name_loc']:
                test = False
                break
        if test:
            if os.path.isdir(elt['name']):
                supprimer(elt['name'])
            else:
                try :
                    os.unlink(elt['name'])
                except :
                    pass

def no_skip(fichier,file_list_receiver):
    for elt in file_list_receiver:
        if elt['name_loc'] == fichier['name_loc'] :
            if os.path.isdir(elt['name']) or os.path.islink(elt['name']):
                return False
            elif os.path.isfile(elt['name']):
                if elt['size'] == fichier['size'] and elt['modtime'] == fichier['modtime']: #modtime ??
                    return False
#gestion des fichiers spéciaux (device node) ?
    return True

def generator_local(dirs,dirr,file_list_sender,file_list_receiver,dic,gs_g):
    if dic["--delete"]:
        delete_files(file_list_receiver,file_list_sender)
    send_list=[]
    for elt in file_list_sender:
        if no_skip(elt,file_list_receiver):
            send_list.append(elt)
    nbr_file = len(send_list)
    #envoit de la liste des fichiers au sender
    if nbr_file == 0:   #si send_list est vide
        print("hello")
        tag = ['','l',(0,0)]
        message.envoit(gs_g,tag,lineFile='comSize1')
    for i in range(nbr_file):
        tag = [send_list[i]["name_loc"],"l",(i+1,nbr_file)]
        message.envoit(gs_g,tag,v=send_list[i],lineFile='comSize1')
    
    #attente de la fin des fils et terminaison
    os.wait()
    os.wait()
    sys.exit(0)

#A faire : gérer les options perm et time