#!/bin/bash
# created: linhld6

source path.sh
conda deactivate
conda activate acc

export CUDA_VISIBLE_DEVICES="0"
if [ $# -ne 1 ];then
    echo "=========================="
    echo "$0 <testset>"
    echo "=========================="
    echo """
Input:
    testset:
            \- wav/*.wav
            \- ground_truth.csv
Output:
    testset:
        \- wav/*.wav
        \- ground_truth.csv
        \- submission.csv
        \- final.csv
        \- accuracy.txt
        """
    exit 1
fi

rm -rf $1/submission.csv $1/final.csv

# Stage 1: Predict output
python src/inference.py --data_dir $1 --output $1 --num_tests 10

# Stage 2: Compute acc
python src/process_result.py --gr $1/ground_truth.csv --hyp $1/submission.csv