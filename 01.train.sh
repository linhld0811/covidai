#!/bin/bash
# created: linhld6

source path.sh
conda deactivate
conda activate acc

export CUDA_VISIBLE_DEVICES="0"
python src/train.py --lr 1e-3 --net_type resnet --depth 50 \
    --weight_decay 5e-4 \
    --dropout_keep_prob 0.5 \
    --duration 2.0 \
    --n_tests 3 \
    --random_state 42 \
    --model_path 0 \
    --batch_size 32 \
    --check_after 1 \
    --train_from 0 \
    --num_epochs 30 \
    --val_ratio 0.1


