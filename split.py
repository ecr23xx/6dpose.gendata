import os
import sys
import argparse
import numpy as np
from tqdm import tqdm
from collections import defaultdict


def parse_arg():
    parser = argparse.ArgumentParser(description='Synthetic data spliter')
    parser.add_argument('--root', default='/home/penggao/data/synthetic/hinterstoisser',
                        type=str, help="Root to synthetic datasets")
    parser.add_argument('--kpnum', type=int, help="Number of keypoints")
    parser.add_argument('--kptype', choices=['sift', 'corner', 'random', 'cluster'],
                        type=str, help="Type of keypoints")
    return parser.parse_args()


def split(root):
    """Split the datasets for different sequences"""
    train_lists = defaultdict(list)
    tbar = tqdm(sorted(os.listdir(os.path.join(root, 'annots'))))
    for name in tbar:
        annot = np.load(os.path.join(root, 'annots', name)).item()
        flag = defaultdict(bool)
        for obj_id in annot['obj_ids']:
            if flag['%02d' % obj_id] == True:
                continue
            train_lists['%02d' % obj_id].append(name.split('.')[0])
            flag['%02d' % obj_id] = True

    if os.path.exists(os.path.join(root, 'lists')):
        print("[WARNING] Overwriting existing spliting file, proceed (y/[n])?", end=' ')
        choice = input()
        if choice != 'y':
            print("[LOG] Interuppted by user, exit")
            sys.exit()
        else:
            os.system('rm %s/*' % os.path.join(root, 'lists'))
    else:
        os.makedirs(os.path.join(root, 'lists'))

    for key, lines in train_lists.items():
        with open(os.path.join(root, 'lists', '%s.txt' % key), 'w') as f:
            f.writelines("%s\n" % l for l in lines)
        with open(os.path.join(root, 'lists', 'split.txt'), 'a') as f:
            f.write('%s: %d\n' % (key, len(lines)))


if __name__ == '__main__':
    args = parse_arg()
    print("[LOG] Number of keypoints: %d" % args.kpnum)
    print("[LOG] Type of keypoints: %s" % args.kptype)
    print("[LOG] Spliting datasets")
    split(os.path.join(args.root, str(args.kpnum), args.kptype))
    print("[LOG] Done!")
