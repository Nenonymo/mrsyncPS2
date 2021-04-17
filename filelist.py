import os

#ajouter ownership, mode, permissions, size et modtime -> ok
#si --checksum ajouter the file checksums

#chaque fichier est transmis au fur et a mesure ? optimisation ?

def parcours_rec(dir):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        st = os.stat(name)
        if os.path.isdir(name):
            file_list = file_list+[{'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'perm':[os.access(name,os.R_OK),os.access(name,os.W_OK),os.access(name,os.X_OK)],'size':st.st_size,'modtime':st.st_mtime}]+parcours_rec(name)
        if os.path.isfile(name):
            file_list.append({'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'perm':[os.access(name,os.R_OK),os.access(name,os.W_OK),os.access(name,os.X_OK)],'size':st.st_size,'modtime':st.st_mtime})
    return file_list

def parcours(dir,dic): #fichiers caches compris
    file_list=[]
    if dir == '.' :
        dir = os.getcwd()
    elif dir == '..' :
        dir = os.path.split(os.getcwd())[0]
    else :
        dir = os.path.join(os.getcwd(),dir)
    if os.path.isfile(dir) or os.path.islink(dir):
        st=os.stat(dir)
        file_list.append({'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'perm':[os.access(name,os.R_OK),os.access(name,os.W_OK),os.access(name,os.X_OK)],'size':st.st_size,'modtime':st.st_mtime})
    elif dic['-r']:
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            name = os.path.join(dir,elt)
            st = os.stat(name)
            if os.path.isfile(name):
                file_list.append({'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'perm':[os.access(name,os.R_OK),os.access(name,os.W_OK),os.access(name,os.X_OK)],'size':st.st_size,'modtime':st.st_mtime})
            else :
                file_list=file_list+[{'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'perm':[os.access(name,os.R_OK),os.access(name,os.W_OK),os.access(name,os.X_OK)],'size':st.st_size,'modtime':st.st_mtime}]+parcours_rec(name)
    else :
        curr_dir = os.listdir(dir)
        for elt in curr_dir:
            name = os.path.join(dir,elt)
            st=os.stat(name)
            file_list.append({'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'perm':[os.access(name,os.R_OK),os.access(name,os.W_OK),os.access(name,os.X_OK)],'size':st.st_size,'modtime':st.st_mtime})
    return file_list