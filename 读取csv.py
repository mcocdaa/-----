'''

'''
import numpy
# import csv
import matplotlib.pyplot as plt

def 定基线(
        波形:numpy.ndarray,
        预期基线区间,
        基线方差最小=0,
        预期基线=None,
        预期基线方差=None,
        分bin个数=20,
        考虑bin数=[-2,2],
        ksigma=1,
        学习率=1.0,
        ):
    '''
    '''
    assert len(波形)>分bin个数,'波形长度要大于'+str(分bin个数)
    binN,bins=numpy.histogram(波形,bins=分bin个数,range=预期基线区间)
    #bins (bin0up,...,binNdown)
    maxindex=numpy.argmax(binN)
    binsdown=max(maxindex+考虑bin数[0],0)
    binsup=min(maxindex+考虑bin数[1]+1,len(binN))
    考虑波形=波形[
        numpy.all(
            [波形>bins[binsdown],波形<bins[binsup]],
            axis=0)
        ]
    obs基线=考虑波形.mean()
    obs基线方差=考虑波形.std()
    obs基线方差总=波形.std()
    if ksigma*obs基线方差<obs基线方差总:
        obs基线方差=obs基线方差总
    obs基线方差=max(obs基线方差,基线方差最小)
    wrong=False
    if type(预期基线)!=type(None) and type(预期基线方差)!=type(None):
        if abs(obs基线-预期基线)>ksigma*obs基线方差:
            wrong=True
            if abs(波形.mean()-预期基线)<abs(obs基线-预期基线):
                obs基线=学习率*波形.mean()+(1-学习率)*obs基线
            else:
                obs基线=学习率*obs基线+(1-学习率)*预期基线
        else:
            obs基线=学习率*obs基线+(1-学习率)*预期基线
    return wrong,obs基线,obs基线方差

def 膨胀区间(波形,基线,阈值,前,后,容忍N=[3,5]):
    obs前=前
    k容忍=False
    for i in range(前-1,-1,-1):
        dV=波形[i]-基线
        if dV<0:
            obs前=i
        else:
            k容忍=True
            if dV<阈值: obs前=i
            else:容忍N[0]=0
        if k容忍:容忍N[0]-=1
        if 容忍N[0]<=0:break

    obs后=后
    k容忍=False
    for i in range(后,len(波形)):
        dV=波形[i]-基线
        if dV<0:
            obs后=i
        else:
            k容忍=True
            if dV<阈值: obs后=i
            else:容忍N[1]=0
        if k容忍:容忍N[1]-=1
        if 容忍N[1]<=0:break
    return [obs前,obs后+1]
def bool转区间(布尔列表,只取第一个=False):
    '''
    把True的区间找到(0,end)最后一个不是
    '''
    therange=[]
    lengthofQ=[]
    kofapulse=False
    startpulse=0
    for j in range(0,len(布尔列表)):
        if (布尔列表[j]) and (not kofapulse):
            #print(j)#,end=' ')
            startpulse=j
            kofapulse=True
            continue
        if kofapulse and (not 布尔列表[j]):
            lengthofQ.append(j-startpulse)
            therange.append([startpulse,j])
            kofapulse=False
            if 只取第一个:
                return therange,lengthofQ
    return therange,lengthofQ
    
