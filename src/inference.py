# common
import os

# torch
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from dataloader import MyDatasetSTFT

# local
import config as cf
import predicts
from utils import *

# utils_v3
import utils_v3
logger = utils_v3.getLogger(__name__)

import argparse
parser = argparse.ArgumentParser(description='Zalo Voice Gender')
parser.add_argument("--data_dir", default="", type=str, help='testset directory')
parser.add_argument("--output", default="", type=str, help='output directory')
parser.add_argument('--net_type', default='resnet', type=str, help='model')
parser.add_argument('--depth', default=18, choices = [18, 50, 152], type=int, help='depth of model')
parser.add_argument('--model_path', type=str, default = ' ')
parser.add_argument('--batch_size', type=int, default = 63)
parser.add_argument('--num_tests', type=int, default = 10, help = 'number of tested windows in each file')
args = parser.parse_args()

model_path_fns = ["/data/linhld6/covid_ai/saved_model/resnet_50_2.0_0624_0944_r42.t7"]

# Stage 1: Load model
models = []
clippeds = [] ## each model might received a different input lengh
for model_path_fn in model_path_fns:
    logger.green("| Load pretrained at  %s..." % model_path_fn)
    checkpoint = torch.load(model_path_fn, map_location=lambda storage, loc: storage)
    model = checkpoint['model']
    model = unparallelize_model(model)
    model = parallelize_model(model)
    best_acc = checkpoint['acc']
    clipped = checkpoint['args'].duration
    logger.green('model {}, acc on CV: {}'.format(model_path_fn, best_acc))
    models.append(model)
    clippeds.append(clipped)

# Stage 2: Load data
logger.green('Data preparation')
fns = [os.path.join(args.data_dir, "wav", fn)
        for fn in os.listdir(os.path.join(args.data_dir, "wav"))]
logger.green('Total provided files: {}'.format(len(fns)))
lbs = [-1]*len(fns) # random labels, we won't use this


dset_loaders = []
for clipped in clippeds:
    dset = MyDatasetSTFT(fns, lbs, duration = clipped)
    dset_loaders.append(torch.utils.data.DataLoader(dset,
                        batch_size=args.batch_size,
                        shuffle= False, num_workers=cf.NUM_WORKERS))


# Stage 3: prediction
pred_score, pred_probs, fns = \
        predicts.multimodels_multiloaders_class(models, dset_loaders, num_tests = args.num_tests)

def gen_outputline(fn, pred):
    s = fn.split('/')[-1][:-4] + ',' +  str(pred%2) + '\n'
    return s

submission_fn = os.path.join(args.output, 'submission.csv')
f = open(submission_fn, 'w')
header = 'uuid,assessment_result\n'
f.write(header)
for i, fn in enumerate(fns):
    f.write(gen_outputline(fn, pred_score[i]))
f.close()
logger.green('done')


