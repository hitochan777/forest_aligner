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
NUMCPUS=4
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
  --etrees $DATA/forest/1best/train.e.forest \
  --fdev $DATA/dev.f \
  --edev $DATA/dev.e \
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

# echo "nice -15 $NILE_DIR/weights.sh $NAME $H"
# nice -15 $NILE_DIR/weights.sh $NAME $H
