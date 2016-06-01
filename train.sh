#!/bin/bash

export PATH=/home/chu/mpich-install/bin:$PATH
export PYTHONPATH=/home/chu/tools/boost_1_54_0/lib:$PYTHONPATH
export LD_LIBRARY_PATH=/home/chu/tools/boost_1_54_0/lib:$LD_LIBRARY_PATH
NUMCPUS=$CORES

K=128
LINK=$1
MAXEPOCH=$2
PARTIAL=$3
LANGPAIR=$4
NAME=k${K}.$LANGPAIR.$MAXEPOCH.$PARTIAL.$LINK

nice -15 mpiexec -n $NUMCPUS $PYTHON ./aligner.py \
  --f $DATA/train.zh \
  --e $DATA/train.en \
  --gold $DATA/train.a.sp.tagged \
  --ftrees $SOURCE_FOREST_DATA/train.zh.forest \
  --etrees $TARGET_FOREST_DATA/train.en.forest \
  --fdev $DATA/dev.zh \
  --edev $DATA/dev.en \
  --ftreesdev $SOURCE_FOREST_DATA/dev.zh.forest \
  --etreesdev $TARGET_FOREST_DATA/dev.en.forest \
  --golddev $DATA/dev.a.sp.tagged \
  --evcb $DATA/en.vcb \
  --fvcb $DATA/zh.vcb \
  --pef $DATA/GIZA++.m4.pef \
  --pfe $DATA/GIZA++.m4.pfe \
  --a1 $DATA/train.m4gdfa.e-f \
  --a2 $DATA/train.nakazawa.e-f.sp.tagged \
  --a1_dev $DATA/dev.m4gdfa.e-f \
  --a2_dev $DATA/dev.nakazawa.e-f.sp.tagged \
  --langpair $LANGPAIR \
  --partial $PARTIAL \
  --maxepochs $MAXEPOCH \
  --binarize=False \
  --decoding_path_out path_out_train \
  --nto1 $LINK \
  --train \
  --joint=True \
  --k $K 3>&1 2>&3 >$NAME.out | tee $NAME.err

ITER=`grep F-score-dev $NAME.err | awk '{print $2}' | cat -n | sort -nr -k 2 | head -1 | cut -f 1 | tr -d '[[:space:]]'`
WEIGHTS_FILE=weights.`head -1 $NAME.out`
./weight_extract.py $WEIGHTS_FILE $ITER $NAME
