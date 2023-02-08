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

    for pt in range(0,3):
        for rho in range(0,3):

            print("pt = "+str(pt)+", rho = "+str(rho))

            # Make the directory and go there
            thedir = "pt"+str(pt)+"rho"+str(rho)
            if not os.path.isdir(thedir):
                os.mkdir(thedir)
            os.chdir(thedir)

            # Link what you need
            linkdir="/uscms/home/jennetd/nobackup/hbb-prod-modes/CMSSW_10_2_13/src/vbf-ul/main-vbf/unblinding/"

            os.system("ln -s "+linkdir+year+"/signalregion.root .")
            os.system("ln -s ../../make_cards_qcd.py .")

            # Create your json files of initial values
            if not os.path.isfile("initial_vals_ggf.json"):

                initial_vals = (np.full((pt+1,rho+1),1)).tolist()
                thedict = {}
                thedict["initial_vals"] = initial_vals

                with open("initial_vals_ggf.json", "w") as outfile:
                    json.dump(thedict,outfile)

            # Create the workspace
            os.system("python make_cards_qcd.py") 

            # Make the workspace
            os.chdir("output/testModel_"+year)
            os.system("chmod +rwx build.sh")
            os.system("./build.sh")
            os.chdir("../../")

            # Run the goodness of fit
            combine_cmd = "combine -M GoodnessOfFit -m 125 -d output/testModel_"+year+"/model_combined.root --setParameters r=0 -n Observed --algo saturated"
            os.system(combine_cmd)

            os.chdir("../")
