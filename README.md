# cortical-maps-dev

This is only to help dealing with the json structure issues.
Breaking changes will be made!

## Quickstart

To start from a list of valid filenames,

- `from cm_helper import *`
- `data = parse_fname_list("fname_list.txt")`
- `complete_json(data, ref_keys="minimal", output_fname="annot-fillable.json")`
- `generate_release_json("annot-fillable.json", "annot-release.json")`

## Description

We would have three files, (they can also be nested in another json)

- `annot-fillable.json` for manual adding / editing the data information
- `annot-release.json` for a cleaner release version (auto-generated)
- `annot-info.json` for necessary supporting information ("source"-level)
  - I did not automate this much because this would be easy to edit

For the dataset,

- You would only need to fill some of `FNAME_KEYS = ["source", "desc", "space", "den", "hemi", "res"]` to uniquely identify one brain map
- Optional keys include `COND_KEYS = ["title", "tags", "redir", "url"]`
  - `title`: a one-line short description of the data
  - `tags`: contains a list of values for filtering data
  - `redir`: this is a potential way to define default `REDIR_KEYS = ["space", "den"]`, but currently not in use
  - `url`: download url
- Before release, we will automatically generate some keys `AUTO_KEYS = ["format", "fname", "rel_path", "checksum"]`
- For the `annot-fillable.json` file, we would include `MINIMAL_KEYS = FNAME_KEYS + AUTO_KEYS + COND_KEYS` only for easier editing, when released as `annot-release.json`, unnecessary keys would be removed and `AUTO_KEYS` would be generated.

For the additional information,

- You would fill the `annot-info.json` with `INFO_KEYS = ["source", "refs", "comments", "demographics"]`

## Example Workflow

1. Fill `annot-fillable.json` with necessary keys from `["source", "desc", "space", "den", "hemi", "res"]`
1. Run `complete_json("annot-fillable.json", ref_keys="minimal", output_fname="annot-fillable.json")` to keep the current edits and complete a full fillable list

   - Edit the file freely
   - For `annot-info.json`, use `complete_json("annot-info.json", ref_keys="info", output_fname="annot-info.json")`

1. Run `generate_release_json("annot-fillabel.json", "annot-release.json")` to output a clean version

1. Repeat the two steps above to fill more information or generate new release file
