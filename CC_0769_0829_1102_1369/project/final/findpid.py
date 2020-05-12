import os
command="pgrep containerd-shim>allpids.txt"
os.system(command)
with open('allpid.txt','r') as l:
 sline=l.readlines()
sline=[x.strip() for x in sline]
print(sline)

