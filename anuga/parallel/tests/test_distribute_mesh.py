#!/usr/bin/env python


import unittest
import sys
from math import sqrt
from pprint import pprint


from anuga import Domain
from anuga import rectangular_cross

from anuga.parallel.distribute_mesh import pmesh_divide_metis
from anuga.parallel.distribute_mesh import build_submesh
from anuga.parallel.distribute_mesh import (
    submesh_full,
    submesh_ghost,
    submesh_quantities,
)
from anuga.parallel.distribute_mesh import extract_submesh, rec_submesh, send_submesh

import numpy as num

# Setup to skip test if mpi4py not available
import sys

try:
    import mpi4py
except ImportError:
    pass

import pytest


def topography(x, y):
    return -x / 2


def xcoord(x, y):
    return x


def ycoord(x, y):
    return y


@pytest.mark.skipif("mpi4py" not in sys.modules, reason="requires the mpi4py module")
class Test_Distribute_Mesh(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pmesh_1(self):
        """
        test distributing with just one processor
        """

        points, vertices, boundary = rectangular_cross(2, 2)

        true_points = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        true_vertices = [
            [0, 9, 1],
            [3, 9, 0],
            [4, 9, 3],
            [1, 9, 4],
            [1, 10, 2],
            [4, 10, 1],
            [5, 10, 4],
            [2, 10, 5],
            [3, 11, 4],
            [6, 11, 3],
            [7, 11, 6],
            [4, 11, 7],
            [4, 12, 5],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
        ]

        assert num.allclose(points, true_points)
        assert num.allclose(vertices, true_vertices)

        domain = Domain(points, vertices, boundary)

        domain.set_quantity("elevation", topography)  # Use function for elevation
        domain.set_quantity("friction", 0.0)  # Constant friction
        domain.set_quantity("stage", expression="elevation")  # Dry initial stage
        domain.set_quantity("xmomentum", expression="friction + 2.0")  #
        domain.set_quantity("ymomentum", ycoord)  #

        # print domain.quantities['ymomentum'].centroid_values

        nodes, triangles, boundary, triangles_per_proc, quantities = pmesh_divide_metis(
            domain, 1
        )

        true_nodes = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        true_triangles = [
            [0, 9, 1],
            [3, 9, 0],
            [4, 9, 3],
            [1, 9, 4],
            [1, 10, 2],
            [4, 10, 1],
            [5, 10, 4],
            [2, 10, 5],
            [3, 11, 4],
            [6, 11, 3],
            [7, 11, 6],
            [4, 11, 7],
            [4, 12, 5],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
        ]

        assert num.allclose(nodes, true_nodes)
        assert num.allclose(triangles, true_triangles)

        assert num.allclose(triangles_per_proc, [16])

    def test_pmesh_2(self):
        """
        Test 2 way pmesh
        """

        # FIXME: Need to update expected values on macos
        if sys.platform == "darwin":
            return

        points, vertices, boundary = rectangular_cross(2, 2)

        true_points = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        true_vertices = [
            [0, 9, 1],
            [3, 9, 0],
            [4, 9, 3],
            [1, 9, 4],
            [1, 10, 2],
            [4, 10, 1],
            [5, 10, 4],
            [2, 10, 5],
            [3, 11, 4],
            [6, 11, 3],
            [7, 11, 6],
            [4, 11, 7],
            [4, 12, 5],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
        ]

        assert num.allclose(points, true_points)
        assert num.allclose(vertices, true_vertices)

        domain = Domain(points, vertices, boundary)

        domain.set_quantity("elevation", topography)  # Use function for elevation
        domain.set_quantity("friction", 0.0)  # Constant friction
        domain.set_quantity("stage", expression="elevation")  # Dry initial stage
        domain.set_quantity("xmomentum", expression="friction + 2.0")  #
        domain.set_quantity("ymomentum", ycoord)  #

        # print domain.quantities['ymomentum'].centroid_values

        nodes, triangles, boundary, triangles_per_proc, quantities = pmesh_divide_metis(
            domain, 2
        )

        true_nodes = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        # Triangles ordered differently in metis4 and metis5
        true_triangles_4 = [
            [0, 9, 1],
            [3, 9, 0],
            [4, 9, 3],
            [1, 9, 4],
            [4, 10, 1],
            [3, 11, 4],
            [4, 11, 7],
            [4, 12, 5],
            [1, 10, 2],
            [5, 10, 4],
            [2, 10, 5],
            [6, 11, 3],
            [7, 11, 6],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
        ]

        from numpy import array

        true_triangles_5 = array(
            [
                [0, 9, 1],
                [3, 9, 0],
                [4, 9, 3],
                [1, 9, 4],
                [1, 10, 2],
                [4, 10, 1],
                [5, 10, 4],
                [2, 10, 5],
                [3, 11, 4],
                [6, 11, 3],
                [7, 11, 6],
                [4, 11, 7],
                [4, 12, 5],
                [7, 12, 4],
                [8, 12, 7],
                [5, 12, 8],
            ]
        )

        true_triangles_win_4 = array(
            [
                [4, 9, 3],
                [1, 9, 4],
                [4, 10, 1],
                [5, 10, 4],
                [4, 11, 7],
                [4, 12, 5],
                [7, 12, 4],
                [8, 12, 7],
                [0, 9, 1],
                [3, 9, 0],
                [1, 10, 2],
                [2, 10, 5],
                [3, 11, 4],
                [6, 11, 3],
                [7, 11, 6],
                [5, 12, 8],
            ]
        )

        true_triangles_5_part_mesh = array(
            [
                [4, 9, 3],
                [1, 9, 4],
                [1, 10, 2],
                [4, 10, 1],
                [5, 10, 4],
                [2, 10, 5],
                [3, 11, 4],
                [4, 11, 7],
                [4, 12, 5],
                [0, 9, 1],
                [3, 9, 0],
                [6, 11, 3],
                [7, 11, 6],
                [7, 12, 4],
                [8, 12, 7],
                [5, 12, 8],
            ]
        )

        true_triangles_meshpy_2022_1_3_win_1 = array(
            [
                [0, 9, 1],
                [3, 9, 0],
                [4, 9, 3],
                [1, 9, 4],
                [1, 10, 2],
                [4, 10, 1],
                [5, 10, 4],
                [2, 10, 5],
                [3, 11, 4],
                [6, 11, 3],
                [7, 11, 6],
                [4, 11, 7],
                [4, 12, 5],
                [7, 12, 4],
                [8, 12, 7],
                [5, 12, 8],
            ]
        )

        true_triangles_meshpy_2022_1_3_win_2 = array(
            [
                [4, 9, 3],
                [1, 9, 4],
                [4, 10, 1],
                [5, 10, 4],
                [3, 11, 4],
                [6, 11, 3],
                [7, 11, 6],
                [4, 11, 7],
                [7, 12, 4],
                [0, 9, 1],
                [3, 9, 0],
                [1, 10, 2],
                [2, 10, 5],
                [4, 12, 5],
                [8, 12, 7],
                [5, 12, 8],
            ]
        )

        true_triangles_meshpy_2022_1_3 = array(
            [
                [0, 9, 1],
                [3, 9, 0],
                [4, 9, 3],
                [1, 9, 4],
                [4, 10, 1],
                [5, 10, 4],
                [3, 11, 4],
                [4, 12, 5],
                [7, 12, 4],
                [1, 10, 2],
                [2, 10, 5],
                [6, 11, 3],
                [7, 11, 6],
                [4, 11, 7],
                [8, 12, 7],
                [5, 12, 8],
            ]
        )

        true_triangles_meshpy_2022_1_4 = array(
            [
                [0, 9, 1],
                [3, 9, 0],
                [1, 9, 4],
                [1, 10, 2],
                [4, 10, 1],
                [5, 10, 4],
                [2, 10, 5],
                [4, 9, 3],
                [3, 11, 4],
                [6, 11, 3],
                [7, 11, 6],
                [4, 11, 7],
                [4, 12, 5],
                [7, 12, 4],
                [8, 12, 7],
                [5, 12, 8],
            ]
        )

        true_triangles_meshpy_2024_1_win_1 = array(
            [
                [ 6, 11,  3],
                [ 7, 11,  6],
                [ 4, 11,  7],
                [ 4, 12,  5],
                [ 7, 12,  4],
                [ 8, 12,  7],
                [ 5, 12,  8],
                [ 0,  9,  1],
                [ 3,  9,  0],
                [ 4,  9,  3],
                [ 1,  9,  4],
                [ 1, 10,  2],
                [ 4, 10,  1],
                [ 5, 10,  4],
                [ 2, 10,  5],
                [ 3, 11,  4],
            ]
        )

        assert num.allclose(nodes, true_nodes)

        pprint(triangles)

        assert (
            num.allclose(triangles, true_triangles_4)
            or num.allclose(triangles, true_triangles_5)
            or num.allclose(triangles, true_triangles_win_4)
            or num.allclose(triangles, true_triangles_5_part_mesh)
            or num.allclose(triangles, true_triangles_meshpy_2022_1_3)
            or num.allclose(triangles, true_triangles_meshpy_2022_1_4)
            or num.allclose(triangles, true_triangles_meshpy_2022_1_3_win_1)
            or num.allclose(triangles, true_triangles_meshpy_2022_1_3_win_2)
            or num.allclose(triangles, true_triangles_meshpy_2024_1_win_1)
        )

        print(triangles_per_proc)
        assert (
            num.allclose(triangles_per_proc, [8, 8])
            or num.allclose(triangles_per_proc, [9, 7])
            or num.allclose(triangles_per_proc, [7, 9])
        )

    def test_build_submesh_3(self):
        """
        Test 3 way build_submesh
        """

        nodes = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        triangles = [
            [4, 9, 3],
            [4, 12, 5],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
            [0, 9, 1],
            [1, 9, 4],
            [1, 10, 2],
            [4, 10, 1],
            [5, 10, 4],
            [2, 10, 5],
            [3, 9, 0],
            [3, 11, 4],
            [6, 11, 3],
            [7, 11, 6],
            [4, 11, 7],
        ]

        boundary = {
            (13, 1): "bottom",
            (7, 1): "left",
            (3, 1): "right",
            (14, 1): "right",
            (11, 1): "bottom",
            (10, 1): "top",
            (5, 1): "left",
            (4, 1): "top",
        }

        triangles_per_proc = [5, 6, 5]

        quantities = {
            "stage": num.array(
                [
                    [-0.25, -0.125, -0.25],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                    [-0.0, -0.125, -0.0],
                    [-0.0, -0.125, -0.25],
                    [-0.0, -0.125, -0.0],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.125, -0.25],
                    [-0.0, -0.125, -0.25],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                ]
            ),
            "elevation": num.array(
                [
                    [-0.25, -0.125, -0.25],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                    [-0.0, -0.125, -0.0],
                    [-0.0, -0.125, -0.25],
                    [-0.0, -0.125, -0.0],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.125, -0.25],
                    [-0.0, -0.125, -0.25],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                ]
            ),
            "ymomentum": num.array(
                [
                    [0.5, 0.25, 0.0],
                    [0.5, 0.75, 1.0],
                    [0.5, 0.75, 0.5],
                    [1.0, 0.75, 0.5],
                    [1.0, 0.75, 1.0],
                    [0.0, 0.25, 0.5],
                    [0.5, 0.25, 0.5],
                    [0.5, 0.75, 1.0],
                    [0.5, 0.75, 0.5],
                    [1.0, 0.75, 0.5],
                    [1.0, 0.75, 1.0],
                    [0.0, 0.25, 0.0],
                    [0.0, 0.25, 0.5],
                    [0.0, 0.25, 0.0],
                    [0.5, 0.25, 0.0],
                    [0.5, 0.25, 0.5],
                ]
            ),
            "friction": num.array(
                [
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ]
            ),
            "xmomentum": num.array(
                [
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                ]
            ),
        }

        true_submesh = {
            "full_boundary": [
                {(3, 1): "right", (4, 1): "top"},
                {(5, 1): "left", (10, 1): "top", (7, 1): "left"},
                {(13, 1): "bottom", (14, 1): "right", (11, 1): "bottom"},
            ],
            "ghost_nodes": [
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.5],
                        [2.0, 0.0, 1.0],
                        [6.0, 1.0, 0.0],
                        [10.0, 0.25, 0.75],
                        [11.0, 0.75, 0.25],
                    ]
                ),
                num.array(
                    [
                        [3.0, 0.5, 0.0],
                        [7.0, 1.0, 0.5],
                        [8.0, 1.0, 1.0],
                        [11.0, 0.75, 0.25],
                        [12.0, 0.75, 0.75],
                    ]
                ),
                num.array(
                    [
                        [1.0, 0.0, 0.5],
                        [5.0, 0.5, 1.0],
                        [8.0, 1.0, 1.0],
                        [12.0, 0.75, 0.75],
                    ]
                ),
            ],
            "full_nodes": [
                num.array(
                    [
                        [3.0, 0.5, 0.0],
                        [4.0, 0.5, 0.5],
                        [5.0, 0.5, 1.0],
                        [7.0, 1.0, 0.5],
                        [8.0, 1.0, 1.0],
                        [9.0, 0.25, 0.25],
                        [12.0, 0.75, 0.75],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.5],
                        [2.0, 0.0, 1.0],
                        [4.0, 0.5, 0.5],
                        [5.0, 0.5, 1.0],
                        [9.0, 0.25, 0.25],
                        [10.0, 0.25, 0.75],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [3.0, 0.5, 0.0],
                        [4.0, 0.5, 0.5],
                        [6.0, 1.0, 0.0],
                        [7.0, 1.0, 0.5],
                        [9.0, 0.25, 0.25],
                        [11.0, 0.75, 0.25],
                    ]
                ),
            ],
            "ghost_triangles": [
                num.array(
                    [
                        [5, 0, 9, 1],
                        [6, 1, 9, 4],
                        [8, 4, 10, 1],
                        [9, 5, 10, 4],
                        [10, 2, 10, 5],
                        [11, 3, 9, 0],
                        [12, 3, 11, 4],
                        [13, 6, 11, 3],
                        [14, 7, 11, 6],
                        [15, 4, 11, 7],
                    ]
                ),
                num.array(
                    [
                        [0, 4, 9, 3],
                        [1, 4, 12, 5],
                        [2, 7, 12, 4],
                        [4, 5, 12, 8],
                        [11, 3, 9, 0],
                        [12, 3, 11, 4],
                    ]
                ),
                num.array(
                    [
                        [0, 4, 9, 3],
                        [1, 4, 12, 5],
                        [2, 7, 12, 4],
                        [3, 8, 12, 7],
                        [5, 0, 9, 1],
                        [6, 1, 9, 4],
                    ]
                ),
            ],
            "ghost_boundary": [
                {
                    (13, 1): "ghost",
                    (8, 0): "ghost",
                    (14, 1): "ghost",
                    (11, 1): "ghost",
                    (10, 1): "ghost",
                    (5, 1): "ghost",
                    (10, 2): "ghost",
                },
                {
                    (12, 2): "ghost",
                    (12, 0): "ghost",
                    (2, 1): "ghost",
                    (11, 1): "ghost",
                    (2, 2): "ghost",
                    (4, 1): "ghost",
                    (4, 0): "ghost",
                },
                {
                    (3, 2): "ghost",
                    (6, 1): "ghost",
                    (3, 1): "ghost",
                    (5, 1): "ghost",
                    (1, 0): "ghost",
                    (1, 1): "ghost",
                },
            ],
            "full_triangles": [
                [[4, 9, 3], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]],
                [[0, 9, 1], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5]],
                [[3, 9, 0], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7]],
            ],
            "full_commun": [
                {0: [1, 2], 1: [1, 2], 2: [1, 2], 3: [2], 4: [1]},
                {5: [0, 2], 6: [0, 2], 7: [], 8: [0], 9: [0], 10: [0]},
                {11: [0, 1], 12: [0, 1], 13: [0], 14: [0], 15: [0]},
            ],
            "ghost_commun": [
                num.array(
                    [
                        [5, 1],
                        [6, 1],
                        [8, 1],
                        [9, 1],
                        [10, 1],
                        [11, 2],
                        [12, 2],
                        [13, 2],
                        [14, 2],
                        [15, 2],
                    ]
                ),
                num.array([[0, 0], [1, 0], [2, 0], [4, 0], [11, 2], [12, 2]]),
                num.array([[0, 0], [1, 0], [2, 0], [3, 0], [5, 1], [6, 1]]),
            ],
            "ghost_quan": {
                "stage": [
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.25, -0.375, -0.5],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                ],
                "elevation": [
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.25, -0.375, -0.5],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                ],
                "ymomentum": [
                    num.array(
                        [
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                            [0.0, 0.25, 0.0],
                            [0.5, 0.25, 0.0],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                        ]
                    ),
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                ],
                "friction": [
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                ],
                "xmomentum": [
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                ],
            },
            "full_quan": {
                "stage": [
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.0, -0.125, -0.0],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                ],
                "elevation": [
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.0, -0.125, -0.0],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                ],
                "ymomentum": [
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                            [0.0, 0.25, 0.0],
                            [0.5, 0.25, 0.0],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                ],
                "friction": [
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                ],
                "xmomentum": [
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                ],
            },
        }

        from anuga.abstract_2d_finite_volumes.neighbour_mesh import Mesh

        mesh = Mesh(nodes, triangles, boundary)
        boundary_polygon = mesh.get_boundary_polygon()

        # Subdivide into non-overlapping partitions

        submesh = submesh_full(mesh, triangles_per_proc)

        # print submesh

        for i in range(3):
            assert num.allclose(
                true_submesh["full_triangles"][i], submesh["full_triangles"][i]
            )
            assert num.allclose(true_submesh["full_nodes"][i], submesh["full_nodes"][i])
        assert true_submesh["full_boundary"] == submesh["full_boundary"]

        # Add any extra ghost boundary layer information

        submesh = submesh_ghost(submesh, mesh, triangles_per_proc)

        for i in range(3):
            assert num.allclose(
                true_submesh["ghost_triangles"][i], submesh["ghost_triangles"][i]
            )
            assert num.allclose(
                true_submesh["ghost_nodes"][i], submesh["ghost_nodes"][i]
            )
            assert num.allclose(
                true_submesh["ghost_commun"][i], submesh["ghost_commun"][i]
            )

        assert true_submesh["full_commun"] == submesh["full_commun"]

        # Order the quantities information to be the same as the triangle
        # information

        submesh = submesh_quantities(submesh, quantities, triangles_per_proc)

        for key, value in true_submesh["ghost_quan"].items():
            for i in range(3):
                assert num.allclose(
                    true_submesh["ghost_quan"][key][i], submesh["ghost_quan"][key][i]
                )
                assert num.allclose(
                    true_submesh["full_quan"][key][i], submesh["full_quan"][key][i]
                )

        submesh["boundary_polygon"] = boundary_polygon

    def test_build_submesh_3_layer_4(self):
        """
        Test 3 Layer 4 way build_submesh with ghost_layer_width = 4
        """

        nodes = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        triangles = [
            [4, 9, 3],
            [4, 12, 5],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
            [0, 9, 1],
            [1, 9, 4],
            [1, 10, 2],
            [4, 10, 1],
            [5, 10, 4],
            [2, 10, 5],
            [3, 9, 0],
            [3, 11, 4],
            [6, 11, 3],
            [7, 11, 6],
            [4, 11, 7],
        ]

        boundary = {
            (13, 1): "bottom",
            (7, 1): "left",
            (3, 1): "right",
            (14, 1): "right",
            (11, 1): "bottom",
            (10, 1): "top",
            (5, 1): "left",
            (4, 1): "top",
        }

        r"""
                     top
            (10,1)       (4,1)
        2 ---------- 5 ---------- 8
        | \   10   / | \   04   / |
        |   \    /   |   \    /   |
 (7,1)  | 07  10  09 | 01  12  03 | (3,1)
        |   /    \   |   /    \   |
        | /   08   \ | /   02   \ |
 left   1 ---------- 4 ---------- 7  right
        | \   06   / | \   15   / |
        |   \    /   |   \    /   |
 (5,1)  | 05  09  00 | 12  11  14 | (14,1)
        |   /    \   |   /    \   |
        | /   11   \ | /   13   \ |
        0 ---------- 3 ---------- 6
            (11,1)        (13,1)
                   bottom


        Processor 0 Full Triangles 00,01,02,03,04
        Processor 1 Full Triangles 05,06,07,08,09,10
        Processor 2 Full Triangles 11,12,13,14,15
        """

        triangles_per_proc = [5, 6, 5]

        quantities = {
            "stage": num.array(
                [
                    [-0.25, -0.125, -0.25],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                    [-0.0, -0.125, -0.0],
                    [-0.0, -0.125, -0.25],
                    [-0.0, -0.125, -0.0],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.125, -0.25],
                    [-0.0, -0.125, -0.25],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                ]
            ),
            "elevation": num.array(
                [
                    [-0.25, -0.125, -0.25],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                    [-0.0, -0.125, -0.0],
                    [-0.0, -0.125, -0.25],
                    [-0.0, -0.125, -0.0],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.125, -0.25],
                    [-0.0, -0.125, -0.25],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                ]
            ),
            "ymomentum": num.array(
                [
                    [0.5, 0.25, 0.0],
                    [0.5, 0.75, 1.0],
                    [0.5, 0.75, 0.5],
                    [1.0, 0.75, 0.5],
                    [1.0, 0.75, 1.0],
                    [0.0, 0.25, 0.5],
                    [0.5, 0.25, 0.5],
                    [0.5, 0.75, 1.0],
                    [0.5, 0.75, 0.5],
                    [1.0, 0.75, 0.5],
                    [1.0, 0.75, 1.0],
                    [0.0, 0.25, 0.0],
                    [0.0, 0.25, 0.5],
                    [0.0, 0.25, 0.0],
                    [0.5, 0.25, 0.0],
                    [0.5, 0.25, 0.5],
                ]
            ),
            "friction": num.array(
                [
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ]
            ),
            "xmomentum": num.array(
                [
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                ]
            ),
        }

        true_submesh = {
            "full_boundary": [
                {(3, 1): "right", (4, 1): "top"},
                {(5, 1): "left", (10, 1): "top", (7, 1): "left"},
                {(13, 1): "bottom", (14, 1): "right", (11, 1): "bottom"},
            ],
            "ghost_nodes": [
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.5],
                        [2.0, 0.0, 1.0],
                        [6.0, 1.0, 0.0],
                        [10.0, 0.25, 0.75],
                        [11.0, 0.75, 0.25],
                    ]
                ),
                num.array(
                    [
                        [3.0, 0.5, 0.0],
                        [7.0, 1.0, 0.5],
                        [8.0, 1.0, 1.0],
                        [11.0, 0.75, 0.25],
                        [12.0, 0.75, 0.75],
                    ]
                ),
                num.array(
                    [
                        [1.0, 0.0, 0.5],
                        [5.0, 0.5, 1.0],
                        [8.0, 1.0, 1.0],
                        [12.0, 0.75, 0.75],
                    ]
                ),
            ],
            "full_nodes": [
                num.array(
                    [
                        [3.0, 0.5, 0.0],
                        [4.0, 0.5, 0.5],
                        [5.0, 0.5, 1.0],
                        [7.0, 1.0, 0.5],
                        [8.0, 1.0, 1.0],
                        [9.0, 0.25, 0.25],
                        [12.0, 0.75, 0.75],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.5],
                        [2.0, 0.0, 1.0],
                        [4.0, 0.5, 0.5],
                        [5.0, 0.5, 1.0],
                        [9.0, 0.25, 0.25],
                        [10.0, 0.25, 0.75],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [3.0, 0.5, 0.0],
                        [4.0, 0.5, 0.5],
                        [6.0, 1.0, 0.0],
                        [7.0, 1.0, 0.5],
                        [9.0, 0.25, 0.25],
                        [11.0, 0.75, 0.25],
                    ]
                ),
            ],
            "ghost_triangles": [
                num.array(
                    [
                        [5, 0, 9, 1],
                        [6, 1, 9, 4],
                        [8, 4, 10, 1],
                        [9, 5, 10, 4],
                        [10, 2, 10, 5],
                        [11, 3, 9, 0],
                        [12, 3, 11, 4],
                        [13, 6, 11, 3],
                        [14, 7, 11, 6],
                        [15, 4, 11, 7],
                    ]
                ),
                num.array(
                    [
                        [0, 4, 9, 3],
                        [1, 4, 12, 5],
                        [2, 7, 12, 4],
                        [4, 5, 12, 8],
                        [11, 3, 9, 0],
                        [12, 3, 11, 4],
                    ]
                ),
                num.array(
                    [
                        [0, 4, 9, 3],
                        [1, 4, 12, 5],
                        [2, 7, 12, 4],
                        [3, 8, 12, 7],
                        [5, 0, 9, 1],
                        [6, 1, 9, 4],
                    ]
                ),
            ],
            "ghost_boundary": [
                {
                    (13, 1): "ghost",
                    (8, 0): "ghost",
                    (14, 1): "ghost",
                    (11, 1): "ghost",
                    (10, 1): "ghost",
                    (5, 1): "ghost",
                    (10, 2): "ghost",
                },
                {
                    (12, 2): "ghost",
                    (12, 0): "ghost",
                    (2, 1): "ghost",
                    (11, 1): "ghost",
                    (2, 2): "ghost",
                    (4, 1): "ghost",
                    (4, 0): "ghost",
                },
                {
                    (3, 2): "ghost",
                    (6, 1): "ghost",
                    (3, 1): "ghost",
                    (5, 1): "ghost",
                    (1, 0): "ghost",
                    (1, 1): "ghost",
                },
            ],
            "full_triangles": [
                [[4, 9, 3], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]],
                [[0, 9, 1], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5]],
                [[3, 9, 0], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7]],
            ],
            "full_commun": [
                {0: [1, 2], 1: [1, 2], 2: [1, 2], 3: [2], 4: [1]},
                {5: [0, 2], 6: [0, 2], 7: [], 8: [0], 9: [0], 10: [0]},
                {11: [0, 1], 12: [0, 1], 13: [0], 14: [0], 15: [0]},
            ],
            "ghost_commun": [
                num.array(
                    [
                        [5, 1],
                        [6, 1],
                        [8, 1],
                        [9, 1],
                        [10, 1],
                        [11, 2],
                        [12, 2],
                        [13, 2],
                        [14, 2],
                        [15, 2],
                    ]
                ),
                num.array([[0, 0], [1, 0], [2, 0], [4, 0], [11, 2], [12, 2]]),
                num.array([[0, 0], [1, 0], [2, 0], [3, 0], [5, 1], [6, 1]]),
            ],
            "ghost_quan": {
                "stage": [
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.25, -0.375, -0.5],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                ],
                "elevation": [
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.25, -0.375, -0.5],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                ],
                "ymomentum": [
                    num.array(
                        [
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                            [0.0, 0.25, 0.0],
                            [0.5, 0.25, 0.0],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                        ]
                    ),
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                ],
                "friction": [
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                ],
                "xmomentum": [
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                ],
            },
            "full_quan": {
                "stage": [
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.0, -0.125, -0.0],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                ],
                "elevation": [
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.0, -0.125, -0.0],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                ],
                "ymomentum": [
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                            [0.0, 0.25, 0.0],
                            [0.5, 0.25, 0.0],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                ],
                "friction": [
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                ],
                "xmomentum": [
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                ],
            },
        }

        # setup parameters to test using different ghost_layer_widths
        parameters = dict(ghost_layer_width=1)

        from anuga.abstract_2d_finite_volumes.neighbour_mesh import Mesh

        mesh = Mesh(nodes, triangles, boundary)
        boundary_polygon = mesh.get_boundary_polygon()

        # Subdivide into non-overlapping partitions

        submesh = submesh_full(mesh, triangles_per_proc)

        for i in range(3):
            assert num.allclose(
                true_submesh["full_triangles"][i], submesh["full_triangles"][i]
            )
            assert num.allclose(true_submesh["full_nodes"][i], submesh["full_nodes"][i])
        assert true_submesh["full_boundary"] == submesh["full_boundary"]

        # Add any extra ghost boundary layer information

        submesh = submesh_ghost(submesh, mesh, triangles_per_proc, parameters)

        # print submesh

        # print 'ghost_triangles', submesh['ghost_triangles']
        # print 'ghost_boundary', submesh['ghost_boundary']
        # print 'ghost_nodes', submesh['ghost_nodes']
        # print 'ghost_commun', submesh['ghost_commun']

        true_submesh["ghost_boundary"] = [
            {
                (12, 2): "ghost",
                (9, 0): "ghost",
                (9, 2): "ghost",
                (6, 1): "ghost",
                (15, 0): "ghost",
                (11, 1): "bottom",
                (11, 0): "ghost",
                (6, 2): "ghost",
            },
            {(0, 1): "ghost", (1, 2): "ghost", (1, 0): "ghost", (11, 1): "bottom"},
            {
                (5, 1): "left",
                (2, 0): "ghost",
                (0, 2): "ghost",
                (5, 0): "ghost",
                (2, 2): "ghost",
            },
        ]

        true_submesh["ghost_triangles"] = [
            num.array(
                [
                    [6, 1, 9, 4],
                    [9, 5, 10, 4],
                    [11, 3, 9, 0],
                    [12, 3, 11, 4],
                    [15, 4, 11, 7],
                ]
            ),
            num.array([[0, 4, 9, 3], [1, 4, 12, 5], [11, 3, 9, 0]]),
            num.array([[0, 4, 9, 3], [2, 7, 12, 4], [5, 0, 9, 1]]),
        ]

        true_submesh["ghost_nodes"] = [
            num.array(
                [
                    [0.0, 0.0, 0.0],
                    [1.0, 0.0, 0.5],
                    [10.0, 0.25, 0.75],
                    [11.0, 0.75, 0.25],
                ]
            ),
            num.array([[3.0, 0.5, 0.0], [12.0, 0.75, 0.75]]),
            num.array([[1.0, 0.0, 0.5], [12.0, 0.75, 0.75]]),
        ]

        true_submesh["ghost_commun"] = [
            num.array([[6, 1], [9, 1], [11, 2], [12, 2], [15, 2]]),
            num.array([[0, 0], [1, 0], [11, 2]]),
            num.array([[0, 0], [2, 0], [5, 1]]),
        ]

        for i in range(3):
            assert true_submesh["ghost_boundary"][i] == submesh["ghost_boundary"][i]
            assert num.allclose(
                true_submesh["ghost_triangles"][i], submesh["ghost_triangles"][i]
            )
            assert num.allclose(
                true_submesh["ghost_nodes"][i], submesh["ghost_nodes"][i]
            )
            assert num.allclose(
                true_submesh["ghost_commun"][i], submesh["ghost_commun"][i]
            )

        true_submesh["full_commun"] = [
            {0: [1, 2], 1: [1], 2: [2], 3: [], 4: []},
            {5: [2], 6: [0], 7: [], 8: [], 9: [0], 10: []},
            {11: [0, 1], 12: [0], 13: [], 14: [], 15: [0]},
        ]

        assert true_submesh["full_commun"] == submesh["full_commun"]

        # Order the quantities information to be the same as the triangle
        # information

        submesh = submesh_quantities(submesh, quantities, triangles_per_proc)

        # print submesh['full_quan']

        true_submesh["full_quan"] = {
            "stage": [
                num.array(
                    [
                        [-0.25, -0.125, -0.25],
                        [-0.25, -0.375, -0.25],
                        [-0.5, -0.375, -0.25],
                        [-0.5, -0.375, -0.5],
                        [-0.25, -0.375, -0.5],
                    ]
                ),
                num.array(
                    [
                        [-0.0, -0.125, -0.0],
                        [-0.0, -0.125, -0.25],
                        [-0.0, -0.125, -0.0],
                        [-0.25, -0.125, -0.0],
                        [-0.25, -0.125, -0.25],
                        [-0.0, -0.125, -0.25],
                    ]
                ),
                num.array(
                    [
                        [-0.25, -0.125, -0.0],
                        [-0.25, -0.375, -0.25],
                        [-0.5, -0.375, -0.25],
                        [-0.5, -0.375, -0.5],
                        [-0.25, -0.375, -0.5],
                    ]
                ),
            ],
            "elevation": [
                num.array(
                    [
                        [-0.25, -0.125, -0.25],
                        [-0.25, -0.375, -0.25],
                        [-0.5, -0.375, -0.25],
                        [-0.5, -0.375, -0.5],
                        [-0.25, -0.375, -0.5],
                    ]
                ),
                num.array(
                    [
                        [-0.0, -0.125, -0.0],
                        [-0.0, -0.125, -0.25],
                        [-0.0, -0.125, -0.0],
                        [-0.25, -0.125, -0.0],
                        [-0.25, -0.125, -0.25],
                        [-0.0, -0.125, -0.25],
                    ]
                ),
                num.array(
                    [
                        [-0.25, -0.125, -0.0],
                        [-0.25, -0.375, -0.25],
                        [-0.5, -0.375, -0.25],
                        [-0.5, -0.375, -0.5],
                        [-0.25, -0.375, -0.5],
                    ]
                ),
            ],
            "ymomentum": [
                num.array(
                    [
                        [0.5, 0.25, 0.0],
                        [0.5, 0.75, 1.0],
                        [0.5, 0.75, 0.5],
                        [1.0, 0.75, 0.5],
                        [1.0, 0.75, 1.0],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.25, 0.5],
                        [0.5, 0.25, 0.5],
                        [0.5, 0.75, 1.0],
                        [0.5, 0.75, 0.5],
                        [1.0, 0.75, 0.5],
                        [1.0, 0.75, 1.0],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.25, 0.0],
                        [0.0, 0.25, 0.5],
                        [0.0, 0.25, 0.0],
                        [0.5, 0.25, 0.0],
                        [0.5, 0.25, 0.5],
                    ]
                ),
            ],
            "friction": [
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ]
                ),
            ],
            "xmomentum": [
                num.array(
                    [
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                    ]
                ),
                num.array(
                    [
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                    ]
                ),
                num.array(
                    [
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                    ]
                ),
            ],
        }

        true_submesh["ghost_quan"] = {
            "stage": [
                num.array(
                    [
                        [-0.0, -0.125, -0.25],
                        [-0.25, -0.125, -0.25],
                        [-0.25, -0.125, -0.0],
                        [-0.25, -0.375, -0.25],
                        [-0.25, -0.375, -0.5],
                    ]
                ),
                num.array(
                    [
                        [-0.25, -0.125, -0.25],
                        [-0.25, -0.375, -0.25],
                        [-0.25, -0.125, -0.0],
                    ]
                ),
                num.array(
                    [
                        [-0.25, -0.125, -0.25],
                        [-0.5, -0.375, -0.25],
                        [-0.0, -0.125, -0.0],
                    ]
                ),
            ],
            "elevation": [
                num.array(
                    [
                        [-0.0, -0.125, -0.25],
                        [-0.25, -0.125, -0.25],
                        [-0.25, -0.125, -0.0],
                        [-0.25, -0.375, -0.25],
                        [-0.25, -0.375, -0.5],
                    ]
                ),
                num.array(
                    [
                        [-0.25, -0.125, -0.25],
                        [-0.25, -0.375, -0.25],
                        [-0.25, -0.125, -0.0],
                    ]
                ),
                num.array(
                    [
                        [-0.25, -0.125, -0.25],
                        [-0.5, -0.375, -0.25],
                        [-0.0, -0.125, -0.0],
                    ]
                ),
            ],
            "ymomentum": [
                num.array(
                    [
                        [0.5, 0.25, 0.5],
                        [1.0, 0.75, 0.5],
                        [0.0, 0.25, 0.0],
                        [0.0, 0.25, 0.5],
                        [0.5, 0.25, 0.5],
                    ]
                ),
                num.array([[0.5, 0.25, 0.0], [0.5, 0.75, 1.0], [0.0, 0.25, 0.0]]),
                num.array([[0.5, 0.25, 0.0], [0.5, 0.75, 0.5], [0.0, 0.25, 0.5]]),
            ],
            "friction": [
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ]
                ),
                num.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
                num.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]),
            ],
            "xmomentum": [
                num.array(
                    [
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                        [2.0, 2.0, 2.0],
                    ]
                ),
                num.array([[2.0, 2.0, 2.0], [2.0, 2.0, 2.0], [2.0, 2.0, 2.0]]),
                num.array([[2.0, 2.0, 2.0], [2.0, 2.0, 2.0], [2.0, 2.0, 2.0]]),
            ],
        }

        for key, value in true_submesh["ghost_quan"].items():
            for i in range(3):
                assert num.allclose(
                    true_submesh["ghost_quan"][key][i], submesh["ghost_quan"][key][i]
                )
                assert num.allclose(
                    true_submesh["full_quan"][key][i], submesh["full_quan"][key][i]
                )

        submesh["boundary_polygon"] = boundary_polygon

    def test_build_extract_submesh_3(self):
        """
        Test 3 way extract_submesh
        """

        nodes = [
            [0.0, 0.0],
            [0.0, 0.5],
            [0.0, 1.0],
            [0.5, 0.0],
            [0.5, 0.5],
            [0.5, 1.0],
            [1.0, 0.0],
            [1.0, 0.5],
            [1.0, 1.0],
            [0.25, 0.25],
            [0.25, 0.75],
            [0.75, 0.25],
            [0.75, 0.75],
        ]

        triangles = [
            [4, 9, 3],
            [4, 12, 5],
            [7, 12, 4],
            [8, 12, 7],
            [5, 12, 8],
            [0, 9, 1],
            [1, 9, 4],
            [1, 10, 2],
            [4, 10, 1],
            [5, 10, 4],
            [2, 10, 5],
            [3, 9, 0],
            [3, 11, 4],
            [6, 11, 3],
            [7, 11, 6],
            [4, 11, 7],
        ]

        boundary = {
            (13, 1): "bottom",
            (7, 1): "left",
            (3, 1): "right",
            (14, 1): "right",
            (11, 1): "bottom",
            (10, 1): "top",
            (5, 1): "left",
            (4, 1): "top",
        }

        triangles_per_proc = [5, 6, 5]

        quantities = {
            "stage": num.array(
                [
                    [-0.25, -0.125, -0.25],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                    [-0.0, -0.125, -0.0],
                    [-0.0, -0.125, -0.25],
                    [-0.0, -0.125, -0.0],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.125, -0.25],
                    [-0.0, -0.125, -0.25],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                ]
            ),
            "elevation": num.array(
                [
                    [-0.25, -0.125, -0.25],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                    [-0.0, -0.125, -0.0],
                    [-0.0, -0.125, -0.25],
                    [-0.0, -0.125, -0.0],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.125, -0.25],
                    [-0.0, -0.125, -0.25],
                    [-0.25, -0.125, -0.0],
                    [-0.25, -0.375, -0.25],
                    [-0.5, -0.375, -0.25],
                    [-0.5, -0.375, -0.5],
                    [-0.25, -0.375, -0.5],
                ]
            ),
            "ymomentum": num.array(
                [
                    [0.5, 0.25, 0.0],
                    [0.5, 0.75, 1.0],
                    [0.5, 0.75, 0.5],
                    [1.0, 0.75, 0.5],
                    [1.0, 0.75, 1.0],
                    [0.0, 0.25, 0.5],
                    [0.5, 0.25, 0.5],
                    [0.5, 0.75, 1.0],
                    [0.5, 0.75, 0.5],
                    [1.0, 0.75, 0.5],
                    [1.0, 0.75, 1.0],
                    [0.0, 0.25, 0.0],
                    [0.0, 0.25, 0.5],
                    [0.0, 0.25, 0.0],
                    [0.5, 0.25, 0.0],
                    [0.5, 0.25, 0.5],
                ]
            ),
            "friction": num.array(
                [
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ]
            ),
            "xmomentum": num.array(
                [
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                    [2.0, 2.0, 2.0],
                ]
            ),
        }

        true_submesh = {
            "full_boundary": [
                {(3, 1): "right", (4, 1): "top"},
                {(5, 1): "left", (10, 1): "top", (7, 1): "left"},
                {(13, 1): "bottom", (14, 1): "right", (11, 1): "bottom"},
            ],
            "ghost_nodes": [
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.5],
                        [2.0, 0.0, 1.0],
                        [6.0, 1.0, 0.0],
                        [10.0, 0.25, 0.75],
                        [11.0, 0.75, 0.25],
                    ]
                ),
                num.array(
                    [
                        [3.0, 0.5, 0.0],
                        [7.0, 1.0, 0.5],
                        [8.0, 1.0, 1.0],
                        [11.0, 0.75, 0.25],
                        [12.0, 0.75, 0.75],
                    ]
                ),
                num.array(
                    [
                        [1.0, 0.0, 0.5],
                        [5.0, 0.5, 1.0],
                        [8.0, 1.0, 1.0],
                        [12.0, 0.75, 0.75],
                    ]
                ),
            ],
            "full_nodes": [
                num.array(
                    [
                        [3.0, 0.5, 0.0],
                        [4.0, 0.5, 0.5],
                        [5.0, 0.5, 1.0],
                        [7.0, 1.0, 0.5],
                        [8.0, 1.0, 1.0],
                        [9.0, 0.25, 0.25],
                        [12.0, 0.75, 0.75],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [1.0, 0.0, 0.5],
                        [2.0, 0.0, 1.0],
                        [4.0, 0.5, 0.5],
                        [5.0, 0.5, 1.0],
                        [9.0, 0.25, 0.25],
                        [10.0, 0.25, 0.75],
                    ]
                ),
                num.array(
                    [
                        [0.0, 0.0, 0.0],
                        [3.0, 0.5, 0.0],
                        [4.0, 0.5, 0.5],
                        [6.0, 1.0, 0.0],
                        [7.0, 1.0, 0.5],
                        [9.0, 0.25, 0.25],
                        [11.0, 0.75, 0.25],
                    ]
                ),
            ],
            "ghost_triangles": [
                num.array(
                    [
                        [5, 0, 9, 1],
                        [6, 1, 9, 4],
                        [8, 4, 10, 1],
                        [9, 5, 10, 4],
                        [10, 2, 10, 5],
                        [11, 3, 9, 0],
                        [12, 3, 11, 4],
                        [13, 6, 11, 3],
                        [14, 7, 11, 6],
                        [15, 4, 11, 7],
                    ]
                ),
                num.array(
                    [
                        [0, 4, 9, 3],
                        [1, 4, 12, 5],
                        [2, 7, 12, 4],
                        [4, 5, 12, 8],
                        [11, 3, 9, 0],
                        [12, 3, 11, 4],
                    ]
                ),
                num.array(
                    [
                        [0, 4, 9, 3],
                        [1, 4, 12, 5],
                        [2, 7, 12, 4],
                        [3, 8, 12, 7],
                        [5, 0, 9, 1],
                        [6, 1, 9, 4],
                    ]
                ),
            ],
            "ghost_boundary": [
                {
                    (13, 1): "ghost",
                    (8, 0): "ghost",
                    (14, 1): "ghost",
                    (11, 1): "ghost",
                    (10, 1): "ghost",
                    (5, 1): "ghost",
                    (10, 2): "ghost",
                },
                {
                    (12, 2): "ghost",
                    (12, 0): "ghost",
                    (2, 1): "ghost",
                    (11, 1): "ghost",
                    (2, 2): "ghost",
                    (4, 1): "ghost",
                    (4, 0): "ghost",
                },
                {
                    (3, 2): "ghost",
                    (6, 1): "ghost",
                    (3, 1): "ghost",
                    (5, 1): "ghost",
                    (1, 0): "ghost",
                    (1, 1): "ghost",
                },
            ],
            "full_triangles": [
                [[4, 9, 3], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]],
                [[0, 9, 1], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5]],
                [[3, 9, 0], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7]],
            ],
            "full_commun": [
                {0: [1, 2], 1: [1, 2], 2: [1, 2], 3: [2], 4: [1]},
                {5: [0, 2], 6: [0, 2], 7: [], 8: [0], 9: [0], 10: [0]},
                {11: [0, 1], 12: [0, 1], 13: [0], 14: [0], 15: [0]},
            ],
            "ghost_commun": [
                num.array(
                    [
                        [5, 1],
                        [6, 1],
                        [8, 1],
                        [9, 1],
                        [10, 1],
                        [11, 2],
                        [12, 2],
                        [13, 2],
                        [14, 2],
                        [15, 2],
                    ]
                ),
                num.array([[0, 0], [1, 0], [2, 0], [4, 0], [11, 2], [12, 2]]),
                num.array([[0, 0], [1, 0], [2, 0], [3, 0], [5, 1], [6, 1]]),
            ],
            "ghost_quan": {
                "stage": [
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.25, -0.375, -0.5],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                ],
                "elevation": [
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.25, -0.375, -0.5],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                ],
                "ymomentum": [
                    num.array(
                        [
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                            [0.0, 0.25, 0.0],
                            [0.5, 0.25, 0.0],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                        ]
                    ),
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                ],
                "friction": [
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                ],
                "xmomentum": [
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                ],
            },
            "full_quan": {
                "stage": [
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.0, -0.125, -0.0],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                ],
                "elevation": [
                    num.array(
                        [
                            [-0.25, -0.125, -0.25],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                    num.array(
                        [
                            [-0.0, -0.125, -0.0],
                            [-0.0, -0.125, -0.25],
                            [-0.0, -0.125, -0.0],
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.125, -0.25],
                            [-0.0, -0.125, -0.25],
                        ]
                    ),
                    num.array(
                        [
                            [-0.25, -0.125, -0.0],
                            [-0.25, -0.375, -0.25],
                            [-0.5, -0.375, -0.25],
                            [-0.5, -0.375, -0.5],
                            [-0.25, -0.375, -0.5],
                        ]
                    ),
                ],
                "ymomentum": [
                    num.array(
                        [
                            [0.5, 0.25, 0.0],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.25, 0.5],
                            [0.5, 0.25, 0.5],
                            [0.5, 0.75, 1.0],
                            [0.5, 0.75, 0.5],
                            [1.0, 0.75, 0.5],
                            [1.0, 0.75, 1.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.25, 0.0],
                            [0.0, 0.25, 0.5],
                            [0.0, 0.25, 0.0],
                            [0.5, 0.25, 0.0],
                            [0.5, 0.25, 0.5],
                        ]
                    ),
                ],
                "friction": [
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                    num.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ]
                    ),
                ],
                "xmomentum": [
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                    num.array(
                        [
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                            [2.0, 2.0, 2.0],
                        ]
                    ),
                ],
            },
        }

        # Subdivide into non-overlapping partitions
        submesh = build_submesh(
            nodes, triangles, boundary, quantities, triangles_per_proc, parameters=None
        )

        for i in range(3):
            assert num.allclose(
                true_submesh["full_triangles"][i], submesh["full_triangles"][i]
            )
            assert num.allclose(true_submesh["full_nodes"][i], submesh["full_nodes"][i])
            assert num.allclose(
                true_submesh["ghost_triangles"][i], submesh["ghost_triangles"][i]
            )
            assert num.allclose(
                true_submesh["ghost_nodes"][i], submesh["ghost_nodes"][i]
            )
            assert num.allclose(
                true_submesh["ghost_commun"][i], submesh["ghost_commun"][i]
            )

        assert true_submesh["full_boundary"] == submesh["full_boundary"]
        assert true_submesh["full_commun"] == submesh["full_commun"]

        for key, value in true_submesh["ghost_quan"].items():
            for i in range(3):
                assert num.allclose(
                    true_submesh["ghost_quan"][key][i], submesh["ghost_quan"][key][i]
                )
                assert num.allclose(
                    true_submesh["full_quan"][key][i], submesh["full_quan"][key][i]
                )

        # Now test the extract_submesh for the 3 processors

        submesh_cell_0 = extract_submesh(submesh, triangles_per_proc, p=0)
        submesh_cell_1 = extract_submesh(submesh, triangles_per_proc, p=1)
        submesh_cell_2 = extract_submesh(submesh, triangles_per_proc, p=2)

        from pprint import pprint

        # pprint(submesh_cell_1)


# -------------------------------------------------------------

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Test_Distribute_Mesh)
    runner = unittest.TextTestRunner()
    runner.run(suite)
