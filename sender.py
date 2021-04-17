import filelist

#brouillon

def send_listonly(lis_dir,dic):
    file_list=[]
    for dir in lis_dir:
        file_list = file_list + filelist.parcours(dir,dic)
    for elt in file_list:
        print(elt)

def send_local(dir,dic):
    file_lists = filelist.parcours(dir,dic)
    return file_lists
