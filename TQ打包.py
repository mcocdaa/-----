'''
TQ数据打包成事例级别
'''
import numpy
import os
import ROOT
def TQ打包(time,ChCount,TQ_chargePE,TriW=64,TriN=5,EndW=3500,EndN=2):
    '''
    触发TQ打包窗口为64单位时时间,内五个击中,记录(如果TriN=1以第一个事例立刻触发)
    触发后结束窗口时间宽度为3500,阈值2个(窗口内低于两个(==1)就结束,如果要立刻结束窗口应该设置EndW<0)
    '''
    assert EndN>1
    PMTID=[]#一个Event的pmt
    PMTQT=[]#一个Event的时间
    PMTPE=[]#一个Event的pmtPE
    Qhits=[]#sum(TQ_hitCount)
    TQ_firsthitTime=[]
    fired_PMT=[]
    SumCharge=[]

    indextime=numpy.argsort(time)
    EventNum=len(indextime)
    INDEXMAX=100#保存ROOT文件需要大的矢量，我也不知道为什么，反正这样没问题
    firstindex=0
    while firstindex<EventNum-TriN+1:
        isit=False
        for index in range(firstindex,EventNum-TriN+1):
            if (time[indextime[index+TriN-1]]-time[indextime[index]])<TriW:
                isit=True
                firstindex=index
                break
        if isit:
            endindex=EventNum
            for index in range(firstindex+1,EventNum):
                if (time[indextime[index]]-time[indextime[firstindex]])>TriW:
                    endindex=index
                    break
            for index in range(firstindex,EventNum-EndN+1):
                if (time[indextime[index+EndN-1]]-time[indextime[index]])>EndW:
                    if index!=firstindex: endindex=index+EndN-1
                    break
            PMTID.append(ChCount[indextime[firstindex:endindex]])
            PMTQT.append(time[indextime[firstindex:endindex]])
            PMTPE.append(TQ_chargePE[indextime[firstindex:endindex]])
            SumCharge.append(numpy.sum(PMTPE[-1]))
            fired_PMT.append(len(set(PMTID[-1])))
            TQ_firsthitTime.append(PMTQT[-1][0])
            Qhits.append(endindex-firstindex)
            INDEXMAX=max(INDEXMAX,endindex-firstindex+10)
            firstindex=endindex
        else:
            break
    return PMTID,PMTQT,PMTPE,Qhits,TQ_firsthitTime,fired_PMT,SumCharge,INDEXMAX

def 读取TQ(path,filename):
    file=ROOT.TFile.Open(os.path.join(path,filename))
    RDF=ROOT.RDataFrame(file.tree)#n_sec #n_nsec#clusterCharge#

    RDF1=RDF

    data=RDF1.AsNumpy(["times","Charge","PeakTime","Channel","n"])
    ChCount=[]
    TQ_chargePE=[]
    timeofQ=[]
    a=1;b=1###############################
    for evti in range(len(data["times"])):
        for hitj in range(data["n"][evti]):
            timeofQ.append(data["times"][evti]+data["PeakTime"][evti][hitj]*a-b)
            TQ_chargePE.append(data["Charge"][evti][hitj])
            ChCount.append(data["Channel"][evti])
    ChCount=numpy.array(ChCount,dtype=int)
    TQ_chargePE=numpy.array(TQ_chargePE)
    timeofQ=numpy.array(timeofQ)

    sorttime=numpy.argsort(timeofQ)
    timeofQ=timeofQ[sorttime]#有没有这个是一样的
    TQ_chargePE=TQ_chargePE[sorttime]
    ChCount=ChCount[sorttime]
    return timeofQ,TQ_chargePE,ChCount

from . import 输出到文件

if __name__=='__main__':
    savepath='./root保存/Event.root'
    timeofQ,TQ_chargePE,ChCount=读取TQ('./root保存/','waveform_TQ.root')
    PMTID,PMTQT,PMTPE,Qhits,TQ_firsthitTime,fired_PMT,SumCharge,INDEXMAX\
        =TQ打包(timeofQ,ChCount,TQ_chargePE,TriW=64,TriN=1,EndW=-3500,EndN=2)
    
    输出到文件.savefile(savepath,
                 {
                    'ChID':PMTID,
                    'hittime':PMTQT,
                    'hitPE':PMTPE,
                    'Qhits':Qhits,
                    'TQ_firsthitTime':TQ_firsthitTime,
                    'fired_Ch':fired_PMT,
                    'SumCharge':SumCharge,
                  },{
                    'ChID':([INDEXMAX],"i","/I"),
                    'hittime':([INDEXMAX],"d","/D"),
                    'hitPE':([INDEXMAX],"d","/D"),
                    'Qhits':([],"i","/I"),
                    'TQ_firsthitTime':([],"d","/D"),
                    'fired_Ch':([],"i","/I"),
                    'SumCharge':([],"d","/D"),
                    }
                  )