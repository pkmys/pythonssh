from __future__ import print_function
try:
    import paramikoscp
    import pexpect
    import getpass
    import socket
    import sys
    import os
    import re

except ImportError, e:
    print(e, "try installing missing packages using pip")
    exit()

destDir = os.getcwd()
os.environ['http_proxy'] = ''
promptType='$ '


def login(user, mgmtIP, passwd):
    child = pexpect.spawn("ssh "+user+"@"+mgmtIP)
    i = child.expect("password:")
    if (i == 0):
        child.sendline(passwd)
    else:
        return -1
    i = child.expect(["Permission denied", user+"@.*:.*[#/$] "])

    if(i == 0):
        print("permission denied")
        child.kill(0)
        return -1
    else:
        return child


def posixmain():

    global destDir
    global promptType

    user = raw_input("enter username: ")
    mgmtIP = raw_input("enter management IP: ")
    if(paramikoscp.isValidIP(mgmtIP)):
        passwd = getpass.getpass(prompt=user+"@"+mgmtIP+"'s password:")
        child = login(user, mgmtIP, passwd)
        scpObj = paramikoscp.mainscp(False, mgmtIP, user, passwd)

    if (child == -1):
        print("login failed")
        return -1
    else:
        input = ""
        prev = ""
        if(user=="root"):
            promptType='# '
        child.before = '''

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    PYSSH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
(C) 2018 Pawan Kumar

 @Usage: 
      exit<"exit","logout","cntl+c"      >
      ????????????????????????????????????
       vim not supported use cat instead
      ????????????????????????????????????
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pyssh:'''
        try:
            while (input != "exit" or input != "logout"):
                out = child.before.strip(prev+'\r\n')
                input = raw_input(out+promptType)
                prev = input
                input.lstrip(" ")
                if(input[:4] == "scp "):
                    child.sendline("ls "+input[4:])
                    child.expect("[#/$] ")
                    tmpOut = child.before

                    fileName = input[4:]
                    tmpOut = tmpOut.split('\r\n')

                    if("No such file or directory" not in tmpOut[1]):
                        child.sendline("pwd")
                        child.expect("[#/$] ")
                        tmpOut = child.before
                        tmpOut = tmpOut.split('\r\n')

                        srcDir = tmpOut[1]+"/"+fileName
                        destDir = destDir+"/"+fileName

                        try:
                            scpObj.get(srcDir, destDir)
                        except:
                            print(
                                "scp: unable to complete operation [Internal Error]")
                            prev = tmpOut[0]+'\r\n'+tmpOut[1]
                            continue
                        print("scp: file copied successfully" +
                              "<"+tmpOut[0]+">")
                        prev = ""
                        continue

                    else:
                        print("scp: file not found"+"<"+tmpOut[0]+">")
                        prev = tmpOut[-2]
                        continue

                elif(input[:5] == "sudo "):
                    child.sendline(input)
                    i = child.expect([".*password.*", "[#/$] "])
                    if(i == 0):
                        child.sendline(passwd)
                        i = child.expect(["Permission denied", "[#/$] "])
                        if(i == 0):
                            print("Default password not valid, re-enter password")
                            rootpw = getpass.getpass("passord:")
                            child.sendline(input)
                            i = child.expect([".*password.*", "[#/$] "])
                            if(i == 0):
                                child.sendline(rootpw)
                                i = child.expect(["Permission denied", "[#/$] "])
                                if(i == 0):
                                    promptType='$ '
                                    continue
                            else:
                                continue
                            child.expect("[#/$] ")
                    promptType='# '
                    continue
                if(input == "exit"):
                    promptType='$ '

                child.sendline(input)
                child.expect("[#/$] ")

        except Exception:
            pass
        child.kill(0)


if (__name__ == "__main__"):
    try:
        if "linux" in sys.platform:
            posixmain()
        else:
            print("This code is not supported on "+sys.platform)
    except KeyboardInterrupt, e:
        print(e, "KeyboardInterrupt")
    except socket.error, e:
        print(e, "check your input")
    except Exception, e:
        print(e, "please try again")
    finally:
        print("connection closed")