def 寻峰算法(
        波形,定基线时间,预期基线区间,
        基线方差最小=0.,预期基线=None,预期基线方差=None,
        预期波形长度=10,预期最小波形长度=5,区间连接阈值=2):
    '''
    给定波形(N,)，输出峰位(多个)T0,T1,Q,Tmax,Tmean(按Q加权),基线
    由前~100ns确定基线
    所有时间均为int(index)
    默认波形向下
    '''
    kwrong=0
    wrong,obs基线,obs基线方差=定基线(波形[0:定基线时间],预期基线区间,基线方差最小=基线方差最小,预期基线=预期基线,预期基线方差=预期基线方差)
    kwrong+=wrong
    # wrong,obs基线2,obs基线方差2=定基线(波形,预期基线区间,预期基线=预期基线,预期基线方差=预期基线方差)
    # kwrong+=wrong
    是脉冲=(obs基线-波形)>obs基线方差*5
    区间,_=bool转区间(是脉冲)
    obs区间=[]
    for i,小区间 in enumerate(区间):
        小区间2=膨胀区间(波形,obs基线,obs基线方差,小区间[0],小区间[1],容忍N=[3,5])
        if len(obs区间)>0:
            if obs区间[-1][1]>=小区间2[0]-区间连接阈值:
                obs区间[-1][1]=小区间2[1]
            else:
                if 小区间2[1]-小区间2[0]>=预期最小波形长度:obs区间.append(小区间2)
        else:
            if 小区间2[1]-小区间2[0]>=预期最小波形长度:obs区间.append(小区间2)
    Q=[];TmaxQ=[];TmeanQ=[]
    for i,小区间 in enumerate(obs区间):
        [iin,iout]=小区间
        if iout-iin>预期波形长度:kwrong+=1
        wave=obs基线-波形[iin:iout]
        TmaxQ.append(numpy.argmax(wave)+iin)
        Q.append(numpy.sum(wave))
        TmeanQ.append(numpy.dot(numpy.arange(iin,iout),numpy.abs(wave)/sum(numpy.abs(wave))))
    return kwrong,obs基线,obs基线方差,obs区间,Q,TmaxQ,TmeanQ

def 画图(波形,定基线时间,预期基线区间,obs基线,obs基线方差,obs区间,TmaxQ,TmeanQ,title='',xylabel=['',''],保存位置=''):
    plt.figure(title)
    plt.plot(波形)
    plt.xlim(0,len(波形))
    plt.plot([0,定基线时间],[obs基线,obs基线],color='black',linestyle='--')
    plt.plot([0,定基线时间],[预期基线区间[0],预期基线区间[0]],color='red',linestyle='--')
    plt.plot([0,定基线时间],[预期基线区间[1],预期基线区间[1]],color='red',linestyle='--')
    plt.plot([0,定基线时间],[obs基线-obs基线方差,obs基线-obs基线方差],color='g',linestyle=':')
    plt.plot([0,定基线时间],[obs基线+obs基线方差,obs基线+obs基线方差],color='g',linestyle=':')
    plt.axhline(y=obs基线,color='gray',linestyle=':')
    for ind,litR in enumerate(obs区间):
        plt.axvline(x=litR[0],linestyle='dashed',c='g')
        plt.axvline(x=litR[1],linestyle='dashed',c='r')
        plt.plot([TmaxQ[ind],TmaxQ[ind]],[obs基线,波形[TmaxQ[ind]]],'b--')
        plt.plot([TmeanQ[ind],TmeanQ[ind]],[obs基线,波形[int(TmeanQ[ind])]],'y--')
    plt.title(title)
    plt.xlabel(xylabel[0])
    plt.ylabel(xylabel[1])
    plt.savefig(保存位置)
    plt.close()
    return
def 读取示波器波形(filename):
    '''
    数据格式
    Time(s),CH1(V),CH2(V),CH4(V),t0 = -5e-07s, tInc = 4e-10s,
    -4.996e-07,+1.343352E-02,+1.824256E-02,+1.364244E-02,,
    '''
    times=[]
    Ch=[]
    with open(filename) as f:
        text=f.readlines()
        chnum=len(text[0].split(','))-4
        Ch=[[] for i in range(chnum)]
        for lin in text[1:]:
            data=lin.replace('\n','').split(',')
            times.append(float(data[0]))
            for i in range(chnum):
                Ch[i].append(float(data[i+1]))
    return times,Ch

