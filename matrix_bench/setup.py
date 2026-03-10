import os
import numpy as np
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

# Helper to read requirements
with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

def generate_matrices(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Example suite: Small (100x100), Big (2000x2000), Sparse (1000x1000, 1% density)
    configs = {
        "small_dense": {"size": (100, 100), "density": 1.0},
        "big_dense": {"size": (2000, 2000), "density": 1.0},
        "large_sparse": {"size": (1000, 1000), "density": 0.01}
    }
    
    for name, config in configs.items():
        rows, cols = config["size"]
        # Generate and save (Senior Tip: Use float32 to save space in the wheel)
        A = np.random.rand(rows, cols).astype(np.float32)
        B = np.random.rand(rows, cols).astype(np.float32)
        
        if config["density"] < 1.0:
            mask_a = np.random.random((rows, cols)) < config["density"]
            mask_b = np.random.random((rows, cols)) < config["density"]
            A *= mask_a
            B *= mask_b
            
        file_path = os.path.join(data_dir, f"{name}.npz")
        np.savez_compressed(file_path, A=A, B=B, config=config)

class CustomBuild(build_py):
    def run(self):
        # Build-time generation logic
        package_dir = os.path.join(self.build_lib, 'matrix_bench', 'data')
        generate_matrices(package_dir)
        super().run()

setup(
    name="matrix_bench",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires, # Read from requirements.txt
    cmdclass={'build_py': CustomBuild},
)