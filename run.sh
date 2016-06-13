#!/bin/bash

export PATH=$HOME/.local/bin:/home/chu/mpich-install/bin:$PATH

CPU=`nproc`
_CORES=`echo "$CPU * 0.8" | bc`

################### CUSTOMIZABLE #####################
LINK=2
ITER=100
PARTIAL=-1
LANG="ja_en"
export DATA=/windroot/otsuki/data/LDC2012/LDC2012-SP # Absolute path to the base directory which has data
export TARGET_FOREST_DATA=$DATA/YaraParser/forest/1best
export SOURCE_FOREST_DATA=$DATA/SKP/forest/1best
######################################################

export CORES=${_CORES%.*}

rm -rf weights-*
rm -rf weights\.*
rm -rf k*
rm -rf *output*

set -e

./train.sh $LINK $ITER $PARTIAL $LANG
./test.sh $LINK $ITER $PARTIAL $LANG
