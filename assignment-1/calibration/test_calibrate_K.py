#!/usr/bin/env python3
# Public tests for CPSC-5590 Assignment 1 - Part V

import unittest
import numpy as np

from calibrate_K import compute_K

class TestCalibrateK(unittest.TestCase):
    """
    Public tests for calibrate_K.py
    """

    def __init__(self, *args):
        """
        Constructor
        """
        super(TestCalibrateK, self).__init__(*args)

        self.input_file = "correspondences.txt"

    def test_compute_K(self):
        """
        Check calculation of K
        """
        K, error = compute_K(self.input_file)

        self.assertIsInstance(K, np.ndarray,
                              "The compute_K() function is not returning K as a numpy array. Output: {}"
                              .format(K))
        print('K: {}'.format(K.shape))
        self.assertTrue(K.shape == (3,3),
                        "Shape of K is not (3,3). Output shape: {}".format(K.shape))

        self.assertIsInstance(error, float,
                              "The compute_K() function is not returning the error as a float value. Output: {}"
                              .format(error))
        self.assertTrue(np.isfinite(error),
                        "The error returned by compute_K() is not finite. Output: {}".format(error))
        self.assertGreaterEqual(error, 0.0,
                                "The error returned by compute_K() is negative, but it should be a sum of squared "
                                "norms. Output: {}".format(error))

        print("Verified that 'compute_K' returns a 3x3 numpy array and a finite, non-negative error")
