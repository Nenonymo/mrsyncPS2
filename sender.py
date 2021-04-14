import filelist

dir="/home/kf/Bureau/test"
dict={'-r':True}

file_list = filelist.parcours(dir,dict)
for elt in file_list:
    print(elt)

