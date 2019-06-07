import sys
import getopt
import paramiko
import os

serverIP = None
passWord = None
configFilePath = None

opts, args = getopt.getopt(sys.argv[1:], 'i:p:c:', '')

for option, value in opts:
    if option == '-i':
        serverIP = value
    elif option == "-p":
        passWord = value
    elif option == "-c":
        configFilePath = value

if not serverIP or not passWord or not configFilePath:
    print("Need more params")
    sys.exit(-1)

configFilePath = os.path.abspath(configFilePath)
if not os.path.exists(configFilePath):
    print("Config file not exists: %s" % configFilePath)
    sys.exit(-1)

print("ssh connecting...")

ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(serverIP, port=22, username="root", password=passWord)

command = 'apt-get update'
print("\n+ %s" % command)
stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

for line in iter(stdout.readline, ""):
    print(line, end="")

command = "apt-get -y install python3-pip"
print("\n+ %s" % command)
stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

for line in iter(stdout.readline, ""):
    print(line, end="")

command = "pip3 install shadowsocks"
print("\n+ %s" % command)
stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

for line in iter(stdout.readline, ""):
    print(line, end="")

print("\n+ scp shadowsocks.json")
sftp_client = ssh.open_sftp()
sftp_client.put(configFilePath, "/etc/shadowsocks.json")

command = "sed -i -- 's/xx/%s/g' /etc/shadowsocks.json" % serverIP
print("\n+ %s" % command)
stdin, stdout, stderr = ssh.exec_command(command)

command = "sed -i -- 's/cleanup/reset/g' /usr/local/lib/python3.6/dist-packages/shadowsocks/crypto/openssl.py"
print("\n+ %s" % command)
stdin, stdout, stderr = ssh.exec_command(command)

command = "ssserver -c /etc/shadowsocks.json"
print("\n+ %s" % command)
stdin, stdout, stderr = ssh.exec_command(command)

ssh.close()

print(u"\n\U0001F37A SS established. Happy hacking, commander!")
