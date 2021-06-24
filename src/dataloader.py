# common
import os
from time import time

# technical
from collections import Counter
import numpy as np

# sklearn
from sklearn.model_selection import train_test_split

# torch
from torch.utils.data import Subset
from torch.utils.data import Dataset, DataLoader

# local
import config as cf
from extract_feats import gen_spec

class MyDatasetSTFT(Dataset):
    def __init__(self, filenames, labels, duration=2):
        assert len(filenames) == len(labels), "Number of files != number of labels"
        self.fns = filenames
        self.lbs = labels
        self.duration = duration
    def __len__(self):
        return len(self.fns)

    def __getitem__(self, idx):
        fname = self.fns[idx]
        feat = gen_spec(fname.strip(), self.duration)
        return feat, self.lbs[idx], self.fns[idx]


def build_dataloaders(args):
    fb = open(os.path.join(cf.DATA_DIR, "metadata.csv"), "r")
    metadatas = fb.readlines()
    fb.close()

    fns, lbs = [], []
    for metadata in metadatas:
        if metadata.strip() == "uuid,subject_gender,subject_age,assessment_result,file_path":
            continue
        elements = metadata.strip().split(",")
        fname = os.path.join(cf.DATA_DIR, "wav", elements[-1])
        fns.append(fname)
        lbs.append(int(elements[-2]))
    train_fns, val_fns, train_lbs, val_lbs = train_test_split(fns, lbs, test_size = args.val_ratio, random_state = 42)
    dsets = {}
    dsets["train"] = MyDatasetSTFT(train_fns, train_lbs, duration = args.duration)
    dsets["val"] = MyDatasetSTFT(val_fns, val_lbs, duration = args.duration)

    N_train = len(train_fns)
    N_val = len(val_fns)

    dset_loaders = dict()
    dset_loaders['train'] = DataLoader(dsets['train'],
            batch_size = args.batch_size,
            shuffle = True,
            num_workers = cf.NUM_WORKERS)

    dset_loaders['val'] = DataLoader(dsets['val'],
            batch_size = args.batch_size,
            shuffle = False,
            num_workers = cf.NUM_WORKERS)

    return dset_loaders, (val_lbs, N_train, N_val)
