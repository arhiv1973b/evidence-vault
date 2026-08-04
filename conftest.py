"""Pytest configuration for antigravity-sdk-python tests.

This module ensures that absl flags are properly initialized before tests run.
This is necessary for tests that use absltest.TestCase, which relies on flags
like --test_tmpdir being parsed before setUp() is called.
"""

import tempfile
from absl import flags


def pytest_configure(config):
  """Initialize absl flags before test collection.
  
  This pytest hook runs before test collection and ensures that absl's
  flag parser has been initialized. This allows tests using absltest.TestCase
  (which calls create_tempdir() and reads --test_tmpdir flag) to work correctly
  with pytest.
  
  Args:
    config: pytest config object
  """
  # Import absltest to ensure test_tmpdir flag is defined
  from absl.testing import absltest  # pylint: disable=unused-import
  
  # Mark flags as parsed so that absltest can access them
  flags.FLAGS.mark_as_parsed()
  
  # Set a default test_tmpdir if not provided by command line
  if not flags.FLAGS.test_tmpdir:
    flags.FLAGS.test_tmpdir = tempfile.gettempdir()
