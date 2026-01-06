import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
from Cable import Cable
from CleanData import split_file
import io
import os
import re
import shutil
import zipfile

import numpy as np
#from scipy import stats


from pathlib import Path

def zip_directory_to_bytes(dir_path: Path) -> bytes:
    """
    Zips the directory at dir_path into an in-memory ZIP and returns its bytes.
    The archive preserves the folder structure relative to dir_path.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in dir_path.rglob("*"):
            if p.is_file():
                arcname = p.relative_to(dir_path)
                zf.write(p, arcname)
    buffer.seek(0)
    return buffer.getvalue()

def clear_temp(temp_root: Path):
    temp_root.mkdir(exist_ok=True)
    for p in temp_root.iterdir():
        if p.is_file():
            p.unlink(missing_ok=True)
        else:
            shutil.rmtree(p, ignore_errors=True)

def process_data_root(data_root: Path, output_root: Path):
    for size_folder in os.listdir(data_root):
        size_path = os.path.join(data_root, size_folder)
        if not os.path.isdir(size_path):
            continue
        
        m = re.search(r'-?\d+(?:\.\d+)?', size_folder)
        if not m:
            continue

        length = float(m.group(0))
        

        for serial_folder in os.listdir(size_path):
            serial_path = os.path.join(size_path, serial_folder)
            if not os.path.isdir(serial_path):
                continue
            sn = serial_folder
            serial_number = sn
            
            cable = Cable(serial_number, length)

            for file_name in os.listdir(serial_path):
                file_path = os.path.join(serial_path, file_name)
                if not os.path.isfile(file_path):
                    continue
                with open(file_path, "rb") as f:
                    extracted_df, type = split_file(f, size_folder, serial_folder, output_root)
                    cable.add_df(type, extracted_df)

            cables.append(cable)
    return cables


def show_download_dialog():
    if output_root.exists():
        zip_bytes = zip_directory_to_bytes(output_root)
        st.write("A ZIP containing everything under `temp/CleanData` is ready.")
        st.download_button(
            label="⬇️ Download all CleanData (ZIP)",
            data=zip_bytes,
            file_name="CleanData_All.zip",
            mime="application/zip",
            help="Downloads all cleaned files generated during processing."
        )
    else:
        st.warning("No cleaned data found yet. Run processing to generate files.")



st.title("Summary Statistics for PTL Cables")
st.markdown("upload a `.zip` containing your `Data` folder with the structure "
            "`Data/<Length> Inches/<RunID>/`")

temp_root = Path("C:\\temp")

output_root = temp_root / "CleanData"


uploaded_zip = st.file_uploader("Upload Data.zip", type=["zip"], accept_multiple_files=False)


cables = []

if uploaded_zip is not None:
    clear_temp(temp_root)
    with zipfile.ZipFile(io.BytesIO(uploaded_zip.read())) as zf:
        zf.extractall(temp_root)

    data_root = temp_root / "Data"
    if not data_root.exists():
        # maybe the zip contains the level directly
        data_root = temp_root

        
    with st.spinner("Parsing uploaded data..."):
        cables = process_data_root(data_root, output_root)
    st.success(f"Loaded {len(cables)} cable records.")

    all_extracted = []

    for size_folder in os.listdir(data_root):
        size_path = os.path.join(data_root, size_folder)
        if not os.path.isdir(size_path):
            continue

        for serial_folder in os.listdir(size_path):
            serial_path = os.path.join(size_path, serial_folder)
            if not os.path.isdir(serial_path):
                continue

            for file_name in os.listdir(serial_path):
                file_path = os.path.join(serial_path, file_name)
                if not os.path.isfile(file_path):
                    continue

                with open(file_path, "rb") as f:
                    extracted_df, type = split_file(f, size_folder, serial_folder, output_root)
                    if extracted_df is not None and not extracted_df.empty:
                        all_extracted.append(extracted_df)

    # Combine all DataFrames (or empty DataFrame if none)
    combined_extracted = pd.concat(all_extracted, ignore_index=True) if all_extracted else pd.DataFrame()


    show_download_dialog()
