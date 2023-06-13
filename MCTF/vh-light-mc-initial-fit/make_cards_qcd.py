from __future__ import print_function, division
import sys, os
import csv, json
import numpy as np
from scipy.interpolate import interp1d
import scipy.stats
import pickle
import ROOT
import pandas as pd
import matplotlib.pyplot as plt

import rhalphalib as rl
rl.util.install_roofit_helpers()
rl.ParametericSample.PreferRooParametricHist = False

# Read the histogram
def get_template(sName, passed, ptbin, cat, obs, syst, muon=False):
    """
    Read msd template from root file
    """

    f = ROOT.TFile.Open('signalregion.root')

    if muon:
        f = ROOT.TFile.Open('muonCR.root')

    #Determind the right branch
    name = 'fail_'

    if passed:
        name = 'pass_'

    if cat == "charm":
        name = 'c_' + name
    elif cat == 'light':
        name = 'l_' + name

    name += sName+'_'+syst

    print("Extracting ... ", name)
    h = f.Get(name)

    sumw = []
    sumw2 = []

    for i in range(1,h.GetNbinsX()+1):
        sumw += [h.GetBinContent(i)]
        sumw2 += [h.GetBinError(i)*h.GetBinError(i)]

    return (np.array(sumw)[1:], obs.binning, obs.name, np.array(sumw2)[1:])

def fit_fail_templ_QCD(sName, passed, ptbin, cat, obs, syst, muon=False):

    f = ROOT.TFile.Open('signalregion.root')

    if muon:
        f = ROOT.TFile.Open('{}/muonCR.root')

    #Determind the right branch
    name = 'fail_'

    if passed:
        name = 'pass_'

    if cat == "charm":
        name = 'c_' + name
    elif cat == 'light':
        name = 'l_' + name

    name += sName+'_'+syst

    print("Extracting ... ", name)
    h = f.Get(name)

    #Perform the fit
    if not h:
        raise Exception("Can't retrieve the histogram from root file")

    #Set poly nomial order from the json file
    with open('initial_vals_poly_{}.json'.format(cat)) as f:
        initial_vals_poly = np.array(json.load(f)['initial_vals'])

    print("Initial poly shape: ",  initial_vals_poly.shape)
    
    #Create the fit poly nomial
    tf_string = "[0]"
    for i in range(initial_vals_poly.shape[0] - 1):
        tf_string += "+ [{}]".format(i+1) + "*x"*(i+1) 
    print("Initial fit function is : ", tf_string)

    fit_function = ROOT.TF1("fa1", tf_string, 40,200)
    h.Fit(fit_function, "Q")

    par = fit_function.GetParameters()
    print('fit results: ', par)

    fit_result = h.GetFunction("fa1")
    
    #error band
    fit_error = ROOT.TH1D("hint", "Fitted function", 23, 40, 201)
    ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(fit_error)

    #Plot the result and get the result
    msd = []
    y_value = []
    y_err = []

    y_value_og = []
    y_err_og = []

    #To return to the template
    sumw = []
    sumw2 = []

    for i in range(1,h.GetNbinsX()+1):

        msd_bin_center = h.GetXaxis().GetBinCenter(i)
        msd.append(msd_bin_center)

        y_value_og.append(h.GetBinContent(i))
        y_err_og.append(h.GetBinError(i))

        fitted_qcd = fit_result(msd_bin_center)
        y_value.append(fitted_qcd)
        y_err.append(fit_error.GetBinError(i))

        sumw += [fitted_qcd]
        sumw2 += [fit_error.GetBinError(i)*fit_error.GetBinError(i)]

    print("PLOTTTING ...")
    os.system('mkdir -p ../plots/')
    plt.errorbar(msd, y_value_og, yerr=y_err_og, fmt='_', label='Bin value')
    plt.plot(msd, y_value,label= 'Fitted values')
    plt.plot([],[],'none',label=tf_string)
    plt.plot([],[],'none',label=r'$\chi^2={}$'.format(round(fit_function.GetChisquare(),2)))
    plt.fill_between(msd, np.asarray(y_value) - np.asarray(y_err), np.asarray(y_value) + np.asarray(y_err), alpha=0.2, label='95% CL', color='C1')
    plt.xlabel(r' Jet 1 $m_{sd}$')
    plt.ylabel('Events')
    plt.legend()
    plt.savefig("../plots/{}_{}_{}.pdf".format(year,name,initial_vals_poly.shape[0] - 1))
    plt.close()

    return (np.array(sumw)[1:], obs.binning, obs.name, np.array(sumw2)[1:])

