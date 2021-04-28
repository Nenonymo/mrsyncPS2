import os

#si --checksum ajouter the file checksums

def parcours_simple(dir):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        st = os.stat(name)
        file_list.append({'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list

def parcours_rec(dir):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        st = os.stat(name)
        if os.path.isdir(name):
            file_list = file_list+[{'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime}]+parcours_rec(name)
        else:
            file_list.append({'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list

def parcours(dir,dic): #fichiers caches compris
    file_list=[]
    if dic['-r'] :
        if os.path.isdir(dir):
            file_list = parcours_rec(dir)
        else:
            st = os.stat(dir)
            file_list.append({'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    else :
        if os.path.isdir(dir) and dir[-1]=='/':
            file_list = parcours_simple(dir)
        else :
            st=os.stat(dir)
            file_list.append({'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list

def norm_liste_dir(lis_dir, dic) :
    #On créé la liste complète (sauf avec -r) de fichiers à traiter en faisant gaffe aux doublons
    if dic['-r'] :
        i = 0
        while i < len(lis_dir) :
            j = i + 1
            while j < len(lis_dir) :
                if lis_dir[i] == lis_dir[j][:len(lis_dir[i])] + '/' :
                    del lis_dir[j]
                elif lis_dir[i][:len(lis_dir[j])] + '/' == lis_dir[j] :
                    del lis_dir[i]
                j += 1
            i += 1
    else :
        i = 0
        while i < len(lis_dir) :
            if lis_dir[i][-1]=='/':
                lis_dir[i]= os.path.abspath(lis_dir[i])+'/'
            else :
                lis_dir[i] = os.path.abspath(lis_dir[i])
            i += 1
        i = 0
        while i < len(lis_dir) :
            j = i+1
            while j < len(lis_dir) :
                if lis_dir[i] == lis_dir[j] :
                    del lis_dir[j]
                j += 1
            i += 1
    return lis_dir

def filelist(lis_dir,dic):
    file_list = []
    lis_dir = norm_liste_dir(lis_dir,dic)
    for dir in lis_dir:
        file_list = file_list + parcours(dir,dic)
    return file_list

#bug
#affichage du nom absolu, j'ai du enlever le truc avec cwd provisoirement