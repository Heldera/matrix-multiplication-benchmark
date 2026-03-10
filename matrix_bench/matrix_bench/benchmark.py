import os
import time
import tracemalloc
import numpy as np
from glob import glob

class Benchmarker:
    def __init__(self, runs=5):
        self.runs = runs
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.test_files = glob(os.path.join(self.data_dir, '*.npz'))
        
        if not self.test_files:
            raise FileNotFoundError("No matrix data found. Was the wheel built correctly?")

    def run_benchmark(self, func, method_name, comment):
        """Runs the passed function against all pre-generated matrices."""
        results = []
        
        for file_path in self.test_files:
            test_name = os.path.basename(file_path).replace('.npz', '')
            
            # Load matrix data
            data = np.load(file_path, allow_pickle=True)
            A, B = data['A'], data['B']
            config = data['config'].item()
            
            # 1. Warm-up run (compiles JIT if using numba, populates cache)
            _ = func(A, B)
            
            # 2. Measure Memory (Peak)
            tracemalloc.start()
            _ = func(A, B)
            _, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            peak_mem_mb = peak_mem / (1024 * 1024)
            
            # 3. Measure Execution Time
            times = []
            for _ in range(self.runs):
                start_time = time.perf_counter()
                _ = func(A, B)
                times.append(time.perf_counter() - start_time)
                
            best_time = min(times)
            avg_time = sum(times) / self.runs
            
            results.append({
                "Method": method_name,
                "Comment": comment,
                "Test Type": test_name,
                "Dimensions": f"{config['size'][0]}x{config['size'][1]}",
                "Density": config['density'],
                "Best Time (s)": best_time,
                "Avg Time (s)": avg_time,
                "Peak Memory (MB)": peak_mem_mb
            })
            
        return results