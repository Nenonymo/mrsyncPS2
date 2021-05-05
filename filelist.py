import os

#si --checksum ajouter the file checksums

def parcours_simple(dir,nom_loc,verbose,whoami):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        nom = nom_loc +elt
        st = os.stat(name)
        file_list.append({'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
        if verbose > 2 :
            print('[{}][parcours simple] file add : {}'.format(whoami,nom))
    return file_list

def parcours_rec(dir,nom_loc,verbose,whoami):
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        if nom_loc.endswith('/'):
            nom = nom_loc+elt
        elif nom_loc == '':
            nom = elt
        else :
            nom=nom_loc+'/'+elt
        if verbose > 2 :
            print('[{}][parcours recursif] file add : {}'.format(whoami,nom))
        st = os.stat(name)
        if os.path.isdir(name):
            file_list = file_list+[{'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime}]+parcours_rec(name,nom,verbose,whoami)
        else:
            file_list.append({'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list

def parcours(dir,nom_loc,dic,whoami): #fichiers caches compris
    file_list=[]
    if dic['-r'] :
        st = os.stat(dir)
        if os.path.isdir(dir) and dir[-1]!='/':
            file_list = [{'name_loc':nom_loc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime}]+parcours_rec(dir,nom_loc,whoami)
        elif os.path.isdir(dir):
            file_list = parcours_rec(dir,nom_loc,dic['-v'],whoami)
        else:
            file_list.append({'name_loc':nom_loc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    else :
        if os.path.isdir(dir) and dir[-1]=='/':
            file_list = parcours_simple(dir,nom_loc,dic['-v'],whoami)
        else :
            st=os.stat(dir)
            file_list.append({'name_loc':nom_loc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list

def norm_liste_dir(lis_dir, dic) :
    lis_dir_abs=[]
    i = 0
    while i < len(lis_dir) :
        if lis_dir[i][-1]=='/':
            lis_dir_abs.append(os.path.abspath(lis_dir[i])+'/')
            lis_dir[i]=''
        else:
            lis_dir_abs.append(os.path.abspath(lis_dir[i]))
            lis_dir[i]=lis_dir[i].split("/")[-1]
        '''if lis_dir[i].startswith('..'):
            if lis_dir[i].endswith('/'):
                chemin_abs=os.getcwd().split("/")
                chemin = lis_dir[i].split("/")
            while len(chemin) > 0 and chemin[0] == '..':
                    chemin_abs.pop()
                    chemin.pop(0)
            lis_dir[i]="/".join([chemin_abs[-1]]+chemin)
        elif lis_dir[i].startswith('./'):
            lis_dir[i]=lis_dir[i][2:]
        elif lis_dir[i] == './':
            lis_dir[i]=''
        elif lis_dir[i]=='.':
            lis_dir[i]=os.getcwd().split("/")[-1]'''
        i += 1
    i = 0
    while i < len(lis_dir) :
        j = i+1
        while j < len(lis_dir) :
            if lis_dir_abs[i] == lis_dir_abs[j] :
                del lis_dir[j]
                del lis_dir_abs[j]
            j += 1
        i += 1
    return lis_dir_abs,lis_dir

def filelist(lis_dir,dic,whoami):
    if dic['-v'] :
        print('building file list {} ... '.format(whoami), end=('' if dic['-v'] < 3 else '\n'))
    file_list = []
    lis_dir_abs,lis_dir = norm_liste_dir(lis_dir,dic)
    if dic['-v'] > 2 :
        print('list {} normalized'.format(whoami))
    for i in range(len(lis_dir_abs)):
        file_list = file_list + parcours(lis_dir_abs[i],lis_dir[i],dic,whoami)
    if dic['-v'] :
        print('{}done'.format('' if dic['-v'] < 3 else whoami + ' '))
    return file_list

#on affiche le nom local, que faire quand plusieurs repertoires differents ? plus englobant ?
#le list-only dossier/ n'affiche pas le .