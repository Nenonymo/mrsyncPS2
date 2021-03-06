import os

def parcours_simple(dir,nomLoc,verbose,whoami):
    '''parcours le repertoire dir et ajoute chaque fichier de ce repertoire a la liste de fichier fileList
    ne s'occupe que d'une seule couche

    utilisee dans la fonction parcours si il n'y a pas l'option -r

    input : dir = nom absolu du repertoire parcouru (string)
            nomLoc = nom local du repertoire dir (string)
            verbose = niveau de verbose (int)
            whoami = role du processus (string)
    output : fileList = liste des fichiers dans dir (liste de fichiers)
    un fichier est représenté par un dictionnaire contenant des informations sur celui-ci
            {'name_loc':nom local,'name':nom absolu,'user':propriètaire,'groupe':groupe propriètaire,'mode':permissions,'size':taille,'modtime':date de derniere modification}
    '''
    curr_dir = os.listdir(dir)
    fileList=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        nom = nomLoc +elt
        st = os.stat(name)
        fileList.append({'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime})
        if verbose > 1 :
            print('[{}] file add : {}'.format(whoami,nom))
    return fileList


def parcours_rec(dir,nomLoc,verbose,whoami):
    '''parcours le repertoire dir et ajoute chaque fichier de ce repertoire a la liste de fichier fileList
    parcours recursivement le repertoire dir pour ajouter tous les fichiers de toutes les couches

    utilisee dans la fonction parcours si il y'a l'option -r

    input : dir = nom absolu du repertoire parcouru (string)
            nomLoc = nom local du repertoire dir (string)
            verbose = niveau de verbose (int) 
            whoami = role du processus (string)
    output : fileList = liste des fichiers dans dir (liste de fichiers)
    '''
    curr_dir = os.listdir(dir)
    fileList=[]
    for elt in curr_dir:
        name = os.path.join(dir,elt)
        if nomLoc.endswith('/') or nomLoc == '':
            nom = nomLoc+elt
        else :
            nom=nomLoc+'/'+elt
        if verbose > 1 :
            print('[{}] file add : {}'.format(whoami,nom))
        st = os.stat(name)
        if os.path.isdir(name): #si repertoire on lui applique parcours_rec
            fileList = fileList+[{'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime}]+parcours_rec(name,nom,verbose,whoami)
        else:
            fileList.append({'name_loc':nom,'name':name,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime})
    return fileList


def parcours(dir,nomLoc,dic,whoami):
    '''ajoute le fichier dir a la liste de fichier fileList
    si dir est un repertoire, appelle les fonctions de parcours de repertoire pour ajouter (recursivement ou non)
    les fichiers a l'interieur de dir

    utilisee par la fonction principale fileList

    input : dir = fichier ou repertoire a ajouter a fileList, chemin absolu (string)
            nomLoc = nom local de dir (string)
            dic = dictionnaire des options (dictionnaire)
            whoami = role du processus (string)
    output : fileList = liste des fichiers du repertoire dir (liste de fichier)
    '''
    fileList=[]
    if dic['-r'] : #si -r on parcours recursivement les repertoires
        st = os.stat(dir)
        if os.path.isdir(dir) and dir[-1]!='/' and whoami != 'list-only': #si le nom du repertoire source ne fini pas par /, on envoit juste le repertoire et son contenu car -r
            fileList = [{'name_loc':nomLoc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime}]+parcours_rec(dir,nomLoc,dic['-v'],whoami)
        elif os.path.isdir(dir): #si le nom du repertoire fini par /, on envoit juste son contenu
            if whoami == 'list-only': #si list-only, on affiche aussi le nom du repertoire donc on l'ajoute
                fileList.append({'name_loc':nomLoc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime})
            fileList = fileList + parcours_rec(dir,nomLoc,dic['-v'],whoami)
        else: #dir nest pas un repertoire
            fileList.append({'name_loc':nomLoc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime})
    else :
        st=os.stat(dir)
        if os.path.isdir(dir) and dir[-1]=='/': #si le nom du repertoire fini par /, on envoit son contenu
            if whoami == 'list-only':
                fileList.append({'name_loc':nomLoc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime})
            fileList = fileList + parcours_simple(dir,nomLoc,dic['-v'],whoami)
        else : #si le nom du repertoire source ne fini pas par /, on envoit juste le repertoire et pas son contenu (+ si dir n'est pas un repertoire)
            fileList.append({'name_loc':nomLoc,'name':dir,'user':st.st_uid,'groupe':st.st_gid,'mode':st.st_mode,'size':st.st_size,'modtime':st.st_mtime,'acctime':st.st_atime})
    return fileList


def norm_liste_dir(lis_dir,dic,whoami) :
    '''donne le nom absolu et le nom local qui sera utilisé des fichiers et repertoires de lis_dir

    utilisee par la fonction principale filelist

    input : lis_dir = liste des noms des fichiers et repertoires a traiter (liste de string)
            dic = dictionnaire des options (dictionnaire)
            whoami = role du processus (string) (list-only,receiver,sender)
    output : lis_dir_abs = liste des noms absolus des fichiers et repertoires (liste de string)
            lis_dir = liste des noms locaux ('') des fichiers et repertoires (liste de string)
    '''
    lis_dir_abs=[]
    i = 0
    while i < len(lis_dir) : #on recupere tous les noms absolus et on met a jour les noms locaux
        if lis_dir[i][-1]=='/' and not dic['-d']: #si le repertoire termine par / on l'ajoute car on aura pas la meme fileList si il est la ou non, si dic -d on transfert le repertoire sans ce qu'il y a dedans donc c'est comme si il n'y avait pas /
            lis_dir_abs.append(os.path.abspath(lis_dir[i])+'/')
            if whoami != 'list-only':
                lis_dir[i]=''
        else:
            lis_dir_abs.append(os.path.abspath(lis_dir[i]))
            if whoami != 'list-only':
                lis_dir[i]=lis_dir_abs[i].split('/')[-1]
        i += 1
    i = 0
    while i < len(lis_dir) : #on supprimme les doublons
        j = i+1
        while j < len(lis_dir) :
            if lis_dir_abs[i] == lis_dir_abs[j] :
                del lis_dir[j]
                del lis_dir_abs[j]
            elif whoami == 'list-only' and lis_dir_abs[i][-1] == '/' and lis_dir_abs[i][:-1] == lis_dir_abs[j] :
                del lis_dir[j]
                del lis_dir_abs[j]
            elif whoami == 'list-only' and lis_dir_abs[j][-1] == '/' and lis_dir_abs[j][:-1] == lis_dir_abs[i] :
                del lis_dir[i]
                del lis_dir_abs[i]
                pass
            else:
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
    lis_dir_abs,lis_dir = norm_liste_dir(lis_dir,dic,whoami)
    if dic['-v'] > 1 :
        print('list {} normalized'.format(whoami))
    for i in range(len(lis_dir_abs)): #on traite chaque repertoires donnés dans la source
        file_list = file_list + parcours(lis_dir_abs[i],lis_dir[i],dic,whoami)
    i=0
    while i < len(file_list) : #on supprimme les doublons
        j = i+1
        while j < len(file_list) :
            if file_list[i]['name'] == file_list[j]['name'] :
                del file_list[j]
            else:
                j += 1
        i += 1
    if dic['-v'] :
        print('{}done'.format('' if dic['-v'] < 2 else 'building file list {} '.format(whoami)))
    return file_list