def get_initial_QCD(sName, passed, ptbin, cat, obs, syst, muon=False):

    f = ROOT.TFile.Open('signalregion.root')

    if muon:
        f = ROOT.TFile.Open('muonCR.root')

    #Determind the right branch
    name = 'fail_'

    if passed:
        name = 'pass_'

    if cat == "charm":
        name = 'c_' + name
    elif cat == 'light':
        name = 'l_' + name

    name += sName+'_'+syst

    print("Extracting ... ", name)
    h = f.Get(name)

    #Perform the fit
    if not h:
        raise Exception("Can't retrieve the histogram from root file")

    #Set poly nomial order from the json file
    with open('initial_vals_poly_{}.json'.format(cat)) as f:
        initial_vals_poly = np.array(json.load(f)['initial_vals'])

    print("Initial poly shape: ",  initial_vals_poly.shape)
    
    #Create the fit poly nomial
    tf_string = "[0]"
    for i in range(initial_vals_poly.shape[0] - 1):
        tf_string += "+ [{}]".format(i+1) + "*x"*(i+1) 
    print("Initial fit function is : ", tf_string)

    fit_function = ROOT.TF1("fa1", tf_string, 40,200)
    h.Fit(fit_function, "Q")

    par = fit_function.GetParameters()
    print('fit results: ', par)

    fit_result = h.GetFunction("fa1")
    
    #error band
    fit_error = ROOT.TH1D("hint", "Fitted function", 23, 40, 201)
    ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(fit_error)

    #Plot the result and get the result
    msd = []
    y_value = []
    y_err = []

    y_value_og = []
    y_err_og = []

    #To return to the template
    sumw = []
    sumw2 = []

    for i in range(1,h.GetNbinsX()+1):

        msd_bin_center = h.GetXaxis().GetBinCenter(i)
        msd.append(msd_bin_center)

        y_value_og.append(h.GetBinContent(i))
        y_err_og.append(h.GetBinError(i))

        fitted_qcd = fit_result(msd_bin_center)
        y_value.append(fitted_qcd)
        y_err.append(fit_error.GetBinError(i))

        sumw += [fitted_qcd]
        sumw2 += [fit_error.GetBinError(i)*fit_error.GetBinError(i)]


    return np.array(sumw)[1:]
    
