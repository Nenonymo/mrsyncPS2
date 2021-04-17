import os, sys, options, sender

if __name__ == '__main__' :
    dic, files, dest = options.parser(sys.argv)
    
    if dic['--list-only'] :
        sender.send_listonly(files, dic)
