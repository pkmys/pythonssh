from __future__ import print_function
try:
    import pexpect
    import getpass
    import socket
    import sys

except ImportError, e:
    print(e, "try installing missing packages using pip")
    exit()


def login(user, mgmtIP):
    child = pexpect.spawn("ssh "+user+"@"+mgmtIP)
    i = child.expect("password:")
    if (i == 0):
        passwd = getpass.getpass(prompt=user+"@"+mgmtIP+"'s password:")
    else:
        return -1
    child.sendline(passwd)
    i = child.expect(["Permission denied", user+"@.*:.*[#\$] "])

    if(i == 0):
        print("permission denied")
        child.kill(0)
        return -1
    else:
        return child


def is_valid_ip(ip):

    if(ip == "localhost"):
        return True
    else:
        socket.inet_aton(ip)
        return True


def posixmain():

    user = raw_input("enter username: ")
    mgmtIP = raw_input("enter management IP: ")
    if(is_valid_ip(mgmtIP)):
        child = login(user, mgmtIP)

    if (child == -1):
        print("login failed")
    else:
        input = ""
        try:
            while (input != "exit" or input != "logout"):
                print(child.before+"$ ", end="")
                input = raw_input()
                child.sendline(input)
                child.expect("[#/$] ")

        except Exception:
            print("connection closed")
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
