#!/usr/bin/env zsh
set -e

CPU=`nproc`
_CORES=`echo "$CPU * 0.5" | bc`
LINK=2
ITER=10
PARTIAL=50

export CORES=${_CORES%.*}
export PYTHONPATH=/usr/local/lib:$HOME/developer/pyglog:$HOME/developer/forest_aligner/pyglog:PYTHONPATH
export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib:/usr/local/lib64:/usr/lib64:$LD_LIBRARY_PATH
export C_INCLUDE_PATH=/home/hitoshi/developer/boost_1_59_0:$C_INCLUDE_PATH
export CPLUS_INCLUDE_PATH=/home/hitoshi/developer/boost_1_59_0:$CPLUS_INCLUDE_PATH
export LD_LIBRARY_PATH=/home/hitoshi/developer/boost_1_59_0/stage/lib:$LD_LIBRARY_PATH

rm -rf weights-* weights.*
rm -rf k*
rm -rf *output*

[ ! -d data ] && ln -s $ASPEC_JE data
./train.sh $LINK $ITER $PARTIAL
./test.sh $LINK $ITER $PARTIAL
