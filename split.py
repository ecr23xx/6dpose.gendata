import os
import numpy as np
from tqdm import tqdm
from collections import defaultdict


def split(root='/home/penggao/data/synthetic/hinterstoisser'):
    """
    Split the datasets for different sequences
    """
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
    for key, lines in train_lists.items():
        with open(os.path.join(root, 'lists', '%s.txt' % key), 'w') as f:
            f.writelines("%s\n" % l for l in lines)


if __name__ == '__main__':
    split()
