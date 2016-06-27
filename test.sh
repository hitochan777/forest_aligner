#!/bin/bash

NUMCPUS=$CORES
LINK=$1
MAXEPOCH=$2
PARTIAL=$3
LANGPAIR=$4
K=$5
ERR_FILE_NAME=k${K}.$LANGPAIR.$MAXEPOCH.$PARTIAL.$LINK
H=`grep F-score-dev $ERR_FILE_NAME.err | awk '{print $2}' | cat -n | sort -nr -k 2 | head -1 | cut -f 1 | tr -d '[[:space:]]'`
WEIGHTS=k${K}.$LANGPAIR.$MAXEPOCH.$PARTIAL.$LINK.weights-$H
NAME=$WEIGHTS.test-output.a

nice -19 mpiexec -n $NUMCPUS -hostfile hosts nice -19 $PYTHON ./aligner.py \
  --f $DATA/test.zh \
  --e $DATA/test.en \
  --ftrees $SOURCE_FOREST_DATA/test.zh.forest \
  --etrees $TARGET_FOREST_DATA/test.en.forest \
  --evcb $DATA/test.en.vcb \
  --fvcb $DATA/test.zh.vcb \
  --pef $DATA/GIZA++.m4.pef  \
  --pfe $DATA/GIZA++.m4.pfe \
  --a1 $DATA/test.m4gdfa.e-f \
  --a2 $DATA/test.nakazawa.e-f.sp.tagged \
  --align \
  --langpair $LANGPAIR \
  --weights $WEIGHTS \
  --partial $PARTIAL \
  --nto1 $LINK \
  --binarize=False \
  --decoding_path_out path_out_test  \
  --out $NAME \
  --joint=True \
  --tempdir ./tmp \
  --k $K

./Fmeasure.py $NAME $DATA/test.a.sp.tagged
