import os

#si --checksum ajouter the file checksums

def parcours_simple(dir,nom_loc,verbose,whoami):
    '''parcours le repertoire dir et ajoute chaque fichier de ce repertoire a la liste de fichier file_list
    ne s'occupe que d'une seule couche

    utilisee dans la fonction parcours si il n'y a pas l'option -r

    input : dir = nom absolu du repertoire parcouru (string)
            nom_loc = nom local du repertoire dir (string)
            verbose = niveau de verbose (int)
            whoami = role du processus (string)
    output : file_list = liste des fichiers dans dir (liste de fichiers)
    un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
            {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
    '''
    curr_dir = os.listdir(dir)
    file_list=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        nom = nom_loc +elt
        st = os.stat(name)
        file_list.append({'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
        if verbose > 1 :
            print('[{}] file add : {}'.format(whoami,nom))
    return file_list


def parcours_rec(dir,nom_loc,verbose,whoami):
    '''parcours le repertoire dir et ajoute chaque fichier de ce repertoire a la liste de fichier file_list
    parcours recursivement le repertoire dir pour ajouter tous les fichiers de toutes les couches

    utilisee dans la fonction parcours si il y'a l'option -r

    input : dir = nom absolu du repertoire parcouru (string)
            nom_loc = nom local du repertoire dir (string)
            verbose = niveau de verbose (int) 
            whoami = role du processus (string)
    output : file_list = liste des fichiers dans dir (liste de fichiers)
    '''
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
        if verbose > 1 :
            print('[{}] file add : {}'.format(whoami,nom))
        st = os.stat(name)
        if os.path.isdir(name):
            file_list = file_list+[{'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime}]+parcours_rec(name,nom,verbose,whoami)
        else:
            file_list.append({'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list


def parcours(dir,nom_loc,dic,whoami):
    '''ajoute le fichier dir a la liste de fichier file_list
    si dir est un repertoire, appelle les fonctions de parcours de repertoire pour ajouter (recursivement ou non)
    les fichiers a l'interieur de dir

    utilisee par la fonction principale filelist

    input : dir = fichier ou repertoire a ajouter a file_list, chemin absolu (string)
            nom_loc = nom local de dir (string)
            dic = dictionnaire des options (dictionnaire)
            whoami = role du processus (string)
    output : file_list = liste des fichiers du repertoire dir (liste de fichier)
    '''
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
            print(dir)
            st=os.stat(dir)
            file_list.append({'name_loc':nom_loc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime})
    return file_list


def norm_liste_dir(lis_dir) :
    '''donne le nom absolu et le nom local qui sera utilisé (ie '') des fichiers et repertoires de list_dir

    utilisee par la fonction principale filelist

    input : lis_dir = liste des noms des fichiers et repertoires a traiter (liste de string)
    output : lis_dir_abs = liste des noms absolus des fichiers et repertoires (liste de string)
            lis_dir = liste des noms locaux ('') des fichiers et repertoires (liste de string)
    '''
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
    '''cree la liste de fichiers file_list qui contient les fichiers de chaque nom de repertoire/fichier de lis_dir

    utilisee par sender_local et sender_listonly dans sender.py et receiver_local dans receiver.py

    input : lis_dir = liste des noms de fichiers ou repertoires a traiter (liste de string)
            dic = dictionnaire des options (dictionnaire)
            whoami = role du processus (string)
    output : file_list = liste des fichiers de chaque element de lis_dir (liste de fichiers)
    '''
    if dic['-v'] :
        print('building file list {} ... '.format(whoami), end='' if dic['-v'] < 2 else '\n')
    file_list = []
    lis_dir_abs,lis_dir = norm_liste_dir(lis_dir)
    if dic['-v'] > 1 :
        print('list {} normalized'.format(whoami))
    for i in range(len(lis_dir_abs)):
        file_list = file_list + parcours(lis_dir_abs[i],lis_dir[i],dic,whoami)
    if dic['-v'] :
        print('{}done'.format('' if dic['-v'] < 2 else 'building file list {} '.format(whoami)))
    return file_list

#on affiche le nom local, que faire quand plusieurs repertoires differents ? plus englobant ?

#le list-only dossier/ n'affiche pas le .