def vh_rhalphabet(tmpdir,
                    throwPoisson = True,
                    fast=0):
    """ 
    Create the data cards!
    """

    # define bins    
    ptbins = {}
    ptbins['light'] = np.array([450,1200])

    npt = {}
    npt['light'] = len(ptbins['light']) - 1


    mjjbins = {}
    mjjbins['light'] = np.array([0,13000])

    nmjj = {}
    nmjj['light'] = len(mjjbins['light']) - 1

    msdbins = np.linspace(40, 201, 23)
    msd = rl.Observable('msd', msdbins)

    validbins = {}

    cats = ['light']
    ncat = len(cats)

    # Build qcd MC pass+fail model and fit to polynomial
    tf_params = {}
    for cat in cats:

        fitfailed_qcd = 0

        # here we derive these all at once with 2D array                            
        ptpts, msdpts = np.meshgrid(ptbins[cat][:-1] + 0.3 * np.diff(ptbins[cat]), msdbins[:-1] + 0.5 * np.diff(msdbins), indexing='ij')
        rhopts = 2*np.log(msdpts/ptpts)
        ptscaled = (ptpts - 450.) / (1200. - 450.)
        rhoscaled = (rhopts - (-6)) / ((-2.1) - (-6))
        validbins[cat] = (rhoscaled >= 0) & (rhoscaled <= 1)
        rhoscaled[~validbins[cat]] = 1  # we will mask these out later   

        while fitfailed_qcd < 5:
        
            qcdmodel = rl.Model('qcdmodel_'+cat)
            qcdpass, qcdfail = 0., 0.

            for ptbin in range(npt[cat]):
                for mjjbin in range(nmjj[cat]):

                    failCh = rl.Channel('ptbin%dmjjbin%d%s%s%s' % (ptbin, mjjbin, cat, 'fail',year))
                    passCh = rl.Channel('ptbin%dmjjbin%d%s%s%s' % (ptbin, mjjbin, cat, 'pass',year))
                    qcdmodel.addChannel(failCh)
                    qcdmodel.addChannel(passCh)

                    # QCD templates from file                           
                    failTempl = fit_fail_templ_QCD('QCD', 0, ptbin+1, cat, obs=msd, syst='nominal')
                    passTempl = get_template('QCD', 1, ptbin+1, cat, obs=msd, syst='nominal')

                    failCh.setObservation(failTempl, read_sumw2=True)
                    passCh.setObservation(passTempl, read_sumw2=True)

                    qcdfail += sum([val for val in failCh.getObservation()[0]])
                    qcdpass += sum([val for val in passCh.getObservation()[0]])

            qcdeff = qcdpass / qcdfail
            print('Inclusive P/F from Monte Carlo = ' + str(qcdeff))

            #Initial values                                                                 
            print('Initial fit values read from file initial_vals*')
            with open('initial_vals_'+cat+'.json') as f:
                initial_vals = np.array(json.load(f)['initial_vals'])

            print("Initial values: {}".format(initial_vals))

            tf_MCtempl = rl.BasisPoly("tf_MCtempl_"+cat+year,
                                      (initial_vals.shape[0]-1,initial_vals.shape[1]-1),
                                      ['pt', 'rho'],
                                      basis='Bernstein',
                                      init_params=initial_vals,
                                      limits=(-10, 10), coefficient_transform=None)
            tf_MCtempl_params = qcdeff * tf_MCtempl(ptscaled, rhoscaled)

            for ptbin in range(npt[cat]):
                for mjjbin in range(nmjj[cat]):

                    failCh = qcdmodel['ptbin%dmjjbin%d%sfail%s' % (ptbin, mjjbin, cat, year)]
                    passCh = qcdmodel['ptbin%dmjjbin%d%spass%s' % (ptbin, mjjbin, cat, year)]
                    failObs = failCh.getObservation()
                    passObs = passCh.getObservation()
                
                    qcdparams = np.array([rl.IndependentParameter('qcdparam_ptbin%dmjjbin%d%s%s_%d' % (ptbin, mjjbin, cat, year, i), 0) for i in range(msd.nbins)])
                    sigmascale = 10.
                    scaledparams = failObs * (1 + sigmascale/np.maximum(1., np.sqrt(failObs)))**qcdparams
                
                    fail_qcd = rl.ParametericSample('ptbin%dmjjbin%d%sfail%s_qcd' % (ptbin, mjjbin, cat, year), rl.Sample.BACKGROUND, msd, scaledparams[0])
                    failCh.addSample(fail_qcd)
                    pass_qcd = rl.TransferFactorSample('ptbin%dmjjbin%d%spass%s_qcd' % (ptbin, mjjbin, cat, year), rl.Sample.BACKGROUND, tf_MCtempl_params[ptbin, :], fail_qcd)
                    passCh.addSample(pass_qcd)
                
                    failCh.mask = validbins[cat][ptbin]
                    passCh.mask = validbins[cat][ptbin]

            qcdfit_ws = ROOT.RooWorkspace('w')

            simpdf, obs = qcdmodel.renderRoofit(qcdfit_ws)
            
            #Set the observed data 
            qcdfit = simpdf.fitTo(obs, 
                                  ROOT.RooFit.Extended(True),
                                  ROOT.RooFit.SumW2Error(True),
                                  ROOT.RooFit.Strategy(2),
                                  ROOT.RooFit.Save(),
                                  ROOT.RooFit.Minimizer('Minuit2', 'migrad'),
                                  ROOT.RooFit.PrintLevel(1),
                              )
            qcdfit_ws.add(qcdfit)
            qcdfit_ws.writeToFile(os.path.join(str(tmpdir), 'testModel_qcdfit_'+cat+year+'.root'))

            # Set parameters to fitted values  
            allparams = dict(zip(qcdfit.nameArray(), qcdfit.valueArray()))
            pvalues = []
            for i, p in enumerate(tf_MCtempl.parameters.reshape(-1)):
                p.value = allparams[p.name]
                pvalues += [p.value]
            
            if qcdfit.status() != 0:
                print('Could not fit qcd')
                fitfailed_qcd += 1

                new_values = np.array(pvalues).reshape(tf_MCtempl.parameters.shape)
                with open("initial_vals_"+cat+".json", "w") as outfile:
                    json.dump({"initial_vals":new_values.tolist()},outfile)

            else:
                break

        if fitfailed_qcd >=5:
            raise RuntimeError('Could not fit qcd after 5 tries')

        print("Fitted qcd for category " + cat)

        # Plot the MC P/F transfer factor                                                   
