import os
import numpy as np
from tqdm import tqdm
from collections import defaultdict


def split(root='/home/penggao/data/synthetic/hinterstoisser'):
    """
    Split the datasets for different sequences
    """
    train_lists = defaultdict(list)
    tbar = tqdm(sorted(os.listdir(os.path.join(root, 'annot'))), ascii=True)
    for idx, name in enumerate(tbar):
        assert '%05d' % idx == name.split('.')[0]
        annot = np.load(os.path.join(root, 'annot', name)).item()
        flag = defaultdict(bool)
        for obj_id in annot['obj_ids']:
            if flag['%02d' % obj_id] == True:
                continue  # skip duplicate entry
            train_lists['%02d' % obj_id].append('%05d' % idx)
            flag['%02d' % obj_id] = True
    for key, lines in train_lists.items():
        with open(os.path.join(root, 'lists', '%s.txt' % key), 'w') as f:
            f.writelines("%s\n" % l for l in lines)


if __name__ == '__main__':
    split()
