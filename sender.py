import filelist

#brouillon

def send_listonly(lis_dir,dict):
    for dir in lis_dir:
        file_list = filelist.parcours(dir,dict)
        for elt in file_list:
            print(elt)

def send_local(dir,dict):
    file_lists = filelist.parcours(dir,dict)
    return file_lists
