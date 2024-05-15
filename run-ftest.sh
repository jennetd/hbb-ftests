#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node

mkdir -p combine
tar -xzf combine.tar.gz -C combine

export PATH=$PWD/combine/bin:$PATH
source combine/bin/activate

combine -h

# My job
echo "Arguments passed to the job: "
echo $1
echo $2
echo $3
echo $4

eosout=$3
index=$4

python compare.py --pt=$1 --rho=$2 --ntoys=50 --index=$4

dirs=`ls | grep pt$1rho$2_vs_`
for d in $dirs;
do
    #move output to eos
    xrdfs root://cmseos.fnal.gov/ mkdir $eosout/${d}_$index
    xrdcp -rf $d root://cmseos.fnal.gov/$eosout/${d}_$index
done
