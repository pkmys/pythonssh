from __future__ import print_function
try:
    import paramiko
    import getpass
    import socket
    import errno
    import sys
    import os
except ImportError, e:
    print(e, "install missing package using pip")
    exit()

destDir = os.getcwd()
PATH = "/"

def clear():

    if ('nt' in sys.platform or 'win32' in sys.platform):
        _ = os.system('cls')

    else:
        _ = os.system('clear')


def isValidIP(ip):
    try:
        if(ip == "localhost"):
            return True
        else:
            socket.inet_aton(ip)
            return True
    except socket.error, e:
        print(e, "check your input")
        return False


def rexists(sftp, path):
    """os.path.exists for paramiko's SCP object
    """
    try:
        sftp.stat(path)
    except IOError, e:
        if e.errno == errno.ENOENT:
            return False
        raise
    else:
        return True


def pathBuilder(xpath,sftp):
    global PATH
    spPath = PATH.split('/')
    xpath.lstrip(" ")
    if(xpath[0] == '/'):
        if(rexists(sftp,xpath)):
            PATH=xpath
    else:
        lpath = xpath.split('/')
        for upath in lpath:
            if(PATH=="/" and (upath == '..' or upath == '.')):
                continue
            else:
                if(upath == '..'):
                    spPath=spPath[:-1]
                    tpath='/'.join(spPath)
                    if(rexists(sftp,tpath)):
                        PATH=tpath
                elif(upath=='.'):
                    continue
                elif(upath==''):
                    continue
                else:
                    tpath=PATH+'/'+upath
                    if(rexists(sftp,tpath)):
                        PATH=tpath


def browse(session, sftp):
    global destDir
    global PATH
    input = ""
    print('''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                 PARAMIKO-SCP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
(C) 2018 Pawan Kumar

 @Usage: 
      exit<"exit","logout","cntl+c"      >
      scp <use absolute path or cd to dir>
	  <then issue "scp FILENAME"     >
 
 <To issue a command in a particular dir. use >
 <cd /path/to/dir[ENTER] then issue command   >
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''')

    while(1):
        print("paramikoscp:"+PATH+"> ", end="")
        input = raw_input()
        if(input == "exit" or input == "logout" or input == "quit"):
            break
        
        input=input.lstrip(' ')
        if(input[:3] == "cd "):
            pathBuilder(input[3:],sftp)

        if(input[:4] == "scp "):
            srcPath = PATH
            destDir = destDir+"/"+input[4:]
            srcPath = srcPath+"/"+input[4:]

            try:
                sftp.get(srcPath, destDir)
                print("scp: file copied successfully"+"<"+srcPath+">")
                continue
            except:
                print("scp: unable to complete operation [Internal Error]")
                continue

        if("clear" in input):
            clear()
            continue
        else:
            stdin, stdout, stderr = session.exec_command("cd "+PATH+";"+input)

        for line in iter(stdout.readline, ""):
            print(line, end="")


def mainscp(local, *args):

    global PATH

    if(len(args) == 0 and local == True):
        session = paramiko.SSHClient()
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

    if(isValidIP(mgmtIP)):
        session.connect(hostname=mgmtIP, username=user, password=passwd)
        transport = paramiko.Transport((mgmtIP, 22))
        transport.connect(username=user, password=passwd)
        sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        PATH="/home/"+user
        browse(session, sftp)
    except KeyboardInterrupt:
        print("Connection closed")


if(__name__ == "__main__"):
    try:
        mainscp(True)
    except:
        print("unknown error")
