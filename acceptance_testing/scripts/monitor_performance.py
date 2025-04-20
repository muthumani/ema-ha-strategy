#!/usr/bin/env python
"""
Performance monitoring script for EMA-HA Strategy.
This script monitors CPU, memory, and disk usage during test execution.
"""

import os
import sys
import time
import psutil
import argparse
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Monitor system performance during test execution')
    parser.add_argument('command', help='Command to execute and monitor')
    parser.add_argument('--interval', type=float, default=1.0, help='Sampling interval in seconds')
    parser.add_argument('--output', default='performance_report.html', help='Output report file')
    return parser.parse_args()

def monitor_performance(command, interval=1.0):
    """Monitor system performance while executing a command"""
    # Start the process
    process = subprocess.Popen(command, shell=True)
    
    # Initialize data collection
    timestamps = []
    cpu_usage = []
    memory_usage = []
    disk_io = []
    
    # Monitor until process completes
    start_time = time.time()
    try:
        while process.poll() is None:
            # Record timestamp
            timestamps.append(time.time() - start_time)
            
            # Record CPU usage
            cpu_usage.append(psutil.cpu_percent(interval=None))
            
            # Record memory usage (MB)
            memory_info = psutil.Process(process.pid).memory_info()
            memory_usage.append(memory_info.rss / (1024 * 1024))
            
            # Record disk I/O
            disk_io.append(sum(psutil.disk_io_counters()[:2]))
            
            # Wait for next sample
            time.sleep(interval)
    except Exception as e:
        print(f"Error monitoring performance: {e}")
    finally:
        # Ensure process is terminated
        if process.poll() is None:
            process.terminate()
            process.wait()
    
    # Return collected data
    return {
        'exit_code': process.returncode,
        'timestamps': timestamps,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_io': disk_io,
        'duration': timestamps[-1] if timestamps else 0,
        'peak_cpu': max(cpu_usage) if cpu_usage else 0,
        'peak_memory': max(memory_usage) if memory_usage else 0,
    }

def generate_report(data, output_file):
    """Generate an HTML performance report"""
    # Create plots
    plt.figure(figsize=(12, 8))
    
    # CPU usage plot
    plt.subplot(2, 1, 1)
    plt.plot(data['timestamps'], data['cpu_usage'])
    plt.title('CPU Usage')
    plt.xlabel('Time (seconds)')
    plt.ylabel('CPU Usage (%)')
    plt.grid(True)
    
    # Memory usage plot
    plt.subplot(2, 1, 2)
    plt.plot(data['timestamps'], data['memory_usage'])
    plt.title('Memory Usage')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Memory Usage (MB)')
    plt.grid(True)
    
    # Save plot
    plot_file = os.path.splitext(output_file)[0] + '.png'
    plt.tight_layout()
    plt.savefig(plot_file)
    
    # Create HTML report
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Performance Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .plot {{ text-align: center; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Performance Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Duration:</strong> {data['duration']:.2f} seconds</p>
                <p><strong>Exit Code:</strong> {data['exit_code']}</p>
                <p><strong>Peak CPU Usage:</strong> {data['peak_cpu']:.2f}%</p>
                <p><strong>Peak Memory Usage:</strong> {data['peak_memory']:.2f} MB</p>
            </div>
            
            <div class="plot">
                <h2>Performance Plots</h2>
                <img src="{os.path.basename(plot_file)}" alt="Performance Plots" style="max-width: 100%;">
            </div>
            
            <h2>Detailed Metrics</h2>
            <table>
                <tr>
                    <th>Time (s)</th>
                    <th>CPU Usage (%)</th>
                    <th>Memory Usage (MB)</th>
                </tr>
    """
    
    # Add data rows
    for i in range(len(data['timestamps'])):
        html += f"""
                <tr>
                    <td>{data['timestamps'][i]:.2f}</td>
                    <td>{data['cpu_usage'][i]:.2f}</td>
                    <td>{data['memory_usage'][i]:.2f}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
    </body>
    </html>
    """
    
    # Write HTML report
    with open(output_file, 'w') as f:
        f.write(html)
    
    return output_file, plot_file

def main():
    """Main entry point"""
    args = parse_arguments()
    
    print(f"Monitoring performance while executing: {args.command}")
    print(f"Sampling interval: {args.interval} seconds")
    
    # Monitor performance
    data = monitor_performance(args.command, args.interval)
    
    # Generate report
    report_file, plot_file = generate_report(data, args.output)
    
    print(f"\nPerformance Summary:")
    print(f"Duration: {data['duration']:.2f} seconds")
    print(f"Exit Code: {data['exit_code']}")
    print(f"Peak CPU Usage: {data['peak_cpu']:.2f}%")
    print(f"Peak Memory Usage: {data['peak_memory']:.2f} MB")
    print(f"\nReport generated: {report_file}")
    print(f"Plot generated: {plot_file}")
    
    return data['exit_code']

if __name__ == "__main__":
    sys.exit(main())
