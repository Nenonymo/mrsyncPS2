import os

#ajouter ownership, mode, permissions, size et modtime
#si --checksum ajouter the file checksums

#chaque fichier est transmis au fur et a mesure ? optimisation ?
#trie de la liste ? par filelist ou ailleurs ? -> ailleurs

def parcours_rec(dir):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        if os.path.isdir(os.path.join(dir,elt)):
            file_list = file_list+[os.path.join(dir,elt)]+parcours_rec(os.path.join(dir,elt))
        if os.path.isfile(os.path.join(dir,elt)):
            file_list.append(os.path.join(dir,elt))
    return file_list

def parcours(dir,dict):#atention affiche les fichiers cachés
    file_list=[]
    if dir == '.' :
        dir = os.getcwd()
    elif dir == '..' :
        dir = os.path.split(os.getcwd())[0]
    if dict['-r']:
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            if os.path.isfile(os.path.join(dir,elt)):
                file_list.append(os.path.join(dir,elt))
            else :
                file_list=file_list+[os.path.join(dir,elt)]+parcours_rec(os.path.join(dir,elt))
    else :
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            file_list.append(os.path.join(dir,elt))
    return file_list

if __name__ == "__main__":
    print(parcours("/home/kf/Bureau/test",{"-r":True}))