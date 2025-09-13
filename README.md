# Human QuickSort App (ko.py)

A Streamlit application that implements a human-driven QuickSort algorithm for ranking people by closeness/preference.

## Overview

This app allows you to sort a list of names by asking you to make pairwise comparisons. Instead of using automated sorting algorithms, it uses human judgment to determine the relative closeness or preference between people.

## How It Works

1. **Loads Data**: Reads names from `names.json` file
2. **QuickSort Algorithm**: Uses the QuickSort partitioning approach with human comparisons
3. **Pairwise Comparisons**: Presents two people at a time and asks "Who is closer to you?"
4. **Progressive Sorting**: Builds up a sorted list through iterative comparisons
5. **Saves Results**: Outputs the final sorted list to `sorted.json`

## Features

- **Interactive Sorting**: Human-driven comparison interface
- **Progress Tracking**: Shows completion status and remaining items
- **Partial Save**: Save progress at any point and resume later
- **Restart Option**: Reset and start over if needed
- **Visual Feedback**: Clear UI with emojis and intuitive buttons

## Installation

### Prerequisites

If you don't have Python and pip installed:

**On macOS:**
```bash
# Install Python (includes pip)
brew install python
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**On Windows:**
- Download Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### Install Dependencies

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure `names.json` exists with your list of names
2. Run the application:
   ```bash
   streamlit run ko.py
   ```
3. Open your browser to the provided URL (typically `http://localhost:8501`)
4. Make comparisons by clicking "Pick Left" or "Pick Right" buttons
5. Continue until all names are sorted
6. Save the final sorted list

## File Dependencies

- **Input**: `names.json` (list of names to sort)
- **Output**: `sorted.json` (final sorted list)

## Algorithm Details

The app implements a modified QuickSort where:
- A pivot is selected from the middle of each sublist
- You compare each remaining item against the pivot
- Items are partitioned into "closer than pivot" and "farther than pivot"
- The process repeats recursively until all items are sorted
- Final result is in descending order of closeness (closest first)
