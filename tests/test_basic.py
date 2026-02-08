import sys
import os
# Force the root directory into the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ta  # Now try the import
def test_version():
    # This just checks that the library can be imported
    assert ta is not None