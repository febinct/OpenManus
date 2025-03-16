# Comprehensive Java Heap Dump Analyzer

This tool analyzes Java heap dump files (.hprof) to identify various issues including memory leaks, database connection problems, thread-related issues, and more.

## Features

- **Memory Analysis**: Identifies large objects and potential memory leaks
- **Database Connection Analysis**: Detects Redis and SQL database connection issues
- **Thread Analysis**: Identifies blocked threads and potential deadlocks
- **Network Analysis**: Detects network connection and timeout issues
- **Exception Analysis**: Provides statistics on exceptions found in the heap dump
- **Comprehensive Reporting**: Generates detailed reports with findings and recommendations

## Requirements

- Python 3.6+
- `strings` command-line utility (available by default on most Unix-like systems)
- Optional: `jmap` for additional heap histogram analysis

## Installation

No special installation is required. Simply download the script and ensure you have Python 3.6+ installed.

## Usage

```bash
python heap_dump_analyzer.py --file /path/to/heapdump.hprof.gz [--output report.txt] [--focus redis|threads|memory|all]
```

### Parameters

- `--file`: Path to the heap dump file (.hprof or .hprof.gz)
- `--output`: (Optional) Path to the output report file. If not specified, a default name will be generated.
- `--focus`: (Optional) Focus area for analysis. Options: all, redis, database, memory, threads, network. Default: all

### Examples

Analyze a heap dump with default settings:
```bash
python heap_dump_analyzer.py --file /Users/username/Downloads/heapdump.hprof.gz
```

Focus on Redis-related issues:
```bash
python heap_dump_analyzer.py --file /Users/username/Downloads/heapdump.hprof.gz --focus redis
```

Specify an output file:
```bash
python heap_dump_analyzer.py --file /Users/username/Downloads/heapdump.hprof.gz --output redis_analysis.txt
```

## Understanding the Report

The generated report includes:

1. **Executive Summary**: Overview of critical issues, warnings, and informational findings
2. **Detailed Findings**: Categorized list of all findings with details
3. **Recommendations**: Specific recommendations based on the findings

## Example: Analyzing Redis Timeout Issues

If you're experiencing Redis timeout issues, use:

```bash
python heap_dump_analyzer.py --file /path/to/heapdump.hprof.gz --focus redis
```

The analyzer will:
1. Search for Redis connection patterns
2. Identify timeout-related strings
3. Find large Redis keys (like BH|WRK_* pattern)
4. Provide recommendations for optimizing Redis configuration

## Troubleshooting

- **Error extracting heap dump**: Ensure you have sufficient disk space and permissions
- **No findings reported**: Try using the `--focus` parameter to narrow the analysis
- **jmap errors**: jmap is optional; the analyzer will continue without it

## Extending the Analyzer

The analyzer is designed to be extensible. To add new patterns for detection:

1. Add new pattern dictionaries in the `analyze_strings` method
2. Add corresponding data structures to store findings
3. Update the `generate_findings` method to include your new findings
4. Add appropriate recommendations in the `generate_report` method
