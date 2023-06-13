from __future__ import print_function, division
import sys, os
import csv, json
import numpy as np
from scipy.interpolate import interp1d
import scipy.stats as stats 
import pickle
import ROOT
import matplotlib.pyplot as plt
import lmfit

def ftest_fail_temp_QCD(year, region = 'c', syst='nominal'):
    '''
    region: charm: 'c' or light: 'l'
    '''
    
    #First link the signal region root file to the correct directory
    linkdir= "/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/hbb-coffea/vh_combine/allyears_Oct19_masscut_functional/"
    os.system("ln -s {}/signalregion.root {}-mc/".format(linkdir+year, year))

    f = ROOT.TFile.Open('{}-mc/signalregion.root'.format(year))

    #Determind the right branch
    branch_name = '{}_fail_{}_{}'.format(region,'QCD',syst)

    print("Extracting ... ", branch_name)
    h = f.Get(branch_name)
    
    if not h:
        raise Exception("Can't retrieve the histogram from root file")
    
    #Get the data from the histogram
    x_data = []
    y_data = []
    y_err = []
    
    for i in range(1,h.GetNbinsX()+1):

        #x axis is msd
        msd_bin_center = h.GetXaxis().GetBinCenter(i)
        x_data.append(msd_bin_center)

        #get bin value and uncertainty
        y_data.append(h.GetBinContent(i))
        y_err.append(h.GetBinError(i))
    
    #TODO: from phil's code, but need to ask what's the best weights here!   
    weights = np.linspace(0.,len(y_data),num=len(y_data))
    for i0 in range(len(y_data)):
        weights[i0] = float(1./y_err[i0])
    
    #Define a bunch of polynomial functions
    def pol0(x,p0):
        pols=[p0]
        y = np.polyval(pols,x)
        return y

    def pol1(x,p0,p1):
        pols=[p0,p1]
        y = np.polyval(pols,x)
        return y

    def pol2(x, p0, p1,p2):
        pols=[p0,p1,p2]
        y = np.polyval(pols,x)
        return y

    def pol3(x, p0, p1,p2,p3):
        pols=[p0,p1,p2,p3]
        y = np.polyval(pols,x)
        return y

    def pol4(x, p0, p1,p2,p3,p4):
        pols=[p0,p1,p2,p3,p4]
        y = np.polyval(pols,x)
        return y

    def pol5(x, p0, p1,p2,p3,p4,p5):
        pols=[p0,p1,p2,p3,p4,p5]
        y = np.polyval(pols,x)
        return y
    
    #
    def fitModel(iX,iY,iWeights,iFunc):
        model  = lmfit.Model(iFunc)
        p = model.make_params(p0=0,p1=0,p2=0,p3=0,p4=0,p5=0)
        result = model.fit(data=iY,params=p,x=iX,weights=iWeights)
        #result = lmfit.minimize(binnedLikelihood, params, args=(iX,iY,(iY**0.5),iFunc))
        output = model.eval(params=result.params,x=iX)
        return output

    result0 = fitModel(x_data,y_data,weights,pol0)
    result1 = fitModel(x_data,y_data,weights,pol1)
    result2 = fitModel(x_data,y_data,weights,pol2)
    result3 = fitModel(x_data,y_data,weights,pol3)
    result4 = fitModel(x_data,y_data,weights,pol4)
    result5 = fitModel(x_data,y_data,weights,pol5)
    
    #Plot the fit results
    plot_dir = '{}-mc/plots'.format(year)
    os.system('mkdir -p {}'.format(plot_dir))
    
    #Calculate Chi^2
    def chi2(iY, iFunc, iYErr, iNDOF): #TODO: Phil used iNDOF incorrectly in his notebook???? iNDOF = 3 if poly order = 3??
        resid = (iY-iFunc)/iYErr
        chi2value = np.sum(resid**2)
        chi2prob=1-stats.chi2.cdf(chi2value,len(iY)-iNDOF)
        print('NDOF: {}, Mean: {}, STD: {}, Chi2 Prob: {}'.format(iNDOF, resid.mean(), resid.std(), chi2prob))
        return chi2value/(len(iY)-iNDOF)
    
    #Some extra labeling
    plt.plot([],[],'none',label='{} {}'.format(year, 'Charm' if region=='c' else 'Light'))
    plt.errorbar(x_data, y_data, yerr=y_err, fmt='.k', label='Bin value')
    plt.plot(x_data,result0,label=r"pol0, Norm $\chi^2$ = {}".format(round(chi2(y_data, result0, y_err, 1), 2)))
    plt.plot(x_data,result1,label=r"pol1, Norm $\chi^2$ = {}".format(round(chi2(y_data, result1, y_err, 2), 2)))
    plt.plot(x_data,result2,label=r"pol2, Norm $\chi^2$ = {}".format(round(chi2(y_data, result2, y_err, 3), 2)))
    plt.plot(x_data,result3,label=r"pol3, Norm $\chi^2$ = {}".format(round(chi2(y_data, result3, y_err, 4), 2)))
    plt.plot(x_data,result4,label=r"pol4, Norm $\chi^2$ = {}".format(round(chi2(y_data, result4, y_err, 5), 2)))
    plt.plot(x_data,result5,label=r"pol5, Norm $\chi^2$ = {}".format(round(chi2(y_data, result5, y_err, 6), 2)))
    
    #plt.fill_between(msd, np.asarray(y_value) - np.asarray(y_err), np.asarray(y_value) + np.asarray(y_err), alpha=0.2, label='95% CL', color='C1')
    plt.xlabel(r' Jet 1 $m_{sd}$ [GeV]')
    plt.ylabel('Events')
    plt.legend()
    plt.savefig("{}/{}_{}.pdf".format(plot_dir, year, region))
    plt.close()

    #Ftest here
    def residual2(iY,iFunc,iYErr):
        residual = (iY-iFunc)/iYErr #TODO: The original code doesn't include iYerr
        return np.sum(residual**2)
        
    def ftest(iY,iYerr,f1,f2,ndof1,ndof2):
        r1=residual2(iY,f1,iYerr)
        r2=residual2(iY,f2,iYerr)
        
        sigma2group=(r1-r2)/(ndof2-ndof1)
        sigma2=r2/(len(y_data)-ndof2)
        
        return sigma2group/sigma2

    f10=ftest(y_data,y_err,result0,result1,1,2)
    f21=ftest(y_data,y_err,result1,result2,2,3)
    f32=ftest(y_data,y_err,result2,result3,3,4)
    f43=ftest(y_data,y_err,result3,result4,4,5)
    f54=ftest(y_data,y_err,result4,result5,5,6)

    #Overall plot
    xrange=np.linspace(0,300,100)
    
    #TODO: This cdf calculation looks sketch, check with Phil.
    farr=1-stats.f.cdf(xrange,1,len(y_data)-1) #number of bins - 5 floating parameters
    fig, ax = plt.subplots(figsize=(9,6))

    plt.plot([],[],'none',label='{} {}'.format(year, 'Charm' if region=='c' else 'Light'))
    ax.axvline(x=f10,linewidth=2,c='b',label='0 to 1')
    ax.axvline(x=f21,linewidth=2,c='g',label='1 to 2')
    ax.axvline(x=f32,linewidth=2,c='purple',label='2 to 3')
    ax.axvline(x=f43,linewidth=2,c='yellow',label='3 to 4')
    ax.axvline(x=f54,linewidth=2,c='orange',label='4 to 5')

    #Labeling
    ax.set_yscale('log')
    plt.plot(xrange,farr,label='f(1,N)')
    plt.legend()
    plt.xlabel('f-statistic')
    plt.ylabel('p-value')
    plt.savefig("{}/{}_{}_ftest_all.pdf".format(plot_dir, year, region))
    plt.close()

    #Zoom in plots
    xrange=np.linspace(0,3,100)
    farr=1-stats.f.cdf(xrange,1,len(y_data)-6) 
    fig, ax = plt.subplots(figsize=(9,6))
    
    plt.plot([],[],'none',label='{} {}'.format(year, 'Charm' if region=='c' else 'Light'))
    ax.axvline(x=f21,linewidth=2,c='g',label='1 to 2')
    ax.axvline(x=f32,linewidth=3,c='purple',label='2 to 3')
    ax.axvline(x=f43,linewidth=3,c='yellow',label='3 to 4')
    ax.axvline(x=f54,linewidth=3,c='orange',label='4 to 5')
    
    #Labeling
    ax.set_yscale('log')
    plt.xlabel('f-statistic')
    plt.plot(xrange,farr,label='f(1,N)')
    plt.ylabel('p-value')
    plt.legend()
    plt.savefig("{}/{}_{}_ftest_zoom.pdf".format(plot_dir, year, region))
    plt.close()

def main():

    #Setting different years depending on 
    if len(sys.argv) < 2:
        print("Enter year")
        return

    global year
    year = sys.argv[1]
    
    print("Running failing QCD fit ftests for: ", year)
    ftest_fail_temp_QCD(year, region='l') #ftests for light region
    ftest_fail_temp_QCD(year, region='c') #ftests for charm region

if __name__ == '__main__':
    year = ""
    main()