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

## Metadata spreadsheet (`ephys_nwb_params.xlsx`)

The `EXPERIMENT SESSIONS` sheet drives every conversion. The header row defines the column names; the second row holds format hints and is skipped. Each subsequent row is one `.abf` recording.

**Grouping:** rows that share the same `EXPERIMENT ID` are bundled into a single NWB file (`<EXPERIMENT ID>.nwb`), with each row contributing one recording session. Per-subject and per-cell fields (`subject_id`, `species`, `cell_id`, `slice_id`, `session_description`, etc.) are read from the *first* row in the group, so keep them consistent within a group.

**Required columns** (rows missing either are dropped):
- `EXPERIMENT ID` — unique experiment identifier, e.g. `YYYYMMDDXX`. Used as the NWB `identifier` and the output filename.
- `.abf file` — recording session filename (e.g. `25530001.abf`). The `.abf` extension is added automatically if omitted.

**Per-recording columns** (one value per row):
- `stimulus_type` — description of the stimulus protocol, typically the `.pro` file name (e.g. `1Hz_LED_train-ChR stim_ic_1Hz.pro`).
- `icephys_experiment_type` — recording mode, e.g. `voltage_clamp` or `current_clamp`.

**Per-experiment columns** (read from the first row of each `EXPERIMENT ID` group):
- `session_description` — free-text NWB session description. **Tip:** include the manuscript figure number(s) here (e.g. `Intracellular electrophysiology experiment — Fig. 3B, Fig. S2`) to track which figure(s) a subject's data was used in.
- `subject_id` — animal identifier (e.g. `subject_ID123`).
- `species` — full Latin binomial, e.g. `Mus musculus`.
- `genotype` — e.g. `Ntsr1-Cre`.
- `sex` — `M`, `F`, or `U`.
- `date_of_birth` — ISO 8601 timestamp, e.g. `2025-04-15T00:00:00`.
- `cell_id` — recorded cell identifier (e.g. `YYYYMMDDXXXX`).
- `slice_id` — slice identifier (e.g. `YYYYMMDDXXXX`).
- `targeted_layer` — intended cortical layer, e.g. `L2-3(medial)`.
- `inferred_layer` — post-hoc layer assignment; optional, leave blank if unused.

`lab`, `institution`, and `experimenter` are *not* in the spreadsheet — set them in the script defaults or pass them via CLI flags (see below).

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
-  with Neurosift v2: https://github.com/flatironinstitute/neurosift/tree/main
    1. `pip install --upgrade neurosift`
    2. `neurosift view-nwb ./nwb_files/2025053001.nwb` (browser should open)