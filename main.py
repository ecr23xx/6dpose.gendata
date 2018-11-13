import os
import argparse
import numpy as np
from tqdm import tqdm
from PIL import Image
opj = os.path.join

from sixd import SixdBenchmark
from transform import *


def parse_arg():
    parser = argparse.ArgumentParser(description='SIXD synthetic data generator')
    parser.add_argument('--dataset', default='hinterstoisser', type=str, help="dataset name")
    parser.add_argument('--bgroot', default='/home/penggao/data/coco/2017/train2017',
                        type=str, help="Path to background images")
    parser.add_argument('--saveroot', default='/home/penggao/data/synthetic/sixd',
                        type=str, help="Path to save images and annotation")
    parser.add_argument('--num', default=10000, type=int, help="Number of synthetic images")
    parser.add_argument('--size', default=(640, 480), type=tuple,
                        help="Width and height of synthetic images")
    return parser.parse_args()


def get_frames(bench, num=(10, 15), hards=[3, 7]):
    """
    Randomly choose frames to render.

    Args
    - bench: (SixdBenchmark)
    - num: (tuple) Number range of selected frames
    - hards: (list) Hard objects to skip

    Returns
    - frames: (list) selected frames
        Each item contains path to images and annotation
    """
    frames = list()
    selected_num = np.random.randint(num[0], num[1])
    selected_seqs = list(np.random.randint(1, len(bench.frames)+1, selected_num))
    for seq in selected_seqs:
        if seq in hards:  # skip hard objects
            continue
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

    Returns
    - syn: (np.array) [H x W x C] image array
    - annot: (dict) Keys and values are
        - bboxes: (np.array) [N x 4] bbox annotation 
        - poses: (np.array) [N x 3 x 4] pose annotation
        - obj_ids: (np.array) [N] object ids, range from [1,15]
    """
    bg = Image.open(bgpath).resize(size)
    syn = np.array(bg)
    assert len(syn.shape) == 3, "Gray scale images are not supported!"

    x1s = np.random.randint(0, size[0], len(frames))
    y1s = np.random.randint(0, size[1], len(frames))

    bboxes = []
    poses = []
    obj_ids = []
    for idx, f in enumerate(frames):
        x1, y1 = x1s[idx], y1s[idx]
        frame, bbox = random_scale(Image.open(f['path']), f['annots'][0]['bbox'], 0.6, 0.8)
        frame = frame.filter(ImageFilter.EDGE_ENHANCE)
        frame = np.array(frame)

        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x2, y2 = x1 + w, y1 + h
        if x2 > size[0] or y2 > size[1]:
            continue

        foreground = frame[bbox[1]:bbox[3], bbox[0]:bbox[2], :]
        zero_mask = foreground == 0
        foreground[zero_mask] = syn[y1:y2, x1:x2, :][zero_mask]
        syn[y1:y2, x1:x2, :] = foreground

        bboxes.append([x1, y1, x2, y2])
        poses.append(f['annots'][0]['pose'])
        obj_ids.append(f['annots'][0]['obj_id'])

    bg.close()

    annot = {
        'bboxes': np.array(bboxes),
        'poses': np.array(poses),
        'obj_ids': np.array(obj_ids)
    }

    return syn, annot


def save(save_root, idx, img_array, annot):
    """
    Save images and annotation

    Args
    - save_root: (str) Root to save directory
    - idx: (int) Saving index
    - img_array: (np.array) Returned from `stick`
    - annot: (dict) Returned from `stick`
    """
    img = Image.fromarray(img_array)
    img = random_blur(img, 0.4)
    img.save(opj(save_root, 'images', '%05d.png' % idx))
    np.save(opj(save_root, 'annot', '%05d.npy' % idx), annot)
    img.close()


if __name__ == '__main__':
    args = parse_arg()
    bench = SixdBenchmark(dataset=args.dataset, unit=1e-3, is_train=True)
    bgpaths = [opj(args.bgroot, bgname) for bgname in os.listdir(args.bgroot)[:args.num]]
    np.random.shuffle(bgpaths)  # shuffle background images

    print("[LOG] Sticking images")
    tbar = tqdm(bgpaths, ascii=True)
    for idx, bg in enumerate(tbar):
        frames = get_frames(bench)
        try:
            syn, annot = stick(frames, bg, args.size)
        except Exception as e:
            print("\n[ERROR]", str(e))
        save(args.saveroot, idx, syn, annot)
