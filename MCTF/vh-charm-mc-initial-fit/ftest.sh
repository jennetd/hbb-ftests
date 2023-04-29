poly=$1

mkdir poly${poly}_vs_poly$((${poly}+1))
cd poly${poly}_vs_poly$((${poly}+1))

ln -s ../copy.sh .
./copy.sh

ln -s ../../../../plot-ftest_InitialFit.py .
python plot-ftest_InitialFit.py

cd ..
