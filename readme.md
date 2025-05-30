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

## Data standardization pipeline:
1. See `icephys_abf2nwb.ipynb`
    1. Set relevant variables:
        - `excel_path` 
        - `ECEPHY_DATA_PATH`
        - `output_folder`
    2. Optionally set:
        - `lab="my lab name"`
        - `institution="My University"`
        - `experimenter=["John Doe", "Jane Doe"]`
    3. Run code block (`ctrl+enter`)