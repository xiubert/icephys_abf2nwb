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