from utils import *
from transform import *
from sixd import SixdBenchmark
import os
import argparse
import numpy as np
from tqdm import tqdm
from PIL import Image
opj = os.path.join


def parse_arg():
    parser = argparse.ArgumentParser(
        description='SIXD synthetic data generator')
    parser.add_argument('--dataset', default='hinterstoisser',
                        type=str, help="dataset name")
    parser.add_argument('--bgroot', default='/home/penggao/data/coco/2017/train2017',
                        type=str, help="Path to background images")
    parser.add_argument('--saveroot', default='/home/penggao/data/synthetic/hinterstoisser',
                        type=str, help="Path to save images and annotation")
    parser.add_argument('--num', default=10000, type=int,
                        help="Number of synthetic images")
    return parser.parse_args()


def get_frames(bench, num=(8, 15)):
    """
    Randomly choose frames to render.

    Args
    - bench: (SixdBenchmark)
    - num: (tuple) Number range of selected frames

    Returns
    - frames: (list) selected frames
        Each item contains path to images and annotation
    """
    frames = list()
    num_frames = np.random.randint(num[0], num[1])
    num_seqs = len(bench.frames)
    selected_seqs = np.random.choice(range(1, num_seqs+1), num_frames, False)
    for seq in selected_seqs:
        idx = np.random.randint(0, len(bench.frames['%02d' % seq]))
        frames.append(bench.frames['%02d' % seq][idx])
    return frames


def stick(frames, bgpath, cam, size=(640, 480)):
    """
    Stick frames in a random location in background images

    Args
    - frames: (list) Returned by `get_frames`
    - bgpath: (str) Path to background image
    - size: (tuple) Synthetic images' width and height
    - cam: (np.array) [3 x 3]

    Returns
    - syn: (np.array) [H x W x C] image array
    - annot: (dict) Keys and values are
        - bboxes: (np.array) [N x 4] bbox annotation
        - poses: (np.array) [N x 3 x 4] pose annotation
        - kps: (np.array) [N x K x 2] keypoints annotation,
                K for number of keypoints
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
    kps = []
    for idx, f in enumerate(frames):
        x1, y1 = x1s[idx], y1s[idx]
        assert len(f['annots']) == 1, "Annotations error!"
        frame, annot, sf = random_scale(Image.open(f['path']), f['annots'][0],
                                        min_sf=0.3, max_sf=0.7)
        frame = frame.filter(ImageFilter.EDGE_ENHANCE)
        frame = np.array(frame)
        bbox = annot['bbox']

        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x2, y2 = x1 + w, y1 + h
        if x2 > size[0] or y2 > size[1]:
            continue

        foreground = frame[bbox[1]:bbox[3], bbox[0]:bbox[2], :]
        zero_mask = foreground == 0
        foreground[zero_mask] = syn[y1:y2, x1:x2, :][zero_mask]
        syn[y1:y2, x1:x2, :] = foreground

        bboxes.append([x1, y1, x2, y2])
        kp = annot['kps']
        kp[:, 0] = kp[:, 0] - bbox[0] + x1
        kp[:, 1] = kp[:, 1] - bbox[1] + y1
        kps.append(kp)
        pose = annot['pose']
        trans = np.array([[sf, 0, x1 - bbox[0]],
                          [0, sf, y1 - bbox[1]],
                          [0, 0, 1]])
        pose = np.linalg.inv(cam).dot(trans).dot(cam).dot(pose)
        poses.append(pose)
        obj_ids.append(annot['obj_id'])

    bg.close()

    annot = {
        'bboxes': np.array(bboxes),
        'kps': np.array(kps),
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
    np.save(opj(save_root, 'annots', '%05d.npy' % idx), annot)
    img.close()


if __name__ == '__main__':
    args = parse_arg()
    bench = SixdBenchmark(dataset=args.dataset, unit=1e-3, is_train=True)
    bgpaths = [opj(args.bgroot, bgname)
               for bgname in os.listdir(args.bgroot)[:args.num]]
    np.random.shuffle(bgpaths)

    os.makedirs(opj(args.saveroot, 'images'), exist_ok=True)
    os.makedirs(opj(args.saveroot, 'annots'), exist_ok=True)
    if len(os.listdir(opj(args.saveroot, 'images'))) != 0:
        print("[WARNING] Clear exsiting images and annotations")
        os.system('rm %s/*' % opj(args.saveroot, 'images'))
        os.system('rm %s/*' % opj(args.saveroot, 'annots'))

    print("[LOG] Sticking images")
    tbar = tqdm(bgpaths, ascii=True)
    for idx, bg in enumerate(tbar):
        frames = get_frames(bench)
        try:
            syn, annot = stick(frames, bg, bench.cam)
            save(args.saveroot, idx, syn, annot)
        except Exception as e:
            print("\n[ERROR] %s in No.%d" % (str(e), idx))