def 读取txt波形(filename):
    '''
    数据格式
    Record Length: 1030
    BoardID: 31
    Channel: 0
    Event Number: 5
    Pattern: 0x0000
    Trigger Time Stamp: 3817876311
    DC offset (DAC): 0x1C28
    14898, 14898, ...
    '''
    Rec_Length=[]
    BoardID=[]
    Channel=[]
    Event_number=[]
    times=[]
    Ch=[]
    状态=['Rec','Boa','Cha','Eve','Pat','Tri','DC ','WAVE']
    状态i=0
    with open(filename,'r') as f:
        text=f.readlines()
        for line in text:
            line=line.replace('\n','')
            if line[0:3]==状态[状态i]:
                if 状态i==0:Rec_Length.append(int(line[15:]))
                elif 状态i==1:BoardID.append(int(line[9:]))
                elif 状态i==2:Channel.append(int(line[9:]))
                elif 状态i==3:Event_number.append(int(line[14:]))
                elif 状态i==5:times.append(float(line[20:]))
                elif 状态i==6:ChlistforSave=[]
                状态i+=1
                continue
            elif 状态i==7:
                if not line[0:3].isdigit():
                    Ch.append(numpy.array(ChlistforSave,dtype=int))
                    del ChlistforSave
                    状态i=0
                    if line[0:3]==状态[状态i]:
                        Rec_Length.append(int(line[15:]))
                        状态i+=1
                    else:
                        print('what?')
                    continue
                # 每个波形数值=line.split(',')
                # 每个波形数值=[int(x) for x in 每个波形数值]#
                # ChlistforSave.append(每个波形数值)#如果他不是并排的需要改！
                ChlistforSave.append(int(line))
            else:
                print('what?')
                状态i=0
        if 状态i==7:Ch.append(numpy.array(ChlistforSave,dtype=int))
    return Rec_Length,BoardID,Channel,Event_number,times,Ch

def deepcopy(A:list):
    '''
    深度复制
    '''
    A0=[]
    for x in A:
        if type(x)==type([]):
            A0.append(deepcopy(x))
        else:
            A0.append(x)
    return A0

def 多通道波形转单波形(Rec_Length,BoardID,Channel,Event_number,times,Ch):
    '''
    假设单波形
    '''
    N=len(Rec_Length)
    delindex=[]
    for i in range(N):
        if len(Ch[i].shape)==2:
            for j in range(Ch[i].shape[1]):
                Rec_Length.append(Rec_Length[i])
                BoardID.append(BoardID[i])
                Channel.append(Channel[i])
                Event_number.append(Event_number[i])
                times.append(times[i])
                Ch.append(Ch[i][:,j])
            delindex.append(i)

    for i in numpy.sort(delindex)[::-1]:
        del Rec_Length[i],BoardID[i],Channel[i],Event_number[i],times[i],Ch[i]
    return Rec_Length,BoardID,Channel,Event_number,times,Ch

