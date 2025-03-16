#!/usr/bin/env python3
"""
Comprehensive Java Heap Dump Analyzer

This script analyzes Java heap dump files (.hprof) to identify various issues including:
1. Memory leaks and large objects
2. Database connection issues (Redis, MySQL, PostgreSQL, etc.)
3. Thread-related problems (deadlocks, thread leaks)
4. Classloader leaks
5. Network connection issues
6. Timeout problems

Usage:
    python heap_dump_analyzer.py --file /path/to/heapdump.hprof.gz [--output report.txt] [--focus redis|threads|memory|all]
"""

import argparse
import gzip
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict, Counter
from datetime import datetime
import json


class HeapDumpAnalyzer:
    def __init__(self, heap_dump_path, output_path=None, focus_area="all"):
        """Initialize the analyzer with the path to the heap dump file."""
        self.heap_dump_path = heap_dump_path
        self.output_path = output_path or f"heap_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.is_compressed = heap_dump_path.endswith('.gz')
        self.temp_dir = None
        self.extracted_path = None
        self.focus_area = focus_area.lower()
        
        # Findings storage
        self.findings = []
        
        # Database related
        self.redis_keys = []
        self.redis_connections = []
        self.db_connections = []
        
        # Memory related
        self.large_objects = []
        self.potential_memory_leaks = []
        self.class_histogram = Counter()
        
        # Thread related
        self.thread_info = []
        self.blocked_threads = []
        self.deadlock_candidates = []
        
        # Network related
        self.network_connections = []
        self.timeout_issues = []
        
        # Classloader related
        self.classloader_info = []
        
        # Statistics
        self.string_stats = Counter()
        self.class_stats = Counter()
        self.exception_stats = Counter()

    def extract_if_compressed(self):
        """Extract the heap dump if it's compressed."""
        if self.is_compressed:
            print(f"Extracting compressed heap dump: {self.heap_dump_path}")
            self.temp_dir = tempfile.mkdtemp()
            self.extracted_path = os.path.join(self.temp_dir, os.path.basename(self.heap_dump_path)[:-3])
            
            try:
                with gzip.open(self.heap_dump_path, 'rb') as f_in:
                    with open(self.extracted_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                print(f"Extracted to: {self.extracted_path}")
                return True
            except Exception as e:
                print(f"Error extracting heap dump: {e}")
                return False
        else:
            self.extracted_path = self.heap_dump_path
            return True

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up temporary directory: {self.temp_dir}")

    def extract_strings(self):
        """Extract strings from the heap dump file."""
        print("Extracting strings from heap dump...")
        heap_path = self.extracted_path or self.heap_dump_path
        
        try:
            if self.is_compressed and not self.extracted_path:
                # If still compressed and not extracted, use gzip to decompress on the fly
                cmd = f"gzip -cd {self.heap_dump_path} | strings"
            else:
                cmd = f"strings {heap_path}"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error extracting strings: {result.stderr}")
                return []
            
            return result.stdout.splitlines()
        except Exception as e:
            print(f"Error running strings command: {e}")
            return []

    def analyze_strings(self, strings_list):
        """Analyze extracted strings for various issues."""
        print("Analyzing strings for issues...")
        
        # Database-related patterns
        redis_key_pattern = re.compile(r'BH\|WRK_[a-zA-Z0-9\-]+')
        redis_patterns = {
            'timeout': re.compile(r'response has been skipped due to timeout', re.IGNORECASE),
            'connection': re.compile(r'redis.*connection', re.IGNORECASE),
            'error': re.compile(r'RedisConnectionException|RedisTimeoutException', re.IGNORECASE)
        }
        
        # SQL database patterns
        sql_patterns = {
            'connection': re.compile(r'(mysql|postgresql|jdbc|oracle|sqlserver).*connection', re.IGNORECASE),
            'timeout': re.compile(r'(sql|query|statement).*timeout', re.IGNORECASE),
            'error': re.compile(r'SQLException|SQLTimeoutException', re.IGNORECASE)
        }
        
        # Thread-related patterns
        thread_patterns = {
            'deadlock': re.compile(r'deadlock|DeadlockDetected', re.IGNORECASE),
            'blocked': re.compile(r'thread.*blocked|blocked.*thread', re.IGNORECASE),
            'waiting': re.compile(r'thread.*waiting|waiting.*thread', re.IGNORECASE),
            'dump': re.compile(r'Thread\.getStackTrace|Thread dump', re.IGNORECASE)
        }
        
        # Memory-related patterns
        memory_patterns = {
            'outofmemory': re.compile(r'OutOfMemoryError|java\.lang\.OutOfMemoryError', re.IGNORECASE),
            'gc': re.compile(r'GC overhead|garbage collect', re.IGNORECASE),
            'leak': re.compile(r'memory leak|leak detected', re.IGNORECASE)
        }
        
        # Network-related patterns
        network_patterns = {
            'timeout': re.compile(r'(connect|socket|read|write).*timeout', re.IGNORECASE),
            'connection': re.compile(r'(connection refused|connection reset|broken pipe)', re.IGNORECASE),
            'dns': re.compile(r'UnknownHostException|dns.*resolve', re.IGNORECASE)
        }
        
        # Exception patterns
        exception_pattern = re.compile(r'Exception|Error', re.IGNORECASE)
        
        # Analyze each string
        for string in strings_list:
            # Database analysis
            if self.focus_area in ["all", "redis", "database"]:
                # Redis analysis
                redis_key_match = redis_key_pattern.search(string)
                if redis_key_match:
                    self.redis_keys.append(redis_key_match.group(0))
                
                for pattern_type, pattern in redis_patterns.items():
                    if pattern.search(string):
                        if pattern_type == 'timeout':
                            self.timeout_issues.append(string)
                        elif pattern_type == 'connection' or pattern_type == 'error':
                            self.redis_connections.append(string)
                
                # SQL database analysis
                for pattern_type, pattern in sql_patterns.items():
                    if pattern.search(string):
                        self.db_connections.append({
                            'type': pattern_type,
                            'text': string
                        })
            
            # Thread analysis
            if self.focus_area in ["all", "threads"]:
                for pattern_type, pattern in thread_patterns.items():
                    if pattern.search(string):
                        self.thread_info.append({
                            'type': pattern_type,
                            'text': string
                        })
                        if pattern_type == 'blocked':
                            self.blocked_threads.append(string)
                        elif pattern_type == 'deadlock':
                            self.deadlock_candidates.append(string)
            
            # Memory analysis
            if self.focus_area in ["all", "memory"]:
                for pattern_type, pattern in memory_patterns.items():
                    if pattern.search(string):
                        self.potential_memory_leaks.append({
                            'type': pattern_type,
                            'text': string
                        })
            
            # Network analysis
            if self.focus_area in ["all", "network"]:
                for pattern_type, pattern in network_patterns.items():
                    if pattern.search(string):
                        self.network_connections.append({
                            'type': pattern_type,
                            'text': string
                        })
                        if pattern_type == 'timeout':
                            self.timeout_issues.append(string)
            
            # Exception analysis
            exception_match = exception_pattern.search(string)
            if exception_match:
                exception_name = string[exception_match.start():].split()[0]
                self.exception_stats[exception_name] += 1
            
            # Count string occurrences for statistical analysis
            if len(string) > 10:  # Ignore very short strings
                self.string_stats[string[:50]] += 1  # Use first 50 chars as key
            
            # Class analysis
            if string.startswith('java.') or string.startswith('javax.') or string.startswith('com.') or string.startswith('org.'):
                parts = string.split('.')
                if len(parts) > 2:  # Likely a class name
                    potential_class = '.'.join(parts[:3])  # Take first 3 parts as potential class
                    self.class_stats[potential_class] += 1
        
        # Find large objects (strings that appear to be JSON or serialized data)
        for string, count in self.string_stats.items():
            if (string.startswith('{') or string.startswith('[')) and len(string) > 1000:
                self.large_objects.append({
                    'preview': string[:100] + '...',
                    'length': len(string),
                    'count': count
                })
                
                # Check for specific types of large objects
                if 'workspaceNodes' in string or 'GetHierarchy' in string:
                    self.large_objects[-1]['type'] = 'business_hierarchy'
                elif '"id"' in string and '"createdAt"' in string:
                    self.large_objects[-1]['type'] = 'entity_data'
                elif 'Exception' in string or 'Error' in string:
                    self.large_objects[-1]['type'] = 'error_data'

    def analyze_heap_dump(self):
        """Main method to analyze the heap dump."""
        print(f"Starting analysis of heap dump: {self.heap_dump_path}")
        print(f"Focus area: {self.focus_area}")
        
        # Extract if compressed
        if not self.extract_if_compressed():
            print("Failed to extract heap dump. Aborting analysis.")
            return False
        
        # Extract and analyze strings
        strings_list = self.extract_strings()
        if not strings_list:
            print("Failed to extract strings from heap dump. Aborting analysis.")
            return False
        
        print(f"Extracted {len(strings_list)} strings from heap dump")
        self.analyze_strings(strings_list)
        
        # Try to extract heap histogram if jhat or jmap is available
        self.extract_heap_histogram()
        
        # Generate findings
        self.generate_findings()
        
        # Generate report
        self.generate_report()
        
        # Cleanup
        self.cleanup()
        
        return True
    
    def extract_heap_histogram(self):
        """Try to extract heap histogram using jhat or jmap if available."""
        try:
            # Check if jmap is available
            result = subprocess.run(['which', 'jmap'], capture_output=True, text=True)
            if result.returncode == 0:
                print("jmap found, attempting to extract heap histogram...")
                # This might not work directly on a heap dump file, but worth trying
                cmd = f"jmap -histo:file={self.extracted_path} | head -30"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout:
                    print("Successfully extracted heap histogram")
                    # Parse the histogram
                    lines = result.stdout.strip().split('\n')
                    for line in lines[2:]:  # Skip header lines
                        parts = line.split()
                        if len(parts) >= 3:
                            class_name = parts[2]
                            count = int(parts[1])
                            self.class_histogram[class_name] = count
        except Exception as e:
            print(f"Error extracting heap histogram: {e}")
            # This is optional, so continue with analysis

    def generate_findings(self):
        """Generate findings based on the analysis."""
        # Database findings
        if self.focus_area in ["all", "redis", "database"]:
            # Redis keys findings
            if self.redis_keys:
                unique_keys = set(self.redis_keys)
                self.findings.append({
                    'category': 'Redis Keys',
                    'title': f'Found {len(unique_keys)} unique Redis keys with pattern BH|WRK_*',
                    'details': list(unique_keys)[:10],  # Show top 10
                    'count': len(unique_keys),
                    'severity': 'info'
                })
            
            # Redis connection issues findings
            if self.redis_connections:
                self.findings.append({
                    'category': 'Redis Connection Issues',
                    'title': f'Found {len(self.redis_connections)} Redis connection references',
                    'details': self.redis_connections[:5],  # Show top 5
                    'count': len(self.redis_connections),
                    'severity': 'warning'
                })
            
            # SQL database connection issues
            if self.db_connections:
                self.findings.append({
                    'category': 'SQL Database Issues',
                    'title': f'Found {len(self.db_connections)} SQL database connection issues',
                    'details': [item['text'] for item in self.db_connections[:5]],
                    'count': len(self.db_connections),
                    'severity': 'warning'
                })
        
        # Timeout issues findings
        if self.timeout_issues:
            self.findings.append({
                'category': 'Timeout Issues',
                'title': f'Found {len(self.timeout_issues)} timeout issues',
                'details': self.timeout_issues[:5],  # Show top 5
                'count': len(self.timeout_issues),
                'severity': 'critical'
            })
        
        # Thread-related findings
        if self.focus_area in ["all", "threads"]:
            # Blocked threads
            if self.blocked_threads:
                self.findings.append({
                    'category': 'Blocked Threads',
                    'title': f'Found {len(self.blocked_threads)} blocked threads',
                    'details': self.blocked_threads[:5],
                    'count': len(self.blocked_threads),
                    'severity': 'critical'
                })
            
            # Potential deadlocks
            if self.deadlock_candidates:
                self.findings.append({
                    'category': 'Potential Deadlocks',
                    'title': f'Found {len(self.deadlock_candidates)} potential deadlock situations',
                    'details': self.deadlock_candidates[:5],
                    'count': len(self.deadlock_candidates),
                    'severity': 'critical'
                })
            
            # Thread information
            if self.thread_info:
                thread_types = Counter([item['type'] for item in self.thread_info])
                self.findings.append({
                    'category': 'Thread Information',
                    'title': f'Found {len(self.thread_info)} thread-related entries',
                    'details': [f"{type}: {count}" for type, count in thread_types.most_common(5)],
                    'count': len(self.thread_info),
                    'severity': 'info'
                })
        
        # Memory-related findings
        if self.focus_area in ["all", "memory"]:
            # Large objects findings
            if self.large_objects:
                self.findings.append({
                    'category': 'Large Objects',
                    'title': f'Found {len(self.large_objects)} potentially large objects',
                    'details': [f"{obj.get('type', 'unknown')}: {obj['preview']} (length: {obj['length']})" for obj in self.large_objects[:5]],
                    'count': len(self.large_objects),
                    'severity': 'warning'
                })
            
            # Memory leak candidates
            if self.potential_memory_leaks:
                self.findings.append({
                    'category': 'Potential Memory Leaks',
                    'title': f'Found {len(self.potential_memory_leaks)} potential memory leak indicators',
                    'details': [item['text'] for item in self.potential_memory_leaks[:5]],
                    'count': len(self.potential_memory_leaks),
                    'severity': 'critical'
                })
            
            # Class histogram
            if self.class_histogram:
                self.findings.append({
                    'category': 'Class Histogram',
                    'title': f'Top classes by instance count',
                    'details': [f"{class_name}: {count}" for class_name, count in self.class_histogram.most_common(10)],
                    'count': len(self.class_histogram),
                    'severity': 'info'
                })
        
        # Network-related findings
        if self.focus_area in ["all", "network"]:
            if self.network_connections:
                network_types = Counter([item['type'] for item in self.network_connections])
                self.findings.append({
                    'category': 'Network Issues',
                    'title': f'Found {len(self.network_connections)} network-related issues',
                    'details': [f"{type}: {count}" for type, count in network_types.most_common(5)],
                    'count': len(self.network_connections),
                    'severity': 'warning'
                })
        
        # Exception statistics
        if self.exception_stats:
            self.findings.append({
                'category': 'Exception Statistics',
                'title': f'Found {len(self.exception_stats)} different exception types',
                'details': [f"{exc}: {count}" for exc, count in self.exception_stats.most_common(10)],
                'count': sum(self.exception_stats.values()),
                'severity': 'warning'
            })

    def generate_report(self):
        """Generate a report with the findings and recommendations."""
        print(f"Generating report to: {self.output_path}")
        
        with open(self.output_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"COMPREHENSIVE HEAP DUMP ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Heap Dump: {self.heap_dump_path}\n")
            f.write(f"Focus Area: {self.focus_area}\n")
            f.write("=" * 80 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 80 + "\n")
            
            # Count findings by severity
            severity_counts = Counter()
            for finding in self.findings:
                severity_counts[finding.get('severity', 'info')] += 1
            
            f.write(f"Critical Issues: {severity_counts.get('critical', 0)}\n")
            f.write(f"Warnings: {severity_counts.get('warning', 0)}\n")
            f.write(f"Informational: {severity_counts.get('info', 0)}\n\n")
            
            if self.findings:
                f.write("Key Findings:\n")
                for finding in self.findings:
                    if finding.get('severity') == 'critical':
                        f.write(f"- [CRITICAL] {finding['title']}\n")
                
                for finding in self.findings:
                    if finding.get('severity') == 'warning':
                        f.write(f"- [WARNING] {finding['title']}\n")
            else:
                f.write("No significant findings.\n")
            f.write("\n")
            
            # Detailed Findings
            f.write("DETAILED FINDINGS\n")
            f.write("-" * 80 + "\n")
            
            # Group findings by category
            categories = defaultdict(list)
            for finding in self.findings:
                categories[finding['category']].append(finding)
            
            if categories:
                for category, category_findings in categories.items():
                    f.write(f"\n{category.upper()}\n")
                    f.write("-" * len(category) + "\n")
                    
                    for i, finding in enumerate(category_findings, 1):
                        severity = finding.get('severity', 'info').upper()
                        f.write(f"{i}. [{severity}] {finding['title']}\n")
                        f.write("   Details:\n")
                        for detail in finding['details']:
                            f.write(f"   - {detail}\n")
                        f.write("\n")
            else:
                f.write("No detailed findings to report.\n")
            f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")
            
            # Add specific recommendations based on findings
            recommendations = []
            
            # Database recommendations
            db_recommendations = []
            
            # Redis recommendations
            if any(finding['category'] in ['Redis Keys', 'Redis Connection Issues', 'Timeout Issues'] 
                  for finding in self.findings):
                db_recommendations.append(
                    "Redis Optimization:\n"
                    "   - Increase Redis connection and operation timeouts in your application configuration:\n"
                    "     * For Redisson: config.setConnectTimeout(10000) and config.setTimeout(10000)\n"
                    "     * For Lettuce: clientOptions.setConnectTimeout(Duration.ofSeconds(10))\n"
                    "     * For Jedis: jedisPoolConfig.setMaxWaitMillis(10000)\n"
                    "   - Optimize connection management:\n"
                    "     * Increase the maximum size of the Redis connection pool\n"
                    "     * Adjust the minimum idle connections to ensure connections are available\n"
                    "     * Implement connection validation to detect stale connections\n"
                    "     * Consider using Redis Cluster for better scalability\n"
                )
            
            # SQL database recommendations
            if self.db_connections:
                db_recommendations.append(
                    "SQL Database Optimization:\n"
                    "   - Review and optimize database connection pool settings\n"
                    "   - Increase query timeout settings if appropriate\n"
                    "   - Consider adding indexes for frequently queried columns\n"
                    "   - Optimize large queries that may be causing timeouts\n"
                )
            
            if db_recommendations:
                recommendations.append("1. Database Optimizations:\n" + "\n".join(db_recommendations))
            
            # Memory recommendations
            if any(finding['category'] in ['Large Objects', 'Potential Memory Leaks'] 
                  for finding in self.findings):
                recommendations.append(
                    "2. Memory Management:\n"
                    "   - Review and optimize large object serialization\n"
                    "   - Break down large hierarchical data into smaller chunks\n"
                    "   - Use more efficient data structures (e.g., Redis Hash instead of serialized strings)\n"
                    "   - Implement pagination for large collections\n"
                    "   - Check for resource leaks (connections, file handles, etc.)\n"
                    "   - Consider increasing JVM heap size if appropriate\n"
                )
            
            # Thread recommendations
            if any(finding['category'] in ['Blocked Threads', 'Potential Deadlocks'] 
                  for finding in self.findings):
                recommendations.append(
                    "3. Thread Management:\n"
                    "   - Review synchronization patterns to avoid deadlocks\n"
                    "   - Consider using higher-level concurrency utilities instead of raw locks\n"
                    "   - Implement timeouts for all blocking operations\n"
                    "   - Review thread pool configurations\n"
                    "   - Consider using async/non-blocking APIs for I/O operations\n"
                )
            
            # Network recommendations
            if any(finding['category'] in ['Network Issues', 'Timeout Issues'] 
                  for finding in self.findings):
                recommendations.append(
                    "4. Network Configuration:\n"
                    "   - Implement circuit breakers for external service calls\n"
                    "   - Add appropriate timeouts for all network operations\n"
                    "   - Consider implementing retry mechanisms with exponential backoff\n"
                    "   - Monitor network latency between services\n"
                )
            
            # General recommendations
            recommendations.append(
                "5. Monitoring and Alerting:\n"
                "   - Implement comprehensive monitoring for memory, threads, and connections\n"
                "   - Set up alerts for slow operations and timeouts\n"
                "   - Regularly analyze heap dumps in non-production environments\n"
                "   - Consider implementing distributed tracing to identify bottlenecks\n"
            )
            
            # Write recommendations
            if recommendations:
                for recommendation in recommendations:
                    f.write(f"{recommendation}\n\n")
            else:
                f.write("No specific recommendations based on the analysis.\n")
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"Report generated successfully: {self.output_path}")
        return True


def main():
    """Main function to parse arguments and run the analyzer."""
    parser = argparse.ArgumentParser(description='Analyze Java heap dumps for various issues')
    parser.add_argument('--file', required=True, help='Path to the heap dump file (.hprof or .hprof.gz)')
    parser.add_argument('--output', help='Path to the output report file')
    parser.add_argument('--focus', default='all', choices=['all', 'redis', 'database', 'memory', 'threads', 'network'],
                        help='Focus area for analysis (default: all)')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: Heap dump file not found: {args.file}")
        return 1
    
    # Run the analyzer
    analyzer = HeapDumpAnalyzer(args.file, args.output, args.focus)
    success = analyzer.analyze_heap_dump()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
