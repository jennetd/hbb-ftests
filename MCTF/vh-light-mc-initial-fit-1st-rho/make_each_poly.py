import os
import numpy as np
import json

if __name__ == '__main__':

    year = "2016"
    thisdir = os.getcwd()
    if "2016APV" in thisdir:
        year = "2016APV"
    elif "2017" in thisdir:
        year = "2017"
    elif "2018" in thisdir:
        year = "2018"

    for poly in range(0,6):

            print("Polynomial order: {}".format(poly))

            # Make the directory and go there
            thedir = "poly{}".format(poly)
            if not os.path.isdir(thedir):
                os.mkdir(thedir)
            os.chdir(thedir)

            #Directory to read the root file from
            linkdir= "/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/hbb-coffea/vh_combine/allyears_Oct19_masscut_functional/"

            os.system("ln -s "+linkdir+year+"/signalregion.root .")
            os.system("ln -s ../../make_cards_qcd.py .")

            # Create your json files of initial values
            # for the polynomial fit
            poly_file = "initial_vals_poly_light.json"
            if not os.path.isfile(poly_file):
                initial_vals = (np.full(poly+1,1)).tolist()
                thedict = {}
                thedict["initial_vals"] = initial_vals
                with open(poly_file, "w") as outfile:
                    json.dump(thedict,outfile)
            
            # Create your json files of initial values
            # For the rho transfer factor fit, this has already been determined
            rho_file = "initial_vals_light.json"
            if not os.path.isfile(rho_file):
                
                #It's a constant for every charm category
                #First order for 2018 light category
                initial_vals = (np.full((1,2),1)).tolist() #is it correct here?
                thedict = {}
                thedict["initial_vals"] = initial_vals

                with open(rho_file, "w") as outfile:
                    json.dump(thedict,outfile)

            # Create the workspace
            os.system("python make_cards_qcd.py") 

            # Make the workspace
            os.chdir("output/testModel_"+year)
            os.system("chmod +rwx build.sh")
            os.system("./build.sh")
            os.chdir("../../")

            # Run the first fit
            combine_cmd = "combineTool.py -M MultiDimFit -m 125 -d output/testModel_"+year+"/model_combined.root --saveWorkspace \
            --setParameters r=0 --freezeParameters r -n \"Snapshot\" \
            --robustFit=1 --cminDefaultMinimizerStrategy 0"
            os.system(combine_cmd)

            # Run the goodness of fit
            combine_cmd = "combineTool.py -M GoodnessOfFit -m 125 -d higgsCombineSnapshot.MultiDimFit.mH125.root \
            --snapshotName MultiDimFit --bypassFrequentistFit \
            --setParameters r=0 --freezeParameters r \
            -n \"Observed\" --algo \"saturated\" --cminDefaultMinimizerStrategy 0"
            os.system(combine_cmd)

            os.chdir("../")
