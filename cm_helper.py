import os
import json
import numpy as np
import pandas as pd
import nibabel as nib
from nilearn.datasets.utils import _md5_sum_file

# uniquely identify each item ("hemi" could be None)
FNAME_KEYS = ["source", "desc", "space", "den", "hemi", "res"]
# auto-generated (checksum could be None if no file available)
AUTO_KEYS = ["format", "fname", "rel_path", "checksum"]
# required but could be None
COND_KEYS = ["title", "tags", "redir", "url"]
# minimal keys for each item
MINIMAL_KEYS = FNAME_KEYS + AUTO_KEYS + COND_KEYS
# keys for redirection
REDIR_KEYS = ["space", "den"]
# keys for more metadata (for each source)
INFO_KEYS = ["source", "refs", "comments", "demographics"]


def parse_filename(fname):
    try:
        base, *ext = fname.split(".")
        fname_dict = dict(
            [pair.split("-") for pair in base.split("_") if pair != "feature"]
        )
        print(fname_dict)
        return fname_dict, "".join(ext)
    except ValueError:
        print("Wrong filename format!")
        return None


def parse_json(fname, root="ds-annotations"):
    try:
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)
            # check root type
            if isinstance(root, str):
                root = [root]
            for key in root:
                data = data[key]
            return data
    except (TypeError, ValueError) as err:
        print(f"Error parsing json file: {err}")
        return


def write_json(data, fname, root="ds-annotations"):
    output = dict()
    output[root] = data
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)


def complete_json(
    input_data,
    ref_keys="minimal",
    input_root=None,
    output_fname=None,
    output_root=None,
):
    # this is to add missing fields to existing data
    # could accept data dict list or filename as input
    # set minimal vs info
    if ref_keys == "minimal":
        ref_keys = MINIMAL_KEYS
        if not input_root:
            input_root = "ds-annotations"
        if output_fname and not output_root:
            output_root = "ds-annotations"
    elif ref_keys == "info":
        ref_keys = INFO_KEYS
        if not input_root:
            input_root = "info"
        if output_fname and not output_root:
            output_root = "info"
    else:
        print("Not supported, return")
        return
    # check input
    if isinstance(input_data, list):
        data = input_data
    else:
        data = parse_json(input_data, root=input_root)
    # make output
    output = []
    for item in data:
        output.append({key: (item[key] if key in item else None) for key in ref_keys})
    # write output
    if output_fname:
        write_json(output, output_fname, root=output_root)
    return output


def describe_fillable_json(fname):
    # this is for quickly debug the fillable json
    # this is only for MINIMAL_KEYS
    data = parse_json(fname)
    if not data:
        print("Json data not load correctly, return")
        return

    # read in as dataframe
    df_data = pd.DataFrame(data, columns=MINIMAL_KEYS)

    # check for missing keys (= NaN, while empty = None)
    is_missing_keys = (
        df_data.applymap(lambda x: isinstance(x, float)) & df_data.isnull()
    ).any(axis=None)
    if is_missing_keys:
        print(
            "Input file is missing MINIMAL_KEYS, "
            "please use complete_json(input_data, ref_keys=MINIMAL_KEYS)"
        )

    # do some useful summary

    return df_data


def generate_auto_keys(item):
    # AUTO_KEYS = ["format", "fname", "rel_path", "checksum"]
    # Filename convention (surface)
    # source-<source>_desc-<desc>_space-<space>_den-<den>_hemi-{L,R}_feature.shape.gii
    # Filename convention (volumetric)
    # source-<source>_desc-<desc>_space-<space>_res-<res>_feature.nii.gz

    # check format by checking "hemi"
    is_surface = item["den"] or item["hemi"] or item["format"] == "surface"
    is_volume = item["res"] or item["format"] == "volume"

    if is_surface:  # this is surface file
        item["format"] = "surface"
        item["fname"] = (
            f"source-{item['source']}_desc-{item['desc']}"
            f"_space-{item['space']}_den-{item['den']}"
            f"_hemi-{item['hemi']}_feature.shape.gii"
        )
    elif is_volume:  # this is volume file
        item["format"] = "volume"
        item["fname"] = (
            f"source-{item['source']}_desc-{item['desc']}"
            f"_space-{item['space']}_res-{item['res']}"
            f"_feature.nii.gz"
        )
    else:
        print("Missing surface/volume keys, format and fname not generated")
    item["rel_path"] = f"{item['source']}/{item['desc']}/{item['space']}/"
    # check file existence
    if item["fname"] and os.path.isfile(item["rel_path"] + item["fname"]):
        item["checksum"] = _md5_sum_file(item["rel_path"] + item["fname"])
    return item


def clean_minimal_keys(item):
    if item["format"] == "surface":
        item.pop("res", None)
    elif item["format"] == "volume":
        item.pop("den", None)
        item.pop("hemi", None)
    else:
        print("Wrong value for format, do not clean")
    return item


def generate_release_json(input_fname, output_fname):
    # reuse this function to generate a new release json
    # input should be a fillable json
    data = parse_json(input_fname)
    output = []
    for item in data:
        item = generate_auto_keys(item)
        item = clean_minimal_keys(item)
        output.append({key: item[key] for key in MINIMAL_KEYS if key in item})
    write_json(output, output_fname, root="ds-annotations")


def generate_redir_json(data):
    pass


def parse_fname_list(fname):
    # helper for read in a list of filenames
    with open(fname, "r", encoding="utf-8") as f:
        fname_list = f.readlines()
    fname_list = [name.strip() for name in fname_list]
    print(fname_list)
    data = [parse_filename(name)[0] for name in fname_list]
    return data


def save_array_as_gii(data, fname):
    # @Ross
    da = nib.gifti.GiftiDataArray(data, datatype="NIFTI_TYPE_FLOAT32")
    img = nib.GiftiImage(darrays=[da])
    nib.save(img, fname)
