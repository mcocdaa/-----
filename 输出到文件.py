'''
一些输出到文件
'''
import ROOT
import os
import array
##########尽量不调用区域##########

def copyarray(a,b):
    #copy b[:]=a[:]
    while len(b)!=len(a):
        break#########################
        if len(b)<len(a):
            b.append(0)
        else:
            b.pop()
    for i in range(len(a)):
        b[i]=a[i]

def savefile(path,file,shape,TreeName='tree'):
    '''
    实现保存文件Tree功能,如果path存在则追加,不存在则创建
    输入
    path:文件路径及文件名
    file:字典,key为变量名,value为变量值 [事例1值,...]
    shape:字典,key为变量名,value为(每个事例的形状,type in array,type in tree)
        每个事例的形状:[]表示单值,[n]表示第一维最多有n个值!!n必须大于所有可能长度!!
    输入例子
    savefile(savepath,
            {
            'EVENT':numpy.arange(len(ID)),
            'ID':ID,
            'Q':Q,
            'X':X,
            'BOOLdata':BOOLdata,
            },{
            'EVENT':([],"L","/l"),###python2 "L"表示Uint64 python3使用"Q"
            'ID':([INDEXMAX+1],"i","/I"),#H,/s
            'Q':([INDEXMAX+1],"L","/l"),
            'X':([INDEXMAX+1],"d","/D"),
            'BOOLdata':([],"H","/s"),
            }
            )
    
    TTree的Branch的type:
    C : a character string terminated by the 0 character
    B : an 8 bit signed integer (Char_t)
    b : an 8 bit unsigned integer (UChar_t)
    S : a 16 bit signed integer (Short_t)
    s : a 16 bit unsigned integer (UShort_t)
    I : a 32 bit signed integer (Int_t)
    i : a 32 bit unsigned integer (UInt_t)
    F : a 32 bit floating point (Float_t)
    f : a 24 bit floating point with truncated mantissa (Float16_t)
    D : a 64 bit floating point (Double_t)
    d : a 24 bit truncated floating point (Double32_t)
    L : a 64 bit signed integer (Long64_t)
    l : a 64 bit unsigned integer (ULong64_t)
    G : a long signed integer, stored as 64 bit (Long_t)
    g : a long unsigned integer, stored as 64 bit (ULong_t)
    O : [the letter o, not a zero] a boolean (Bool_t)

    python3_array must be b, B, u, h, H, i, I, l, L, q, Q, f or d
    python2_array must be b, B, u, h, H, i, I, l, L,       f or d ,c (character)
    b signed char       1
    B unsigned char     1
    u py_UNICODE        2
    h signed short int  2
    H unsigned short int2
    i signed int        2
    I unsigned int      2 uint16
    l signed long       4 
    L unsigned long     4 uint32
    q signed long long  8
    Q unsigned long long8 uint64
    f float             4
    d double            8
    csq
    '''
    exist0=True
    bianlianglist={}
    if not os.path.exists(path):
        exist0=False
        print("# path not exists")
        outfile= ROOT.TFile(path, "UPDATE")
        tree=ROOT.TTree(TreeName,TreeName)
        for i in shape:
            if len(shape[i][0])==0:
                bianlianglist[i]=array.array(shape[i][1],[0])
                tree.Branch(i,bianlianglist[i],i+shape[i][2])
            elif len(shape[i][0])==1:
                if 'n' not in bianlianglist:
                    bianlianglist['n']=array.array('I',[0])
                    tree.Branch('n',bianlianglist['n'],'n/i')
                bianlianglist[i]=array.array(shape[i][1],[0]*shape[i][0][0])
                tree.Branch(i,bianlianglist[i],i+'[n]'+shape[i][2])
            else:
                print('wrong!csqhaimeibian')
    else:
        outfile= ROOT.TFile(path, "UPDATE")
        tree=outfile.tree
        for i in shape:
            if len(shape[i][0])==0:
                bianlianglist[i]=array.array(shape[i][1],[0])
                tree.SetBranchAddress(i,bianlianglist[i])
            elif len(shape[i][0])==1:
                if 'n' not in bianlianglist:
                    bianlianglist['n']=array.array('I',[0])
                    tree.SetBranchAddress('n',bianlianglist['n'])
                bianlianglist[i]=array.array(shape[i][1],[0]*shape[i][0][0])
                tree.SetBranchAddress(i,bianlianglist[i])
            else:
                print('wrong!haimeibian')
    N=len(file[list(file.keys())[0]])
    for i in range(N):
        for x in shape:
            if len(shape[x][0])==0:
                bianlianglist[x][0]=file[x][i]
            elif len(shape[x][0])==1:
                bianlianglist['n'][0]=len(file[x][i])
                copyarray(file[x][i],bianlianglist[x])
            else:
                print('wrong!haimeibian')
        tree.Fill()
    #outfile.WriteObject(tree,'tree')#这会导致重复存储
    tree.Write("",ROOT.TObject.kOverwrite)
    outfile.Close()
    print('文件已保存')
