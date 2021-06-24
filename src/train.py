# common
import os, sys
import copy
import random

# torch
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn


# import time
from time import time, strftime
from sklearn.metrics import confusion_matrix, accuracy_score

# model
from predicts import singlemodel_class
from nets import MyResNet

# local
import utils
import config as cf
from dataloader import build_dataloaders

# utils_v3
import utils_v3
logger = utils_v3.getLogger(__name__)


import argparse
parser = argparse.ArgumentParser(description='PyTorch Digital Mammography Training')
parser.add_argument('--lr', default=1e-3, type=float, help='learning rate')
parser.add_argument('--net_type', default='resnet', type=str, help='model')
parser.add_argument('--depth', default=50, choices = [11, 16, 19, 18, 34, 50, 152, 161, 169, 121, 201], type=int, help='depth of model')
parser.add_argument('--weight_decay', default=5e-4, type=float, help='weight decay')
parser.add_argument('--finetune', '-f', action='store_true', help='Fine tune pretrained model')
parser.add_argument('--trainer', default='adam', type = str, help = 'optimizer')
parser.add_argument('--duration', default= 1.5, type = float, help='time duration for each file in second')
parser.add_argument('--n_tests', default=3, type = int, help='number of tests in valid set')
parser.add_argument('--random_state', default=42)
parser.add_argument('--model_path', type=str, default = ' ')
parser.add_argument('--gamma', default = 0.5, type = float)
parser.add_argument('--batch_size', default=64, type=int)
parser.add_argument('--num_epochs', default=10, type=int,
                    help='Number of epochs in training')
parser.add_argument('--dropout_keep_prob', default=0.5, type=float)
parser.add_argument('--check_after', default=1,
                    type=int, help='check the network after check_after epoch')
parser.add_argument('--train_from', default=0,
                    choices=[0, 1],  # 0: from scratch, 1: from pretrained 1 (need model_path)
                    type=int,
                    help="training from beginning (1) or from the most recent ckpt (0)")
parser.add_argument('--frozen_until', '-fu', type=int, default = -1,
                    help="freeze until --frozen_util block")
parser.add_argument('--val_ratio', default=0.1, type=float,
        help = "number of training samples per class")

if __name__ == '__main__':
    args = parser.parse_args()

    logger.green('======================================================')
    logger.green('Data preparation')
    dset_loaders, (val_lbs, N_train, N_val) = build_dataloaders(args)
    num_classes = cf.NUM_CLASS

    def exp_lr_scheduler(args, optimizer, epoch):
        init_lr = args.lr
        lr_decay_epoch = 4
        weight_decay = args.weight_decay
        lr = init_lr * (0.6 ** (min(epoch, 200) // lr_decay_epoch))

        for param_group in optimizer.param_groups:
            param_group['lr'] = lr
            param_group['weight_decay'] = weight_decay

        return optimizer, lr

    saved_models = './saved_model/'
    if not os.path.isdir(saved_models): os.mkdir(saved_models)
    saved_model_fn = saved_models + args.net_type + '_' + str(args.depth) + '_' +\
        str(args.duration) + '_' +  strftime('%m%d_%H%M') + '_r' + str(args.random_state)

    logger.green('model will be saved to {}'.format(saved_model_fn))
    logger.green('********************************************************')
    old_model = './checkpoint/' + args.net_type + '_' + str(args.depth) + '.pth'

    if args.train_from == 1 and os.path.isfile(old_model):
        logger.green("| Load pretrained at: {}.".format(old_model))
        checkpoint = torch.load(old_model, map_location=lambda storage, loc: storage)
        tmp = checkpoint['model']
        model = utils.unparallelize_model(tmp)
        try:
            top1acc = checkpoint['acc']
            logger.green('previous acc\t%.4f'% top1acc)
        except KeyError:
            pass
        logger.green('=============================================')
    else:
        model = MyResNet(args.depth, num_classes)

    model, optimizer = utils.net_frozen(args, model)
    model = utils.parallelize_model(model)
    criterion = nn.CrossEntropyLoss()
    ################################
    best_acc = 0

    logger.green('Start training ... ')
    t0 = time()
    for epoch in range(args.num_epochs):
        optimizer, lr = exp_lr_scheduler(args, optimizer, epoch)
        logger.green('#################################################################')
        logger.green('=> Training Epoch #%d, LR=%.10f' % (epoch + 1, lr))
        running_loss, running_corrects, tot = 0.0, 0.0, 0.0
        running_loss_src, running_corrects_src, tot_src = 0.0, 0.0, 0.0
        ########################
        model.train()
        torch.set_grad_enabled(True)
        ## Training
        for batch_idx, (inputs, labels, fns) in enumerate(dset_loaders['train']):
            optimizer.zero_grad()
            inputs = utils.cvt_to_gpu(inputs)
            labels = utils.cvt_to_gpu(labels)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            ############################################
            _, preds = torch.max(outputs.data, 1)
            running_loss += loss.item()
            running_corrects += preds.eq(labels.data).cpu().sum()
            tot += labels.size(0)
            sys.stdout.write('\r')
            try:
                batch_loss = loss.item()
            except NameError:
                batch_loss = 0

            top1acc = float(running_corrects)/tot
            sys.stdout.write('Epoch [%2d/%2d] Iter [%3d/%3d]\tBatch loss %.4f\tTop1acc %.4f'
                             % (epoch + 1, args.num_epochs, batch_idx + 1,
                                (N_train // args.batch_size), batch_loss/args.batch_size,
                                top1acc))
            sys.stdout.flush()
            sys.stdout.write('\r')

        top1acc =  float(running_corrects)/N_train
        epoch_loss = running_loss/N_train
        logger.green('\n| Training loss %.8f\tTop1error %.4f'\
                % (epoch_loss, top1acc))

        utils.print_eta(t0, epoch, args.num_epochs)

        ###################################
        ## Validation
        if (epoch + 1) % args.check_after == 0:
            logger.green('On validation')
            pred_output, pred_prob, _ = singlemodel_class(model, dset_loaders['val'], num_tests =args.n_tests)
            logger.green(confusion_matrix(val_lbs, pred_output))
            acc1 = accuracy_score(val_lbs, pred_output)
            acc2 = accuracy_score(val_lbs, pred_prob)
            logger.green('acc_output: {}, acc_prob: {}'.format(acc1, acc2))
            ########### end test on multiple windows ##############
            running_loss, running_corrects, tot = 0.0, 0.0, 0.0
            torch.set_grad_enabled(False)
            model.eval()
            for batch_idx, (inputs, labels, _) in enumerate(dset_loaders['val']):
                inputs = utils.cvt_to_gpu(inputs)
                labels = utils.cvt_to_gpu(labels)
                outputs = model(inputs)
                _, preds  = torch.max(outputs.data, 1)
                running_loss += loss.item()
                running_corrects += preds.eq(labels.data).cpu().sum()
                tot += labels.size(0)

            epoch_loss = running_loss / N_val
            top1acc= float(running_corrects)/N_val
            logger.green('| Validation loss %.8f\tTop1acc %.4f'\
                    % (epoch_loss, top1acc))

            ################### save model based on best acc
            if acc1 > best_acc:
                best_acc = acc1
                logger.green('Saving model')
                best_model = copy.deepcopy(model)
                state = {
                    'model': best_model,
                    'acc' : acc1,
                    'clipped': args.duration,
                    'args': args
                }

                torch.save(state, saved_model_fn + '.t7')
                logger.green('=======================================================================')
                logger.green('model saved to:', (saved_model_fn + '.t7'))

