import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.abspath(os.path.join(cur_dir, '.'))
if root not in sys.path:
    sys.path.append(root)

from main_v2 import run

if __name__ == '__main__':
    run()