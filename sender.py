import filelist

def send_listonly(dir,dict):
    file_list = filelist.parcours(dir,dict)
    for elt in file_list:
        print(elt)

def send_local(dir,dict):
    file_lists = filelist.parcours(dir,dict)
    return file_lists
