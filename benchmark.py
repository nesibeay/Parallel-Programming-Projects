import subprocess 
import matplotlib.pyplot as plt 
import csv 
 
data_sizes = [1000000, 5000000, 10000000] 
thread_counts = [1, 2, 4, 8, 16, 32] 
schedulers = ["static", "dynamic", "guided"] 
 
results = {s: {} for s in schedulers} 
 
for schedule in schedulers: 
    for size in data_sizes: 
        times = [] 
        for threads in thread_counts: 
            print(f"Running: schedule={schedule}, size={size}, threads={threads}") 
            result = subprocess.run( 
                ["./histogram", str(size), str(threads), schedule], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True 
            ) 
            if result.returncode != 0: 
                print(f"Error: {result.stderr}") 
                continue 
 
            for line in result.stdout.splitlines(): 
                if "Time" in line: 
                    time = float(line.strip().split()[-2]) 
                    times.append((threads, time)) 
                    break 
        results[schedule][size] = sorted(times) 
 
# Save to CSV 
with open("benchmark_results.csv", "w", newline="") as f: 
    writer = csv.writer(f) 
    writer.writerow(["Schedule", "Data Size", "Thread Count", "Time (s)", "Speedup", 
"Efficiency"]) 
    for schedule in schedulers: 
        for size, times in results[schedule].items(): 
            baseline_time = times[0][1] 
            for threads, time in times: 
                speedup = baseline_time / time 
                efficiency = speedup / threads 
                writer.writerow([schedule, size, threads, round(time, 6), round(speedup, 2), 
round(efficiency, 2)]) 
 
# Generate one set of plots per scheduler 
def plot_one_metric(metric_name, y_fn, ylabel, suffix): 
    for schedule in schedulers: 
        plt.figure(figsize=(10, 6)) 
        for size, times in results[schedule].items(): 
            x = [t[0] for t in times] 
            y = [y_fn(times[0][1], t[0], t[1]) for t in times] 
            plt.plot(x, y, marker='o', label=f"{size//1_000_000}M") 
        plt.title(f"{metric_name} vs Threads ({schedule.capitalize()})") 
        plt.xlabel("Thread Count") 
        plt.ylabel(ylabel) 
        plt.legend() 
        plt.grid(True) 
        plt.tight_layout() 
        filename = f"{suffix}_{schedule}.png" 
        plt.savefig(filename) 
        plt.close() 
        print(f"Saved: {filename}") 
 
# Metric-specific functions 
plot_one_metric("Runtime", lambda _, __, time: time, "Time (seconds)", "runtime") 
plot_one_metric("Speedup", lambda base, __, time: base / time, "Speedup", "speedup") 
plot_one_metric("Efficiency", lambda base, threads, time: (base / time) / threads, "Efficiency", 
"efficiency") 
 
# LaTeX Table Output 
with open("benchmark_table.tex", "w") as f: 
    f.write("\\begin{table}[h]\n\\centering\n") 
    f.write("\\begin{tabular}{|c|c|c|c|c|c|}\n\\hline\n") 
    f.write("Schedule & Data Size & Threads & Time (s) & Speedup & Efficiency \\\\\n\\hline\n") 
    for schedule in schedulers: 
        for size, times in results[schedule].items(): 
            baseline_time = times[0][1] 
            for threads, time in times: 
                speedup = baseline_time / time 
                efficiency = speedup / threads 
                f.write(f"{schedule} & {size} & {threads} & {time:.3f} & {speedup:.2f} & 
{efficiency:.2f} \\\\\n") 
    f.write("\\hline\n\\end{tabular}\n") 
    f.write("\\caption{Benchmark Results by Scheduling Strategy}\n") 
    f.write("\\label{tab:omp_scheduling_comparison}\n\\end{table}\n")