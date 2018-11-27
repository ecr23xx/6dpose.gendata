#####################################
# Sixd benchmark loading utilities  #
# Author: Gao PENG                  #
# ################################# #

import os
import yaml
import pickle
import numpy as np
from tqdm import tqdm
from plyfile import PlyData

opj = os.path.join


class SixdBenchmark:
    """Sixd dataset

    Attrs
    - root: (str) Path to root. e.g. '/home/penggao/data/sixd/hinterstoisser'
    - unit: (float) Unit scale to meters. e.g. '1e-3' means unit is mm
    - pklpath: (str) Path to .pkl file
    - cam: (np.array) [3 x 3] camera matrix
    - models: (dict) Named with sequence number (e.g. '01').
          Each item is a [N x 3] np.array for corresponding model vertices
    - kps: (dict) Same format as 'models', represents corresponding keypoints
    - frames: (dict) Named with sequence number (e.g. '01')
          Each item is a list of image frames, with file paths and annotations
    """

    def __init__(self, dataset, num_kp, unit, is_train, resume=True):
        # Prepare
        self.root = opj('/home/penggao/data/sixd', dataset)
        self.num_kp = num_kp
        self.unit = unit
        self.is_train = is_train

        self.pklpath = opj(self.root, 'libs/benchmark.%s.pkl' %
                           ('train' if is_train else 'test'))
        self.seq_num = 15  # FIXME: constant

        self.cam = np.zeros((3, 3))
        self.models = dict()
        self.models_info = dict()
        self.kps = dict()
        self.frames = dict()

        # Try to load from disk
        if resume == True:
            try:
                self._load_from_disk()
                print("[LOG] Load SIXD from pkl file success")
                return
            except Exception as e:
                print("[ERROR]", str(e))
                print("[ERROR] Load from pkl file failed. Load all anew")
        else:
            print("[LOG] Load SXID all anew")

        # Load camera matrix
        print("[LOG] Load camera matrix")
        with open(os.path.join(self.root, 'camera.yml')) as f:
            content = yaml.load(f)
            self.cam = np.array([[content['fx'], 0, content['cx']],
                                 [0, content['fy'], content['cy']],
                                 [0, 0, 1]])

        # Load models and keypoints
        print("[LOG] Load models and keypoints")
        with open(os.path.join(self.root, 'models/models_info.yml')) as f:
            content = yaml.load(f)
            for key, val in tqdm(content.items(), ascii=True):
                name = '%02d' % int(key)  # e.g. '01'
                self.models_info[name] = val

                ply_path = os.path.join(self.root, 'models/obj_%s.ply' % name)
                data = PlyData.read(ply_path)
                self.models[name] = np.stack((np.array(data['vertex']['x']),
                                              np.array(data['vertex']['y']),
                                              np.array(data['vertex']['z'])), axis=1)

                kp_path = os.path.join(
                    self.root, 'kps/%d/obj_%s.ply' % (self.num_kp, name))
                data = PlyData.read(kp_path)
                self.kps[name] = np.stack((np.array(data['vertex']['x']),
                                           np.array(data['vertex']['y']),
                                           np.array(data['vertex']['z'])), axis=1)

        # Load annotations
        print("[LOG] Load annotations")
        for seq in tqdm(['%02d' % i for i in range(1, self.seq_num+1)], ascii=True):
            frames = list()
            seq_root = opj(
                self.root, 'train' if self.is_train else 'test', str(seq))
            imgdir = opj(seq_root, 'rgb')
            with open(opj(seq_root, 'gt.yml')) as f:
                content = yaml.load(f)
                for key, val in content.items():
                    frame = dict()
                    frame['path'] = opj(imgdir, '%04d.png' % int(key))
                    frame['annots'] = list()
                    for v in val:
                        annot = dict()
                        rot = np.array(v['cam_R_m2c']).reshape(3, 3)
                        tran = np.array(v['cam_t_m2c']).reshape(3, 1)
                        annot['pose'] = np.concatenate((rot, tran), axis=1)
                        # x1 y1 w h => x1 y1 x2 y2
                        bbox = np.array(v['obj_bb'])
                        bbox[2] += bbox[0]
                        bbox[3] += bbox[1]
                        annot['bbox'] = bbox
                        annot['obj_id'] = v['obj_id']
                        annot['kps'] = self._project_kps(
                            self.kps[seq], annot['pose'])
                        frame['annots'].append(annot)
                    frames.append(frame)
            self.frames[seq] = frames

        # Save to pickle path
        try:
            self._save_to_disk()
            print("[LOG] Save benchmark to disk")
        except Exception as e:
            print("[ERROR]", str(e))
            print("[ERROR] Save to disk failed")

    def _project_kps(self, kps, pose):
        """Project 3d vertices to 2d

        Args
        - kps: (np.array) [N x 3] 3d keypoints vertices.
        - pose: (np.array) [4 x 4] pose matrix

        Returns
        - projected: (np.array) [N x 2] projected 2d points
        """
        kps = np.concatenate((kps, np.ones((kps.shape[0], 1))), axis=1)
        projected = np.matmul(np.matmul(self.cam, pose), kps.T)
        projected /= projected[2, :]
        projected = projected[:2, :].T
        return projected

    def _load_from_disk(self):
        assert os.path.exists(self.pklpath) == True, ".pkl file doesn't exist"
        assert os.path.getsize(self.pklpath) > 0, ".pkl file corrupted"
        with open(self.pklpath, 'rb') as handle:
            benchmark = pickle.load(handle)
        assert benchmark['root'] == self.root, "Wrong dataset root"
        assert benchmark['num_kp'] == self.num_kp, "Wrong number of keypoints"
        assert benchmark['unit'] == self.unit, "Wrong unit"
        assert benchmark['pklpath'] == self.pklpath, "Wrong .pkl path"
        self.__dict__ = benchmark

    def _save_to_disk(self):
        if os.path.exists(self.pklpath):
            print("[WARNING] Overwrite benchmark")
            os.remove(self.pklpath)
        with open(self.pklpath, 'wb') as output:
            pickle.dump(self.__dict__, output, pickle.HIGHEST_PROTOCOL)
