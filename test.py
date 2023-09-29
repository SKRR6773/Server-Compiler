import os
import shutil


__DIR__ = os.path.dirname(__file__)

# print(os.path.exists(os.path.join(__DIR__, "output")))


shutil.rmtree(os.path.join(__DIR__, "copy"))