import os
import argparse
import numpy as np
from PIL import Image
from tqdm import tqdm
opj = os.path.join

from sixd import SixdBenchmark
from utils import *


def parse_arg():
    parser = argparse.ArgumentParser(description='SIXD synthetic data generator')
    parser.add_argument('--dataset', default='hinterstoisser',
                        type=str, help="dataset name")
    parser.add_argument('--bgroot', default='/home/penggao/data/coco/2017/train2017',
                        type=str, help="Path to background images")
    parser.add_argument('--saveroot', default='/home/penggao/data/synthetic/sixd',
                        type=str, help="Path to save images and annotation")
    parser.add_argument('--num', default=10000,
                        type=int, help="Number of synthetic images")
    return parser.parse_args()


def get_frames(bench, num=(10, 15)):
    """
    Randomly choose frames to render.

    Args
    - bench: (SixdBenchmark)
    - num: (tuple) number range of selected frames

    Returns
    - frames: (list) selected frames
        Each item contains path to images and annotation
    """
    frames = list()
    selected_num = np.random.randint(num[0], num[1])
    selected_seqs = list(np.random.randint(1, len(bench.frames)+1, selected_num))
    for seq in selected_seqs:
        idx = np.random.randint(0, len(bench.frames['%02d' % seq]))
        frames.append(bench.frames['%02d' % seq][idx])
    return frames


def stick(frames, bgpath, savepath, size=(640, 480)):
    """
    Stick frames in a random location in background images

    Args
    - frames: (list) Returned by `get_frames`
    - bgpath: (str) Path to background image
    - savepath: (str) Image saving path
    - size: (tuple) Synthetic images' width and height
    """
    bg = Image.open(bgpath).resize(size)
    syn = np.array(bg)  # [H x W x C]

    x1s = np.random.randint(0, size[0], len(frames))
    y1s = np.random.randint(0, size[1], len(frames))

    bboxes = []
    poses = []
    obj_id = []
    for idx, f in enumerate(frames):
        x1, y1 = x1s[idx], y1s[idx]
        frame = np.array(Image.open(f['path']))

        bbox = f['annots'][0]['bbox']  # each image contains only one object
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x2, y2 = x1 + w, y1 + h
        if x2 > size[0] or y2 > size[1]:
            continue

        zero_mask = frame[bbox[1]:bbox[3], bbox[0]:bbox[2], :] == 0
        frame[bbox[1]:bbox[3], bbox[0]:bbox[2], :][zero_mask] = syn[y1:y2, x1:x2, :][zero_mask]
        syn[y1:y2, x1:x2, :] = frame[bbox[1]:bbox[3], bbox[0]:bbox[2], :]

        bboxes.append([x1, y1, x2, y2])
        poses.append(f['annots'][0]['pose'])
        obj_id.append(f['annots'][0]['obj_id'])

    syn_img = Image.fromarray(syn)
    syn_img.save(savepath)
    bg.close()
    syn_img.close()


if __name__ == '__main__':
    args = parse_arg()
    bench = SixdBenchmark(dataset=args.dataset, unit=1e-3, is_train=True)
    bgpaths = [opj(args.bgroot, bgname) for bgname in os.listdir(args.bgroot)[:args.num]]

    print("[LOG] Sticking images")
    tbar = tqdm(bgpaths, ascii=True)
    for idx, bg in enumerate(tbar):
        frames = get_frames(bench)
        stick(frames, bg, opj(args.saveroot, '%05d.png' % idx))
