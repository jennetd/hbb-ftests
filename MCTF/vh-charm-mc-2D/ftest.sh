#Define the base poly and rho
poly=$1
rho=$2

rho_comparison=poly${poly}rho${rho}_vs_poly${poly}rho$((${rho}+1))
poly_comparison=poly${poly}rho${rho}_vs_poly$((${poly}+1))rho${rho}

echo $rho_comparison

#Comparison with higher order of rho
rm $rho_comparison
mkdir $rho_comparison
cd $rho_comparison

ln -s ../copy.sh .
./copy.sh

ln -s ../../../../plot-ftest.py .
python plot-ftest.py

cd ..

#Comparison with higher order of polynomial
rm $poly_comparison
mkdir $poly_comparison
cd $poly_comparison

ln -s ../copy.sh .
./copy.sh

ln -s ../../../../plot-ftest.py .
python plot-ftest.py
