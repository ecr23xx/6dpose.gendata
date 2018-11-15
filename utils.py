import numpy as np

def project_vertices(vertices, pose, cam, offset=0):
    """Project 3d vertices to 2d

    Args
    - vertices: (np.array) [N x 3] 3d vertices.
    - pose: (np.array) [4 x 4] pose matrix
    - cam: (np.array) [3 x 3] camera matrix

    Returns
    - projected: (np.array) [N x 2] projected 2d points
    """
    vertices = np.concatenate(
        (vertices, np.ones((vertices.shape[0], 1))), axis=1)
    projected = np.matmul(np.matmul(cam, pose), vertices.T)
    projected /= projected[2, :]
    projected = projected[:2, :].T
    return projected