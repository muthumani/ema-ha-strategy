# Getting Started

This guide will help you get started with the EMA Heikin Ashi Strategy.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ema-ha-strategy.git
cd ema-ha-strategy

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ema-ha-strategy.git
cd ema-ha-strategy

# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

## Basic Usage

### Running the Strategy

```bash
python main.py --config config/config.yaml --symbol NIFTY
```

This will run the strategy with the default configuration.

### Viewing Results

Results will be saved in the `data/results` directory. You can view the results in the following formats:

- JSON file with performance metrics
- CSV file with individual trades
- Excel report (if `--report` option is used)

### Generating Excel Report

```bash
python main.py --report
```

This will generate a comprehensive Excel report with detailed analysis.

## Next Steps

- [Configuration](configuration.md): Learn how to configure the strategy
- [Running the Strategy](running.md): Learn more about running the strategy
- [Interpreting Results](results.md): Learn how to interpret the results
- [Excel Reports](excel_reports.md): Learn how to generate and interpret Excel reports
