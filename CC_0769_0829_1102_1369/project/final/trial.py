import re
with open('tee.txt','r') as l:
            sline=l.readlines()
sline=[x.strip() for x in sline]
sline=sline[1]
print(sline)
sline=re.split("\s+",sline)
print(sline[2])
#sline=list(sline)
'''
final=''
index=38
#print(len(sline))
#print(type(sline))
i=0
for x in sline:
 print(x,":",i)
 i+=1
 if(i>=index):
  if(x!=''):
   final=final+
print(final)
'''
