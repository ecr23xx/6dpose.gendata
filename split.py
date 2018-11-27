import os
import argparse
import numpy as np
from tqdm import tqdm
from collections import defaultdict


def parse_arg():
    parser = argparse.ArgumentParser(description='Synthetic data spliter')
    parser.add_argument('--kp', default=17, type=int,
                        help="Number of keypoints")
    return parser.parse_args()


def split(root):
    """Split the datasets for different sequences"""
    train_lists = defaultdict(list)
    tbar = tqdm(sorted(os.listdir(os.path.join(root, 'annots'))), ascii=True)
    for name in tbar:
        annot = np.load(os.path.join(root, 'annots', name)).item()
        flag = defaultdict(bool)
        for obj_id in annot['obj_ids']:
            if flag['%02d' % obj_id] == True:
                continue
            train_lists['%02d' % obj_id].append(name.split('.')[0])
            flag['%02d' % obj_id] = True

    if os.path.exists(os.path.join(root, 'lists')):
        print("[WARNING] Overwriting existing spliting file")
    else:
        os.makedirs(os.path.join(root, 'lists'))

    for key, lines in train_lists.items():
        with open(os.path.join(root, 'lists', '%s.txt' % key), 'w') as f:
            f.writelines("%s\n" % l for l in lines)


if __name__ == '__main__':
    args = parse_arg()
    print("[LOG] Spliting datasets of %d keypoints" % args.kp)
    split(os.path.join('/home/penggao/data/synthetic/hinterstoisser', str(args.kp)))