#        plot_mctf(tf_MCtempl,msdbins, cat)                           

        param_names = [p.name for p in tf_MCtempl.parameters.reshape(-1)]
        decoVector = rl.DecorrelatedNuisanceVector.fromRooFitResult(tf_MCtempl.name + '_deco', qcdfit, param_names)
        tf_MCtempl.parameters = decoVector.correlated_params.reshape(tf_MCtempl.parameters.shape)
        tf_MCtempl_params_final = tf_MCtempl(ptscaled, rhoscaled)

        tf_dataResidual = rl.BasisPoly("tf_dataResidual_"+year+cat,
                                       (0,0),
                                       ['pt', 'rho'],
                                       basis='Bernstein',
                                       init_params=np.array([[1]]),
                                       limits=(-20,20),
                                       coefficient_transform=None)
        tf_dataResidual_params = tf_dataResidual(ptscaled, rhoscaled)
        tf_params[cat] = qcdeff * tf_MCtempl_params_final * tf_dataResidual_params

    # build actual fit model now
    model = rl.Model('testModel_'+year)

    # exclude QCD from MC samps
    samps = ['ggF']
    sigs = ['ggF']

    for cat in cats:
        for ptbin in range(npt[cat]):
            for mjjbin in range(nmjj[cat]):
                for region in ['pass', 'fail']:

                    binindex = ptbin
                    if cat == 'vbf':
                        binindex = mjjbin

                    # drop bins outside rho validity                                                
                    mask = validbins[cat][ptbin]

                    ch = rl.Channel('ptbin%dmjjbin%d%s%s%s' % (ptbin, mjjbin, cat, region, year))
                    model.addChannel(ch)

                    isPass = region == 'pass'
                    templates = {}
            
                    for sName in samps:

                        templates[sName] = get_template(sName, isPass, binindex+1, cat, obs=msd, syst='nominal')
                        nominal = templates[sName][0]

                        # expectations
                        templ = templates[sName]
                        
                        if sName in sigs:
                            stype = rl.Sample.SIGNAL
                        else:
                            stype = rl.Sample.BACKGROUND
                    
                        sample = rl.TemplateSample(ch.name + '_' + sName, stype, templ)
                
                        ch.addSample(sample)

                    # Observed data = QCD MC
                    data_obs = get_template('QCD', isPass, binindex+1, cat, obs=msd, syst='nominal')

                    ch.setObservation(data_obs, read_sumw2=True)

                    # drop bins outside rho validity
                    mask = validbins[cat][ptbin]

    for cat in cats:
        for ptbin in range(npt[cat]):
            for mjjbin in range(nmjj[cat]):

                failCh = model['ptbin%dmjjbin%d%sfail%s' % (ptbin, mjjbin, cat, year)]
                passCh = model['ptbin%dmjjbin%d%spass%s' % (ptbin, mjjbin, cat, year)]

                qcdparams = np.array([rl.IndependentParameter('qcdparam_ptbin%dmjjbin%d%s%s_%d' % (ptbin, mjjbin, cat, year, i), 0) for i in range(msd.nbins)])
                initial_qcd = get_initial_QCD('QCD', 0, 1, cat, obs=msd, syst='nominal')  # was integer, and numpy complained about subtracting float from it   
                                             
                if np.any(initial_qcd < 0.):
                    raise ValueError('initial_qcd negative for some bins..', initial_qcd)

                sigmascale = 10  # to scale the deviation from initial                                                                                                     
                scaledparams = initial_qcd * (1 + sigmascale/np.maximum(1., np.sqrt(initial_qcd)))**qcdparams
                fail_qcd = rl.ParametericSample('ptbin%dmjjbin%d%sfail%s_qcd' % (ptbin, mjjbin, cat, year), rl.Sample.BACKGROUND, msd, scaledparams)
                failCh.addSample(fail_qcd)
                pass_qcd = rl.TransferFactorSample('ptbin%dmjjbin%d%spass%s_qcd' % (ptbin, mjjbin, cat, year), rl.Sample.BACKGROUND, tf_params[cat][ptbin, :], fail_qcd)
                passCh.addSample(pass_qcd)

    with open(os.path.join(str(tmpdir), 'testModel_'+year+'.pkl'), 'wb') as fout:
        pickle.dump(model, fout)

    model.renderCombine(os.path.join(str(tmpdir), 'testModel_'+year))

if __name__ == '__main__':

    year = "2016"
    thisdir = os.getcwd()
    if "2016APV" in thisdir:
        year = "2016APV"
    elif "2017" in thisdir: 
        year = "2017"
    elif "2018" in thisdir:
        year = "2018"

    print("Running for "+year)

    if not os.path.exists('output'):
        os.mkdir('output')

    vh_rhalphabet('output',year)

