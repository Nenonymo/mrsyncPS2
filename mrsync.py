import os, sys, options, sender, server

if __name__ == '__main__' :
    dic, files, dest = options.parser(sys.argv)
    
    if dic['--list-only'] :
        sender.send_listonly(files, dic)
    else : #si local
        sr_r,sr_s = os.pipe()
        gs_s,gs_g = os.pipe()
        pid=os.fork()
        if pid == 0 :
            server.server_local(files,dest,dic,gs_g,sr_r)
        else :
            sender.send_local(files,dic,gs_s,sr_s)