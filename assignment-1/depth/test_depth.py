#!/usr/bin/env python3
# Public tests for CPSC459/559 Assignment 2 - Part VI

import sys
import unittest
import numpy as np
from process_images import compute_depth_from_gray_image, compute_depth_from_depth_image

class TestDepth(unittest.TestCase):
    """
    Public tests for process_images.py
    """

    def __init__(self, *args):
        """
        Constructor
        """
        super(TestDepth, self).__init__(*args)

        self.object_height = 0.245
        self.image_coordinates = [[0, 0], [80, 60]]
        
    def test_gray_depth(self):
        """
        Check calculation of depth from grayscale image
        """
        gray = np.full((480, 640), 181, dtype=np.uint8)
        K = np.array([612.65332031,   0., 311.68063354,   0., 612.71502686, 247.28131104,   0.,   0., 1.])
        K = np.reshape(K, (3, 3))
        
        gray_depth = compute_depth_from_gray_image(gray, self.image_coordinates, K, self.object_height)
        self.assertIsInstance(gray_depth, float,
                              "The compute_depth_from_gray_image() function is not returning a float value. Output: {}"
                              .format(gray_depth))
        self.assertTrue(np.isfinite(gray_depth),
                        "The output of compute_depth_from_gray_image() is not finite. Output: {}"
                        .format(gray_depth))

        print("Verified that 'compute_depth_from_gray_image' returns a finite float")

    def test_depth_image(self):
        """
        Check calculation of depth from depth image
        """
        depth = np.full((480, 640), 0.853, dtype='float64')

        # Zero out part of the selected region. These cells stand for pixels of the gray
        # image for which the camera could not estimate depth, so they must be filtered
        # out before averaging (see task VI-3.ii). Every remaining cell of the region
        # holds the same value, so a correct implementation must return exactly that value.
        depth[0:30, 0:40] = 0.0

        avg_depth = compute_depth_from_depth_image(depth, self.image_coordinates)
        self.assertIsInstance(avg_depth, float,
                              "The compute_depth_from_depth_image() function is not returning a float value. Output: {}"
                              .format(avg_depth))
        self.assertTrue(np.isfinite(avg_depth),
                        "The output of the compute_depth_from_depth_image() function is not finite. Output: {}. "
                        "Note that averaging an empty set of depth values results in nan."
                        .format(avg_depth))
        self.assertAlmostEqual(avg_depth, 0.853, places=6,
                               msg="The output of the compute_depth_from_depth_image() function is not the average "
                                   "of the non-zero depth values in the selected region. Expected: 0.853. Output: {}. "
                                   "Remember to filter out the zero values of the depth image before averaging."
                                   .format(avg_depth))

        print("Verified that 'compute_depth_from_depth_image' returns a finite float and filters out zero values")
