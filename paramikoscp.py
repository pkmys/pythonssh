from __future__ import print_function
try:
    import paramiko
    import getpass
    import socket
    import sys
    import os
except ImportError,e:
    print(e, "install missing package using pip")
    exit()

destDir = os.getcwd()

def clear(): 

    if ('nt' in sys.platform or 'win32' in sys.platform): 
        _ = os.system('cls') 
 
    else: 
        _ = os.system('clear') 

def is_valid_ip(ip):
    try:
        if(ip == "localhost"):
            return True
        else:
            socket.inet_aton(ip)
            return True
    except socket.error, e:
        print(e, "check your input")
        return False

def browse(session, sftp):
    input=""
    while(1):
        print("paramikoscp:$ ", end="")
        input = raw_input()
        if(input == "exit" or input == "logout" or input == "quit"):
            break
#        elif(input[:4] == "scp "):
#            try:

        otherInput = input
        srcPath = ""
        while("cd " in otherInput):
            srcPath += otherInput[3:]+"/"
            otherInput=raw_input(input+";")
            input = input+";"+otherInput
            if(otherInput[:4] == "scp "):
                srcPath += otherInput[4:]
                try:
                    sftp.get(srcPath, destDir)
                    print("scp: file copied successfully"+"<"+srcPath+">")
                    continue
                except:
                    print("scp: unable to complete operation [Internal Error]")
                    continue
                print(srcPath)    
                
        if("clear" in input):
            clear()
            continue
        else:
            stdin,stdout,stderr=session.exec_command(input)

        for line in iter(stdout.readline, ""):
            print(line, end="")

def mainscp(local, *args):

    if( len(args) == 0 and local == True):
        session =paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        user = raw_input("enter username: ")
        mgmtIP = raw_input("enter management IP: ")
        passwd = getpass.getpass(prompt=user+"@"+mgmtIP+"'s password:")
    elif(len(args) < 3):
        print("Insufficient arguments, usage: mainscp(False,  mgmtIp, user, passwd)")
        return -1
    else:
        transport = paramiko.Transport((args[0], 22))
        transport.connect(username=args[1], password=args[2])
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp


    if(is_valid_ip(mgmtIP)):
        session.connect(hostname=mgmtIP, username=user, password=passwd)
        transport = paramiko.Transport((mgmtIP, 22))
        transport.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        browse(session, sftp)
    except KeyboardInterrupt:
        print("Connection closed")

if(__name__ == "__main__"):
    mainscp(True)