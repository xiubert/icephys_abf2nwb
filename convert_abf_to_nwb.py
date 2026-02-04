#!/usr/bin/env python3
"""
NWB Conversion Script for Electrophysiology Data
Converts ABF files to NWB format based on Excel metadata sheet
Author: Patrick Cody
"""

import pandas as pd
from pathlib import Path
from neuroconv.datainterfaces import AbfInterface
from datetime import datetime
import argparse


# ============================================================================
# DEFAULT CONFIGURATION - MODIFY THESE AS NEEDED
# ============================================================================
DEFAULT_LAB = "Tzounopoulos Lab"
DEFAULT_INSTITUTION = "University of Pittsburgh"
DEFAULT_EXPERIMENTER = ["Yanjun Zhao"]
# ============================================================================


def log_message(log_file, message, print_to_console=True):
    """Write message to log file and optionally print to console"""
    with open(log_file, 'a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")
    if print_to_console:
        print(message)


def safe_get(value, default=""):
    """Helper function to safely get values (returns empty string for NaN)"""
    return value if pd.notna(value) else default


def ensure_abf_extension(filename):
    """Append .abf extension if not already present"""
    if pd.isna(filename):
        return filename
    filename = str(filename).strip()
    if not filename.lower().endswith('.abf'):
        filename += '.abf'
    return filename


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Convert ABF electrophysiology files to NWB format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use defaults
  python convert_abf_to_nwb.py

  # Specify paths
  python convert_abf_to_nwb.py --excel_path /path/to/params.xlsx --data_path /path/to/abf_files

  # Override metadata
  python convert_abf_to_nwb.py --lab "Smith Lab" --institution "MIT" --experimenter "John Doe"
        """
    )
    
    parser.add_argument(
        '--excel_path',
        type=str,
        help='Path to Excel metadata file'
    )
    
    parser.add_argument(
        '--data_path',
        type=str,
        help='Path to directory containing ABF files'
    )
    
    parser.add_argument(
        '--lab',
        type=str,
        default=DEFAULT_LAB,
        help=f'Lab name (default: {DEFAULT_LAB})'
    )
    
    parser.add_argument(
        '--institution',
        type=str,
        default=DEFAULT_INSTITUTION,
        help=f'Institution name (default: {DEFAULT_INSTITUTION})'
    )
    
    parser.add_argument(
        '--experimenter',
        type=str,
        nargs='+',
        default=DEFAULT_EXPERIMENTER,
        help=f'Experimenter name(s) (default: {DEFAULT_EXPERIMENTER})'
    )
    
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Determine paths
    if args.excel_path:
        excel_path = Path(args.excel_path)
    else:
        # Prompt user if not provided
        excel_input = input("Enter path to Excel metadata file: ").strip()
        excel_path = Path(excel_input)
    
    if args.data_path:
        ECEPHY_DATA_PATH = Path(args.data_path)
    else:
        # Use Excel file's parent directory as default
        ECEPHY_DATA_PATH = excel_path.parent
        print(f"Using data path: {ECEPHY_DATA_PATH}")
    
    # Output directory is always nwb_files in the data directory
    output_folder = ECEPHY_DATA_PATH / "nwb_files"
    output_folder.mkdir(parents=True, exist_ok=True)

    # Setup logging
    log_file = output_folder / f"conversion_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    error_csv = output_folder / f"error_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Track errors for CSV output
    error_records = []

    # Load Excel file
    log_message(log_file, "Starting NWB conversion process")
    log_message(log_file, f"Excel file: {excel_path}")
    log_message(log_file, f"Data path: {ECEPHY_DATA_PATH}")
    log_message(log_file, f"Output folder: {output_folder}")
    log_message(log_file, f"Lab: {args.lab}")
    log_message(log_file, f"Institution: {args.institution}")
    log_message(log_file, f"Experimenter(s): {', '.join(args.experimenter)}")

    df = pd.read_excel(excel_path)
    df = df.iloc[1:]  # Drop the first row after the header

    # Clean data: remove completely empty rows and rows with missing critical data
    initial_row_count = len(df)
    df = df.dropna(how="all")  # Remove completely empty rows
    df = df.dropna(subset=["EXPERIMENT ID", ".abf file"], how="any")  # Must have these
    df = df.reset_index(drop=True)

    rows_removed = initial_row_count - len(df)
    log_message(log_file, f"Removed {rows_removed} empty or incomplete rows. {len(df)} rows remaining.")

    # Apply .abf extension fix to the column
    df[".abf file"] = df[".abf file"].apply(ensure_abf_extension)

    # Group by EXPERIMENT ID
    grouped = df.groupby("EXPERIMENT ID")
    total_experiments = len(grouped)
    log_message(log_file, f"Processing {total_experiments} experiments")

    successful_conversions = 0
    failed_conversions = 0

    for experiment_id, group in grouped:
        try:
            log_message(log_file, f"\n--- Processing experiment {experiment_id} ---")
            first_row = group.iloc[0]

            # Construct icephys_metadata with safe value extraction
            icephys_metadata = {
                "cell_id": safe_get(first_row["cell_id"]),
                "slice_id": safe_get(first_row["slice_id"]),
                "targeted_layer": safe_get(first_row["targeted_layer"]),
                "inferred_layer": safe_get(first_row.get("inferred_layer", "")),
                "recording_sessions": [
                    {
                        "abf_file_name": safe_get(row[".abf file"]),
                        "stimulus_type": safe_get(row["stimulus_type"]),
                        "icephys_experiment_type": safe_get(row["icephys_experiment_type"])
                    }
                    for _, row in group.iterrows()
                    if pd.notna(row[".abf file"])  # Extra safety check
                ]
            }

            # Verify ABF files exist
            abf_file_paths = []
            missing_files = []
            for _, row in group.iterrows():
                if pd.notna(row[".abf file"]):
                    file_path = ECEPHY_DATA_PATH / row[".abf file"]
                    if not file_path.exists():
                        warning_msg = f"Warning: ABF file not found: {file_path}"
                        log_message(log_file, warning_msg)
                        missing_files.append(row[".abf file"])
                        continue
                    abf_file_paths.append(file_path)

            if not abf_file_paths:
                error_msg = f"Skipping experiment {experiment_id}: no valid ABF files found"
                log_message(log_file, error_msg)
                # Add all ABF files from this experiment to error records
                for _, row in group.iterrows():
                    error_records.append({
                        "EXPERIMENT ID": experiment_id,
                        ".abf file": row[".abf file"],
                        "error_type": "no_valid_files"
                    })
                failed_conversions += 1
                continue

            log_message(log_file, f"Found {len(abf_file_paths)} valid ABF files for experiment {experiment_id}")

            # Instantiate data interface
            interface = AbfInterface(
                file_paths=abf_file_paths,
                icephys_metadata=icephys_metadata
            )

            # Retrieve and update metadata
            metadata = interface.get_metadata()
            metadata['NWBFile'].update(
                identifier=str(experiment_id),
                session_description=safe_get(first_row["session_description"]),
                lab=args.lab,
                institution=args.institution,
                experimenter=args.experimenter
            )
            metadata["Subject"] = {
                "subject_id": safe_get(first_row["subject_id"]),
                "species": safe_get(first_row["species"]),
                "genotype": safe_get(first_row["genotype"]),
                "sex": safe_get(first_row["sex"]),
                "date_of_birth": str(safe_get(first_row["date_of_birth"]))
            }

            # Run conversion
            nwb_output_path = output_folder / f"{experiment_id}.nwb"
            interface.run_conversion(nwbfile_path=nwb_output_path, metadata=metadata)

            success_msg = f"✓ Finished NWB conversion for experiment {experiment_id}"
            log_message(log_file, success_msg)
            successful_conversions += 1

        except Exception as e:
            error_msg = f"✗ Error processing experiment {experiment_id}: {str(e)}"
            log_message(log_file, error_msg)
            # Add all ABF files from this experiment to error records
            for _, row in group.iterrows():
                error_records.append({
                    "EXPERIMENT ID": experiment_id,
                    ".abf file": row[".abf file"],
                    "error_type": f"conversion_error: {str(e)}"
                })
            failed_conversions += 1
            continue

    # Write summary to log
    log_message(log_file, "\n" + "="*50)
    log_message(log_file, "CONVERSION SUMMARY")
    log_message(log_file, "="*50)
    log_message(log_file, f"Total experiments: {total_experiments}")
    log_message(log_file, f"Successful conversions: {successful_conversions}")
    log_message(log_file, f"Failed conversions: {failed_conversions}")
    if total_experiments > 0:
        log_message(log_file, f"Success rate: {(successful_conversions/total_experiments)*100:.1f}%")

    # Save error CSV
    if error_records:
        error_df = pd.DataFrame(error_records)
        error_df.to_csv(error_csv, index=False)
        log_message(log_file, f"\nError details saved to: {error_csv}")
        log_message(log_file, f"Total error records: {len(error_records)}")
    else:
        log_message(log_file, "\nNo errors encountered - all conversions successful!")

    log_message(log_file, f"\nLog file saved to: {log_file}")
    print(f"\n{'='*50}")
    print(f"Conversion complete! Check {log_file} for details.")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()