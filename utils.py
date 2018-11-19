import numpy as np


def project_vertices(vertices, pose, cam, offset=0):
    """Project 3d vertices to 2d

    Args
    - vertices: (np.array) [N x 3] 3d vertices.
    - pose: (np.array) [4 x 4] pose matrix.
    - cam: (np.array) [3 x 3] camera matrix.

    Returns
    - projected: (np.array) [N x 2] projected 2d points
    """
    vertices = np.concatenate(
        (vertices, np.ones((vertices.shape[0], 1))), axis=1)
    projected = np.matmul(np.matmul(cam, pose), vertices.T)
    projected /= projected[2, :]
    projected = projected[:2, :].T
    return projected


def get_3D_corners(vertices):
    """Get 3D corners of vertices

    Args
    - vertices: (np.array) [N x 3] 3d vertices.

    Returns
    - corners: (np.array) [N x 3] Corner vertices.
    """
    min_x = np.min(vertices[:, 0])
    max_x = np.max(vertices[:, 0])
    min_y = np.min(vertices[:, 1])
    max_y = np.max(vertices[:, 1])
    min_z = np.min(vertices[:, 2])
    max_z = np.max(vertices[:, 2])
    corners = np.array([[min_x, min_y, min_z],
                        [min_x, min_y, max_z],
                        [min_x, max_y, min_z],
                        [min_x, max_y, max_z],
                        [max_x, min_y, min_z],
                        [max_x, min_y, max_z],
                        [max_x, max_y, min_z],
                        [max_x, max_y, max_z]])
    return corners