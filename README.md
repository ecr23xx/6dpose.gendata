# 6dpose.gendata

Tools for generating synthetic 6DoF pose estimation training images. Now it only supports SIXD's hinterstoisser dataset. In the future, it will support SIXD's other datasets, and YCB video datasets.

## Download

- [SIXD](http://cmp.felk.cvut.cz/sixd/challenge_2017/)

## Workflow

1. Load rendered images from `$SIXDROOT/train/rgb`
2. Load background images from `$COCOROOT`
3. Stick rendered images into background with some data augumentation
4. Save annotation
    - bounding box
    - keypoints position
    - pose

## Example

Gaussian blur

![](assets/gaussian.png)

Motion blur

![](assets/motion.png)

## TODO

- [ ] Basic
    - [x] ~~Load SIXD information~~
    - [ ] Generate keypoints
    - [x] ~~Stick image~~
    - [x] Save annotation
    - [x] ~~Data augmentation~~
        - [x] ~~Scale~~
        - [x] ~~Motion blur~~
        - [x] ~~Gaussian blur~~
        - [x] ~~Box blur~~
- [ ] Advanced
    - [ ] Lighting
    - [ ] Texture
