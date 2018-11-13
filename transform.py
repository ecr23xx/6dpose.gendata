import numpy as np
from PIL import Image, ImageFilter


def random_scale(frame, bbox, min, max):
    """
    Randomly scale frame

    Args
    - frame: (Pillow.Image)
    - bbox: (np.array) [4]
    - min: (float) Minimum scaling factor
    - max: (float) Maximum scaling factor

    Returns
    - scaled_frame:
    - scaled_bbox:
    """
    w, h = frame.size
    sf = (max - min) * np.random.random() + min
    scaled_frame = frame.resize((int(w * sf), int(h * sf)), Image.BICUBIC)
    scaled_bbox = bbox.astype(float) * sf
    return scaled_frame, scaled_bbox.astype(int)


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
