#!/usr/bin/env python3
import os
import sys
import unittest

if __name__ == '__main__':
    if not os.path.exists('tests'):
        os.makedirs('tests')
    
    if not os.path.exists('db'):
        os.makedirs('db')
    
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    sys.exit(not result.wasSuccessful())
