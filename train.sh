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
NUMCPUS=15
# NUMCPUS=`wc -l $PBS_NODEFILE | awk '{print $1}'`
###################################################################

NILE_DIR=/home/otsuki/tools/nile
K=5
LINK=$1
MAXEPOCH=$2
PARTIAL=$3
DATA=./sample
LANGPAIR=ja_en
NAME=k${K}.$LANGPAIR.$MAXEPOCH.$PARTIAL.$LINK

nice -15 mpiexec -n $NUMCPUS $PYTHON /home/otsuki/developer/forest_aligner/aligner.py \
  --f $DATA/train.f \
  --e $DATA/train.e \
  --gold $DATA/train.a.s \
  --ftrees $DATA/train.f.forest \
  --etrees $DATA/train.e.forest \
  --fdev $DATA/dev.f \
  --edev $DATA/dev.e \
  --ftreesdev $DATA/dev.f.forest \
  --etreesdev $DATA/dev.e.forest \
  --golddev $DATA/dev.a.s \
  --evcb $DATA/e.vcb \
  --fvcb $DATA/f.vcb \
  --pef $DATA/pef \
  --pfe $DATA/pfe \
  --a1 $DATA/train.a.s \
  --a2 $DATA/train.a.s \
  --a1_dev $DATA/dev.a.s \
  --a2_dev $DATA/dev.a.s \
  --langpair $LANGPAIR \
  --partial $PARTIAL \
  --maxepochs $MAXEPOCH \
  --nto1 $LINK \
  --train \
  --k $K 1> $NAME.out 2> $NAME.err

# echo "nice -15 $NILE_DIR/weights.sh $NAME $H"
# nice -15 $NILE_DIR/weights.sh $NAME $H
