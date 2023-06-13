#!/usr/bin/python
import os, sys
import subprocess
import argparse

# Main method                                                                          
def main():

    year = "2016"
    thisdir = os.getcwd()
    if "2016APV" in thisdir:
        year = "2016APV"
    elif "2017" in thisdir:
        year = "2017"
    elif "2018" in thisdir:
        year = "2018"

    cat = "charm-mc"
    if "vh-light-mc" in thisdir:
        cat = "light-mc"

    parser = argparse.ArgumentParser(description='F-test batch submit')
    parser.add_argument('-p','--poly', nargs='+',help='poly order of baseline')
    parser.add_argument('-r','--rho', nargs='+',help='rho order of baseline')
    parser.add_argument('-n','--njobs',nargs='+',help='number of 100 toy jobs to submit')
    args = parser.parse_args()

    poly = int(args.poly[0])
    rho = int(args.rho[0])
    njobs = int(args.njobs[0])

    print("Poly order: {}, Rho order: {} ".format(poly, rho))

    loc_base = os.environ['PWD']
    logdir = 'logs'

    tag = "poly{}rho{}".format(poly, rho)
    script = 'run-ftest.sh'

    homedir = '/store/user/dhoang/f-tests/hbb-f-tests-pf/initial-fit/'+cat+'/'+year+'/'
    outdir = homedir + tag 

    # make local directory
    locdir = logdir
    os.system('mkdir -p  %s' %locdir)

    print('CONDOR work dir: ' + homedir)
    os.system('mkdir -p /eos/uscms'+outdir)

    for i in range(0,njobs):
        prefix = tag+"_"+str(i)
        print('Submitting '+prefix)

        condor_templ_file = open("submit.templ.condor")
        transferfiles = "compare.py,poly{}rho{},poly{}rho{}".format(poly,rho,poly,rho+1) #is this correct?

        submitargs = str(poly) + " " + str(rho) + " " + outdir + " " + str(i)
    
        localcondor = locdir+'/'+prefix+".condor"
        condor_file = open(localcondor,"w")
        for line in condor_templ_file:
            line=line.replace('TRANSFERFILES',transferfiles)
            line=line.replace('PREFIX',prefix)
            line=line.replace('SUBMITARGS',submitargs)
            condor_file.write(line)
        condor_file.close()
    
        if (os.path.exists('%s.log'  % localcondor)):
            os.system('rm %s.log' % localcondor)
        os.system('condor_submit %s' % localcondor)

        condor_templ_file.close()
    
    return 

if __name__ == "__main__":
    main()
