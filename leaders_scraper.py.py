import os

if "VIRTUAL_ENV" in os.environ:
    print("Running in a virtual environment")
else:
    print("Not running in a virtual environment")

