#!/bin/zsh
#PBS -l walltime=00:30:00,nodes=10:ppn=4
#PBS -N nile-test

# cd $PBS_O_WORKDIR  # Connect to working directory
###################################################################
# Initialize MPI
###################################################################
export PATH=/home/chu/mpich-install/bin:$PATH
export PYTHONPATH=/home/chu/tools/boost_1_54_0/lib:$PYTHONPATH
export LD_LIBRARY_PATH=/home/chu/tools/boost_1_54_0/lib:$LD_LIBRARY_PATH
NUMCPUS=$CORE
###################################################################

NILE_DIR=/home/otsuki/developer/forest_aligner
K=128
LINK=$1
MAXEPOCH=$2
PARTIAL=$3
DATA=/home/otsuki/developer/forest_aligner/data
LANGPAIR=ja_en
H=`grep F-score-dev $NAME.err | awk '{print $2}' | cat -n | sort -nr -k 2 | head -1 | cut -f 1`
WEIGHTS=k${K}.$LANGPAIR.$MAXEPOCH.$PARTIAL.$LINK.weights-$H
NAME=$WEIGHTS.test-output.a

nice -19 mpiexec -n $NUMCPUS $PYTHON $NILE_DIR/aligner.py \
  --f $DATA/test.f \
  --e $DATA/test.e \
  --ftrees $DATA/forest/1best/test.f.forest \
  --etrees $DATA/forest/1best/test.e.forest \
  --evcb $DATA/test.e.vcb \
  --fvcb $DATA/test.f.vcb \
  --pef $DATA/GIZA++.m4.pef  \
  --pfe $DATA/GIZA++.m4.pfe \
  --a1 $DATA/test.m4gdfa.e-f \
  --a2 $DATA/test.nakazawa.e-f.s \
  --align \
  --langpair $LANGPAIR \
  --weights $WEIGHTS \
  --partial $PARTIAL \
  --nto1 $LINK \
  --out $NAME \
  --k $K

$NILE_DIR/Fmeasure.py $NAME $DATA/test.a.s
