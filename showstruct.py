import gdb
import re

class showStruct(gdb.Command):

    
    """showstruct
    Usage: showstruct [struct] [address]
    Example:
        (gdb) showstruct _IO_FILE_plus stdout
    """

    def __init__(self):
        super().__init__("showstruct", gdb.COMMAND_USER)


    def invoke(self, args, from_tty):
        argv = gdb.string_to_argv(args)
        if len(argv) == 1:
            raise gdb.GdbError('argc wrong! `help showstruct` for help ')
        if argv[0] == 'struct':
            raise gdb.GdbError('no need for struct')
        command='p *(struct '+argv[0]+" *) "+argv[1]
        #print(command)
        raw=gdb.execute(command,to_string=True)
        ls=trans2list(raw)
        printResult(command,ls)



def find_index_couple(str,index):
    deep=0
    for i in range(index,len(str)):
        if str[i]=='{':
            deep=deep+1
        if str[i]=='}':
            deep=deep-1
            if deep==0:
                return i

def __str2list(_str):
    ls=[]
    temp=_str
    begin=0
    while temp.find('{') != -1 :
        a=_str.find('{',begin)
        b=find_index_couple(_str,a)
        begin=begin+b+1
        flag="###"+str(a+1)+"###"+str(b)+"###"
        aa=temp.find('{')
        bb=find_index_couple(temp,aa)
        temp=temp[:aa]+flag+temp[bb+1:]       
    ls=re.split("[,]+",temp)
    while "" in ls:
        ls.remove("")
    for i in range(len(ls)):
        while ls[i][0]==' ' :
            ls[i]=ls[i][1:]
    return ls

def creat_stuct(ls):
    for i in range(len(ls)):
        if ls[i].find("###") == -1:
            _ty="NORMAL"
        else:
            _ty="_RECURSE"
        lls=ls[i].split(" = ")
        lls.insert(0,_ty)
        ls[i]=lls
    return ls
        
def recurse2list(Init,cursestr):
    match=re.match(r'###(.*)###(.*)###',cursestr)
    cursestr=match.group(0)
    [a,b]=cursestr[3:-3].split("###")
    a=int(a)
    b=int(b)
    transd=Init[a:b]
    result=_str2list(transd,transd)
    return result

def checkfini(Init,ls):
    for i in range(len(ls)):
        if ls[i][0] == "_RECURSE":
            ret=recurse2list(Init,ls[i][2])
            tmp=ls[i]
            ls[i][0] = "RECURSE"
            ls[i][2] = ret
    return ls

def _str2list(Init,s):
    ls=__str2list(s)
    ls=creat_stuct(ls)
    ls=checkfini(Init,ls)
    return ls

def trans2list(s):
    content=s[1:-1].replace('\n','')
    Init=content
    result = _str2list(Init,content)
    return result

def printResult(command,ls):
    ls=ls[0][2]
    command="p &("+command[1:]+")"
    #print(command)
    _printResult(command,ls)

def _printResult(typ,ls):
    output=""
    for i in range(len(ls)):
        if ls[i][0] == 'RECURSE' :
            print(ls[i][1])
            typp=typ+"->"+ls[i][1]
            _printResult(typp,ls[i][2])
        else:
            member=ls[i][1]
            line = getaddr(typ,member)
            line = line +"\t\x1b[0;34m"+ls[i][1]+" = \x1b[1;93m"+ls[i][2] +"\x1b[0m"
            output=output+line+"\n"
    print(output)
            
def getaddr(typ,member):
    command = typ+"->"+member
    addrs=gdb.execute(command,to_string=True)
    return addrs.strip('\n')

showStruct()
