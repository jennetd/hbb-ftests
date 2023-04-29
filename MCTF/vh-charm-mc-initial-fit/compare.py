import os
import numpy as np
import ROOT
import argparse

def gen_toys(infile, ntoys, seed=123456):
    combine_cmd = "combineTool.py -M GenerateOnly -m 125 -d " + infile + "\
    --snapshotName MultiDimFit --bypassFrequentistFit \
    -n \"Toys\" -t "+str(ntoys)+" --saveToys \
    --seed "+str(seed)
    os.system(combine_cmd)

def GoF(infile, ntoys, seed=123456):

    combine_cmd = "combineTool.py -M GoodnessOfFit -m 125 -d " + infile + "\
    --snapshotName MultiDimFit --bypassFrequentistFit \
    -n \"Toys\" -t " + str(ntoys) + " --algo \"saturated\" --toysFile higgsCombineToys.GenerateOnly.mH125."+str(seed)+".root \
    --seed "+str(seed)
    os.system(combine_cmd)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='F-test')
    parser.add_argument('-p','--poly',nargs='+',help='polynomial order')
    parser.add_argument('-n','--ntoys',nargs='+',help='number of toys')
    parser.add_argument('-i','--index',nargs='+',help='index for random seed')
    args = parser.parse_args()

    poly = int(args.poly[0])
    ntoys = int(args.ntoys[0])
    seed = 123456+int(args.index[0])*100+31
    
    baseline = "poly{}".format(poly)
    alternatives = []
    pvalues = []
    
    alternatives += ["poly{}".format(poly+1)]
    
    alternatives = list(set(alternatives))

    for i,alt in enumerate(alternatives):

        poly_alt = int(alt.split("poly")[1])
        print(poly)
        
        print(alt)
        thedir = baseline+"_vs_"+alt

        os.mkdir(thedir)
        os.chdir(thedir)

        # Copy what we need
        os.system("cp ../"+baseline+"/higgsCombineSnapshot.MultiDimFit.mH125.root baseline.root")
        os.system("cp ../"+alt+"/higgsCombineSnapshot.MultiDimFit.mH125.root alternative.root")

        gen_toys("baseline.root",ntoys,seed=seed)

        # run baseline gof                                                                                                                              
        GoF("baseline.root",ntoys,seed=seed)
        os.system('mv higgsCombineToys.GoodnessOfFit.mH125.'+str(seed)+'.root higgsCombineToys.baseline.GoodnessOfFit.mH125.'+str(seed)+'.root')

        # run alternative gof                                                                                                                           
        GoF("alternative.root",ntoys,seed=seed)
        os.system('mv higgsCombineToys.GoodnessOfFit.mH125.'+str(seed)+'.root higgsCombineToys.alternative.GoodnessOfFit.mH125.'+str(seed)+'.root')

        os.chdir('../')

