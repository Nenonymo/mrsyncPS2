import os, sys, options, sender

if __name__ == '__main__' :
    dic, files, dest = options.parser(sys.argv)
    
    if dic['--list-only'] :
        sender.send_listonly(files, dic)
    else : #si local
        sr_r,sr_w = os.pipe()
        rs_r,rs_w = os.pipe()
        pid=os.fork()
        if pid == 0 :
            server_local(files,dest,dic,sr_r,rs_w)
        else :
            send_local(files,dic,sr_w,rs_r)