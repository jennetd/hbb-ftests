#The first argument is year for this script
echo "The current path of this script is: ${PWD}"

mkdir $1-mc
cd $1-mc

#Run the first script to set things up
ln -s ../make_each_ptrho.py .

cmsenv
python make_each_ptrho.py

#Then link other necessary files for toy job submission
ln -s ../submit.sh .
ln -s ../copy.sh .
ln -s ../compare.py .
ln -s ../ftest.sh .

ln -s ../../submit.py .

ln -s ../../../run-ftest.sh
ln -s ../../../submit.templ.condor

#Submit the jobs to generate toys samples
./submit.sh