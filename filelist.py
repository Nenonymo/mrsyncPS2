import os

#ajouter ownership, mode, permissions, size et modtime
#si --checksum ajouter the file checksums

#chaque fichier est transmis au fur et a mesure ? optimisation ?

def parcours_rec(dir):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        if os.path.isdir(name):
            file_list = file_list+[[name]+os.stat(name)]+parcours_rec(name)
        if os.path.isfile(name):
            file_list.append([name]+os.stat(name))
    return file_list

def parcours(dir,dic):#atention affiche les fichiers caches
    file_list=[]
    if dir == '.' :
        dir = os.getcwd()
    elif dir == '..' :
        dir = os.path.split(os.getcwd())[0]
    else :
        dir = os.path.join(os.getcwd(),dir)
    if os.path.isfile(dir) or os.path.islink(dir):
        file_list.append([dir]+os.stat(dir))
    elif dic['-r']:
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            name = os.path.join(dir,elt)
            if os.path.isfile(name):
                file_list.append([name]+os.stat(name))
            else :
                file_list=file_list+[[name]+os.stat(name)]+parcours_rec(name)
    else :
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            name = os.path.join(dir,elt)
            file_list.append([name]+os.stat(name))
    return file_list

if __name__ == "__main__":
    print(parcours("/home/kf/Bureau/test",{"-r":True}))