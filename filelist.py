import os

def parcours_rec(dir,nom):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        if os.path.isdir(os.path.join(dir,elt)):
            file_list = file_list+[os.path.join(nom,elt)]+parcours_rec(os.path.join(dir,elt),elt)
        if os.path.isfile(os.path.join(dir,elt)):
            file_list.append(os.path.join(nom,elt))
    return file_list

def parcours(dir):#dict #atention affiche les fichiers cachés
    file_list=[]
    if dir == '.' :
        dir = os.getcwd()
    elif dir == '..' :
        dir = os.path.split(os.getcwd())[0]
    if True:#dict['-r']:
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            if os.path.isfile(os.path.join(dir,elt)):
                file_list.append(elt)
            else :
                file_list=file_list+[elt]+parcours_rec(os.path.join(dir,elt),elt)
    else :
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            file_list.append(elt)
    return file_list

if __name__ == "__main__":
    print(parcours("/home/kf/Bureau/test"))