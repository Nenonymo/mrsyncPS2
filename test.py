import os, sys, options, sender, server, filelist,generator

if __name__ == '__main__' :
    dic, src, dest = options.parser(sys.argv)
    
    if dic['--list-only'] :
        sender.send_listonly(src, dic)
    else : #si local
        srcl = filelist.filelist(src,dic)
        if dest[-1] != '/':
            dest = dest + '/'
        destl = filelist.filelist([dest],dic)
        print(srcl)
        print(destl)