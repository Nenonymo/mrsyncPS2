import filelist

def send(dir,dict):
    file_list = filelist.parcours(dir,dict)
    for elt in file_list:
        print(elt)

