# ------------------------------------------------------------------------------
# Copyright (c) 2018 Gao Peng
# Licensed under the MIT License.
# Written by: Gao PENG (ecr23pg@gmail.com)
# ------------------------------------------------------------------------------

import numpy as np
from PIL import Image, ImageFilter


def random_scale(frame, annot, min_sf, max_sf):
    """
    Randomly scale frame

    Args
    - frame: (Pillow.Image)
    - annot: (dict) Keys and values are
        - bbox: (np.array) [4] bbox annotation
        - pose: (np.array) [3 x 4] pose annotation
        - kps: (np.array) [K x 2] keypoints annotation,
               K for number of keypoints
        - obj_id: (np.array) [N] object ids, range from [1,15]
    - min_sf: (float) Minimum scaling factor
    - max: (float) Maximum scaling factor

    Returns
    - scaled_frame: (Pillow.Image) Scaled image
    - scaled_annot: (dict) Scaled annotation
    """
    w, h = frame.size
    sf = (max_sf - min_sf) * np.random.random() + min_sf
    scaled_frame = frame.resize((int(w * sf), int(h * sf)), Image.BICUBIC)
    scaled_annot = dict()
    scaled_annot['bbox'] = (annot['bbox'] * sf).astype(int)
    scaled_annot['kps'] = annot['kps'] * sf
    scaled_annot['pose'] = annot['pose']
    scaled_annot['obj_id'] = annot['obj_id']
    return scaled_frame, scaled_annot, sf


def random_blur(img, prob):
    """
    Randomly blur an image.

    Args
    - img: (Pillow.Image)
    - prob: Probability to blur
    """
    if np.random.random() > prob:
        return img

    # TODO: stronger blur
    filters = [
        ImageFilter.BoxBlur(3),
        ImageFilter.GaussianBlur(3),
        ImageFilter.Kernel((5, 5), (1, 0, 0, 0, 0,
                                    0, 1, 0, 0, 0,
                                    0, 0, 1, 0, 0,
                                    0, 0, 0, 1, 0,
                                    0, 0, 0, 0, 1)),
        ImageFilter.Kernel((5, 5), (0, 0, 0, 0, 1,
                                    0, 0, 0, 1, 0,
                                    0, 0, 1, 0, 0,
                                    0, 1, 0, 0, 0,
                                    1, 0, 0, 0, 0)),
        ImageFilter.Kernel((5, 5), (0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0,
                                    1, 1, 1, 1, 1,
                                    0, 0, 0, 0, 0,
                                    0, 0, 0, 0, 0)),
        ImageFilter.Kernel((5, 5), (0, 0, 1, 0, 0,
                                    0, 0, 1, 0, 0,
                                    0, 0, 1, 0, 0,
                                    0, 0, 1, 0, 0,
                                    0, 0, 1, 0, 0)),
    ]

    img = img.filter(np.random.choice(filters))

    return img
