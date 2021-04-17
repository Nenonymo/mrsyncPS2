import os

#ajouter ownership, mode, permissions, size et modtime
#si --checksum ajouter the file checksums

#chaque fichier est transmis au fur et a mesure ? optimisation ?

def parcours_rec(dir):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        st = os.stat(name)
        if os.path.isdir(name):
            file_list = file_list+[{'name':name,'user':st[4],'groupe':st[5],'mode':st[0],'perm':[os.access(name,R_OK),os.access(name,W_OK),os.access(name,X_OK)],'size':st[6],'modtime':st[8]}]+parcours_rec(name)
        if os.path.isfile(name):
            file_list.append({'name':name,'user':st[4],'groupe':st[5],'mode':st[0],'perm':[os.access(name,R_OK),os.access(name,W_OK),os.access(name,X_OK)],'size':st[6],'modtime':st[8]})
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
        st=os.stat(dir)
        file_list.append({'name':dir,'user':st[4],'groupe':st[5],'mode':st[0],'perm':[os.access(dir,R_OK),os.access(dir,W_OK),os.access(dir,X_OK)],'size':st[6],'modtime':st[8]})
    elif dic['-r']:
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            name = os.path.join(dir,elt)
            st = os.stat(name)
            if os.path.isfile(name):
                file_list.append({'name':name,'user':st[4],'groupe':st[5],'mode':st[0],'perm':[os.access(name,R_OK),os.access(name,W_OK),os.access(name,X_OK)],'size':st[6],'modtime':st[8]})
            else :
                file_list=file_list+[{'name':name,'user':st[4],'groupe':st[5],'mode':st[0],'perm':[os.access(name,R_OK),os.access(name,W_OK),os.access(name,X_OK)],'size':st[6],'modtime':st[8]}]+parcours_rec(name)
    else :
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            name = os.path.join(dir,elt)
            st=os.stat(name)
            file_list.append({'name':name,'user':st[4],'groupe':st[5],'mode':st[0],'perm':[os.access(name,R_OK),os.access(name,W_OK),os.access(name,X_OK)],'size':st[6],'modtime':st[8]})
    return file_list

if __name__ == "__main__":
    print(parcours("/home/kf/Bureau/test",{"-r":True}))