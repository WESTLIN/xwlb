#!/usr/bin/env bash

SRCDIR=/home/yhyan/xwlb

python $SRCDIR/news_xwlb.py $1
python $SRCDIR/news_content.py $1
python $SRCDIR/news_keys.py $1

