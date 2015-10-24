#!/bin/bash
#PBS -l walltime=00:30:00,nodes=10:ppn=4
#PBS -N nile-train

# cd $PBS_O_WORKDIR  # Connect to working directory
###################################################################
# Initialize MPI
###################################################################
export PATH=/home/chu/mpich-install/bin:$PATH
export PYTHONPATH=/home/chu/tools/boost_1_54_0/lib:$PYTHONPATH
export LD_LIBRARY_PATH=/home/chu/tools/boost_1_54_0/lib:$LD_LIBRARY_PATH
NUMCPUS=$CORES
# NUMCPUS=`wc -l $PBS_NODEFILE | awk '{print $1}'`
###################################################################

APP_DIR=$HOME/developer/forest_aligner
K=128
LINK=$1
MAXEPOCH=$2
PARTIAL=$3
DATA=./data
LANGPAIR=ja_en
NAME=k${K}.$LANGPAIR.$MAXEPOCH.$PARTIAL.$LINK

nice -15 mpiexec -n $NUMCPUS $PYTHON $APP_DIR/aligner.py \
  --f $DATA/train.f \
  --e $DATA/train.e \
  --gold $DATA/train.a.s \
  --ftrees $DATA/forest/train.f.forest \
  --etrees $DATA/forest/1best/train.e.forest \
  --fdev $DATA/dev.f \
  --edev $DATA/dev.e \
  --ftreesdev $DATA/forest/dev.f.forest \
  --etreesdev $DATA/forest/1best/dev.e.forest \
  --golddev $DATA/dev.a.s \
  --evcb $DATA/e.vcb \
  --fvcb $DATA/f.vcb \
  --pef $DATA/GIZA++.m4.pef \
  --pfe $DATA/GIZA++.m4.pfe \
  --a1 $DATA/train.m4gdfa.e-f \
  --a2 $DATA/train.nakazawa.e-f.s \
  --a1_dev $DATA/dev.m4gdfa.e-f \
  --a2_dev $DATA/dev.nakazawa.e-f.s \
  --langpair $LANGPAIR \
  --partial $PARTIAL \
  --maxepochs $MAXEPOCH \
  --nto1 $LINK \
  --train \
  --k $K 1> $NAME.out 2> $NAME.err

ITER=`grep F-score-dev $NAME.err | awk '{print $2}' | cat -n | sort -nr -k 2 | head -1 | cut -f 1`
WEIGHTS_FILE=weights.`head -1 $NAME.out`
./extract-weights.py $WEIGHTS_FILE $ITER $NAME
