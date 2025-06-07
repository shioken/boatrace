# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Japanese boat racing (競艇/kyotei) prediction and betting analysis system. The system collects race data, trains machine learning models, and generates betting recommendations.

## Architecture

The system follows a data pipeline: **Data Collection** → **Processing** → **Training** → **Prediction** → **Betting Analysis**

### Key Directories
- `b_lzh/`: Compressed race schedule files (daily)
- `csv/`: Processed CSV data for ML training
- `model/`: Trained ML models (LightGBM)
- `predicted/`: Prediction outputs
- `votes/`: Betting recommendations
- `odds/`: Betting odds data

### Data Flow
1. ~~`scrap_race.py` downloads race data from `http://www1.mbrace.or.jp/od2/`~~ (Service terminated 2025/03/05)
2. `parse_race.py` converts raw data to JSON format
3. `convert_csv.py` transforms JSON to CSV for ML training
4. `train_lambdarank.py` trains LambdaRank model using LightGBM
5. `predict.py` generates predictions
6. `make_votes.py` creates betting recommendations

**Note**: Daily data scraping is no longer available. New data must be obtained from the official biannual LZH releases at `https://boatrace.jp/owpc/pc/extra/data/download.html`

## Common Commands

### Daily Prediction Workflow
```bash
# Get today's race data and parse it
./get_race.sh today

# Convert to training format
./convert_csv.py today

# Generate predictions
./predict.py today

# Create betting recommendations  
./make_votes.py today
```

### Data Collection
```bash
# Scrape specific date (YYMMDD format)
./scrap_race.py 240607

# Parse scraped data
./parse_race.py 240607

# Combined scraping and parsing
./get_race.sh 240607
```

### Model Training
```bash
# Train LambdaRank model (uses 2+ years of historical data)
./train_lambdarank.py

# Aggregate training results
./aggregate_lambdarank_results.py
```

### Analysis and Validation
```bash
# Check prediction accuracy
./inquire.py

# Validate odds data
./check_odds.py

# Show performance deviations
./show_deviation.py
```

## Machine Learning Models

The system uses **LambdaRank with LightGBM** for ranking-based prediction optimized for NDCG metrics. Features include:
- Racer stats (win rates, age, weight, rank: A1/A2/B1/B2)
- Motor/boat performance ratios  
- Recent race results and season performance
- Track/venue information (24 venues across Japan)
- Race conditions

## File Naming Convention

- Date format: `YYMMDD`
- `b` prefix: Race schedules
- `m` prefix: Processed race data
- `l` prefix: LambdaRank predictions

## Development Notes

- All Python scripts are executable with shebang `#!/usr/bin/env python3`
- The `utils.py` file contains common functions for place mapping, rank encoding, and date utilities
- Training uses 2+ years of historical data for model stability
- Predictions generate both ranking scores and betting recommendations