# Simple script for standardizing pCLAMP / clampFit .abf data to [NWB](https://nwb.org/) format
- Allows for simple upload to [DANDI](https://dandiarchive.org/) public data repository
- Using [NeuroConv](https://github.com/catalystneuro/neuroconv) based upon https://neuroconv.readthedocs.io/en/main/conversion_examples_gallery/recording/abf.html

## Environment setup
1. Clone repository `https://github.com/xiubert/icephys_abf2nwb` and change to respository directory (`cd icephys_abf2nwb`).
2. Create python venv for running these scripts to isolate dependencies: `python -m venv env`
3. Activate virtual environment:
    - Unix/MacOS: `source env/bin/activate`
    - Windows: 
        - VSCode terminal defaults to PowerShell: `.\env\Scripts\Activate.ps1`
        - If in command prompt `.\env\bin\activate.bat`
4. Install dependencies: `pip install -r requirements.txt`

## Data standardization pipeline

### Option 1: Command-line script (Recommended)
Use `convert_abf_to_nwb.py` for automated batch conversion with logging:
```bash
# Interactive mode (prompts for Excel path)
python convert_abf_to_nwb.py

# Specify all paths
python convert_abf_to_nwb.py --excel_path /path/to/params.xlsx --data_path /path/to/abf_files

# Override metadata
python convert_abf_to_nwb.py --excel_path /path/to/params.xlsx --lab "Smith Lab" --institution "MIT"

# Multiple experimenters
python convert_abf_to_nwb.py --excel_path /path/to/params.xlsx --experimenter "John Doe" "Jane Smith"

# View help
python convert_abf_to_nwb.py --help
```

**Default configuration:**
- Output directory: `nwb_files/` (created in the data directory)
- Default lab, institution, and experimenter can be set at the top of the script
- If `--data_path` is not provided, uses the Excel file's parent directory

**Output:**
- NWB files in `nwb_files/` directory
- Log file: `conversion_log_YYYYMMDD_HHMMSS.txt`
- Error CSV: `error_experiments_YYYYMMDD_HHMMSS.csv` (if any errors occur)

### Option 2: Jupyter notebook
See `icephys_abf2nwb.ipynb`
1. Set relevant variables:
    - `excel_path` 
    - `ECEPHY_DATA_PATH`
    - `output_folder`
2. Optionally set:
    - `lab="my lab name"`
    - `institution="My University"`
    - `experimenter=["John Doe", "Jane Doe"]`
3. Run code block (`ctrl+enter`)

## Viewing NWB
-  with Neurosift v1: https://github.com/flatironinstitute/neurosift/tree/main
    1. `pip install --upgrade neurosift`
    2. `neurosift view-nwb ./nwb_files/2025053001.nwb` (browser should open)
-  with Neurosift v2: https://github.com/flatironinstitute/neurosift?tab=readme-ov-file
    1. `git submodule add https://github.com/flatironinstitute/neurosift.git`
    2. `cd neurosift`
    3. `git submodule update --init --recursive`
    4. `npm install`
    5. `npm run dev` => open browser to http://localhost:5173
    6. run server for hosting local nwb files w/ CORS support:
        1. global npm install of http-server: `npm install -g http-server`
        2. from project root run: `http-server -p 8000 --cors`
        3. open local file: http://localhost:5173/nwb?url=http://localhost:8000/nwb_files/2025053001.nwb