import sys
sys.path.append('/home/csq/代码/工作/一般工作流/小工具/分类回归工具')
sys.path.append('/home/csq/代码/工作')
import 一般工作流.输出到文件 as 输出到文件
def 保存波形到文件(Rec_Length,BoardID,Channel,Event_number,times,Ch,
            基线,
            基线方差,
            击中区间,
            峰Q,
            峰值时间,
            加权时间,
            savepath='',
    ):
    击中区间前=[]
    击中区间后=[]
    hitmax=100
    for x in 击中区间:
        击中区间前_evt=[]
        击中区间后_evt=[]
        hitmax=max(hitmax,len(x))
        for his in x:
            击中区间前_evt.append(his[0])
            击中区间后_evt.append(his[1])
        击中区间前.append(击中区间前_evt.copy())
        击中区间后.append(击中区间后_evt.copy())
    输出到文件.savefile(savepath,
                 {
                    'Rec_Length':Rec_Length,
                    'BoardID':BoardID,
                    'Channel':Channel,
                    'Event_number':Event_number,
                    'times':times,
                    # 'Waveform':Ch,
                    'Baseline':基线,
                    'BaselineStd':基线方差,#sqrt((x-xm)**2/N)
                    'Hittime_Up':击中区间前,
                    'Hittime_Down':击中区间后,
                    'Charge':峰Q,
                    'PeakTime':峰值时间,
                    'AvgTime':加权时间,
                  },{
                    'Rec_Length':([],"i","/I"),
                    'BoardID':([],"i","/I"),
                    'Channel':([],"i","/I"),
                    'Event_number':([],"i","/I"),
                    'times':([],"d","/D"),
                    # 'Waveform':([2000],"d","/D"),
                    'Baseline':([],"d","/D"),
                    'BaselineStd':([],"d","/D"),#sqrt((x-xm)**2/N)
                    'Hittime_Up':([hitmax+1],"i","/I"),
                    'Hittime_Down':([hitmax+1],"i","/I"),
                    'Charge':([hitmax+1],"d","/D"),
                    'PeakTime':([hitmax+1],"d","/D"),
                    'AvgTime':([hitmax+1],"d","/D"),
                    }
                  )
    pass

if __name__=='__main__':
    readpath='/home/csq/工作/宇宙线测量/数据位置/'
    波形显示保存位置='/home/csq/工作/宇宙线测量/波形/'
    root文件保存位置='/home/csq/工作/宇宙线测量/wave0.root'
    import os
    Rec_Length=[]
    BoardID=[]
    Channel=[]
    Event_number=[]
    times=[]
    Ch=[]
    for file in os.listdir(readpath):
        Rec_Length_now,BoardID_now,Channel_now,Event_number_now,times_now,Ch_now=读取txt波形(os.path.join(readpath,file))
        Rec_Length+=Rec_Length_now
        BoardID+=BoardID_now
        Channel+=Channel_now
        Event_number+=Event_number_now
        times+=times_now
        Ch+=Ch_now
    
    # Rec_Length,BoardID,Channel,Event_number,times,Ch=多通道波形转单波形(Rec_Length,BoardID,Channel,Event_number,times,Ch)
    dt=(max(times)-min(times))/1e9*1.0
    print('共记',len(Rec_Length),'在',dt,'=',len(Rec_Length)/dt,'*? Hz',sep=' ')

    基线=[]
    基线方差=[]
    击中区间=[]
    峰Q=[]
    峰值时间=[]
    加权时间=[]
    
    定基线时间=200
    预期基线区间=[13500,16384]#[0,2**4]=[0,16384]
    抽样时间=1#ns
    Chmax=0
    for i in range(len(Rec_Length)):
        波形=Ch[i]
        kwrong,obs基线,obs基线方差,obs区间,Q,TmaxQ,TmeanQ=寻峰算法(
            波形,定基线时间,预期基线区间,基线方差最小=20,预期基线=None,预期基线方差=None,
            预期波形长度=20/抽样时间,预期最小波形长度=10/抽样时间,区间连接阈值=2)
        基线.append(obs基线);基线方差.append(obs基线方差)
        击中区间.append(deepcopy(obs区间))
        峰Q.append(Q.copy())
        峰值时间.append(TmaxQ.copy())
        加权时间.append(TmeanQ.copy())
        画图(波形,定基线时间,预期基线区间,obs基线,obs基线方差,obs区间,TmaxQ,TmeanQ,
        title='Ch'+str(i)+'_wrong'+str(kwrong),
        xylabel=['time/'+str(dt)+'ns','V'],
        保存位置=波形显示保存位置+'Event'+str(i)+'.png')

    保存波形到文件(Rec_Length,BoardID,Channel,Event_number,times,Ch,
            基线,
            基线方差,
            击中区间,
            峰Q,
            峰值时间,
            加权时间,
            savepath=root文件保存位置,
    )