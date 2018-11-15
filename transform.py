import numpy as np
from PIL import Image, ImageFilter


def random_scale(frame, annot, min, max):
    """
    Randomly scale frame

    Args
    - frame: (Pillow.Image)
    - annot: (dict) Keys and values are
        - bbox: (np.array) [4] bbox annotation 
        - pose: (np.array) [3 x 4] pose annotation
        - kps: (np.array) [K x 2] keypoints annotation,
               K for number of keypoints
        - obj_ids: (np.array) [N] object ids, range from [1,15]
    - min: (float) Minimum scaling factor
    - max: (float) Maximum scaling factor

    Returns
    - scaled_frame: (Pillow.Image) Scaled image
    - annot: (dict) Scaled annotation
    """
    w, h = frame.size
    sf = (max - min) * np.random.random() + min
    scaled_frame = frame.resize((int(w * sf), int(h * sf)), Image.BICUBIC)
    annot['bbox'] = (annot['bbox'] * sf).astype(int)
    annot['kps'] *= sf
    return scaled_frame, annot, sf


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
