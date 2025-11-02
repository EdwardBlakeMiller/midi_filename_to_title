import os
import argparse
import mido
import shutil
import zipfile
import tempfile
from tqdm import tqdm

def change_midi_title(input_file, output_file, new_title, verbose=False):
    """
    Changes the title of a MIDI file.
    
    Args:
        input_file (str): The path to the original MIDI file.
        output_file (str): The path to save the modified MIDI file.
        new_title (str): The new title for the MIDI file.
    """
    try:
        # Open the MIDI file
        midi_file = mido.MidiFile(input_file)

        # This should convert from type 1 to type 0
        mido.merge_tracks(midi_file.tracks)

        # Assuming the track name is in the first track (track 0)
        # This is common but not guaranteed for all MIDI files.
        track = midi_file.tracks[0]

        # Remove existing 'track_name' meta-events
        # Iterate backwards to safely delete items from the list
        for i in range(len(track) - 1, -1, -1):
            if track[i].type == 'track_name':
                del track[i]

        # Create a new 'track_name' meta-event with the desired title
        new_title_message = mido.MetaMessage('track_name', name=new_title, time=0)

        # Insert the new title message at the beginning of the track
        # This is important for some software that reads the title early.
        track.insert(0, new_title_message)

        # Save the changes to a new MIDI file
        midi_file.save(output_file)
        if verbose:
            print(f"\t\tNew Title:      {new_title}")
            print(f"\t\tOutput File:    {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred with {input_file}: {e}")

def findstem(arr):

    # Determine size of the array
    n = len(arr)

    # Take first word from array
    # as reference
    s = arr[0]
    l = len(s)

    res = ""

    for i in range(l):
        for j in range(i + 1, l + 1):

            # generating all possible substrings
            # of our reference string arr[0] i.e s
            stem = s[i:j]
            k = 1
            for k in range(1, n):

                # Check if the generated stem is
                # common to all words
                if stem not in arr[k]:
                    break

            # If current substring is present in
            # all strings and its length is greater
            # than current result
            if (k + 1 == n and len(res) < len(stem)):
                res = stem

    return res

def find_maximum_common_substring(directory):
    """Finds the maximum common substring in filenames
       excluding the file extension.
    """

    list_of_basenames = []
    for filename in os.listdir(directory):
        basename = os.path.basename(os.path.splitext(filename)[0])
        list_of_basenames.append(basename)

    stem = findstem(list_of_basenames)

    stem = stem.strip()

    return stem

def process_zip_file(zip_file_path, extract_parent_dir):

    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zf:
            # Extracted dir will be zip file without the .zip
            extract_to_directory = os.path.splitext(os.path.basename(zip_file_path))[0]
            extract_to_directory = os.path.join(extract_parent_dir, extract_to_directory)
            os.makedirs(extract_to_directory, exist_ok=True)

            zf.extractall(extract_to_directory)
            print(f"Successfully unzipped '{zip_file_path}' to '{extract_to_directory}'")
    except zipfile.BadZipFile:
        print(f"Error: '{zip_file_path}' is not a valid ZIP file.")
    except FileNotFoundError:
        print(f"Error: ZIP file not found at '{zip_file_path}'.")

    mcs = find_maximum_common_substring(extract_to_directory)
    # Don't allow a single character mcs
    # because all we end up doing is replacing this
    # single character with a space
    if len(mcs) == 1: 
        mcs = ""
    print(f"\tMCS: {mcs}")

    for file_path in tqdm(os.listdir(extract_to_directory)):
        file_path = os.path.join(extract_to_directory, file_path)
        #print(f"\tWorking on {file_path}")
        if not os.path.isfile(file_path):
            print(f"\tSkipping {file_path}")
            continue
        if not file_path.endswith(".mid") and not file_path.endswith(".MID"): 
            print(f"\tSkipping non-midi file {file_path}")
            continue

        desired_title = os.path.splitext(os.path.basename(file_path))[0]
        if mcs:
            desired_title = desired_title.replace(mcs, " ")

        orig_basename, orig_ext = os.path.splitext(file_path)

        new_file_path = os.path.join(extract_to_directory, os.path.basename(file_path))

        change_midi_title(file_path, new_file_path, desired_title)

    # Replace the old zip with a new zip
    assert "new" not in zip_file_path
    new_zip_file_without_ext = zip_file_path.replace(".zip", "_new")
    shutil.make_archive(new_zip_file_without_ext, 'zip', extract_to_directory)
    shutil.move(new_zip_file_without_ext + '.zip', zip_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir")

    opts = parser.parse_args()

    with tempfile.TemporaryDirectory(dir=opts.in_dir) as temp_dir:
        print(f"Temporary directory created at: {temp_dir}")
    for zip_filename in os.listdir(opts.in_dir):
        print(f"On {zip_filename}")
        zip_file_path = os.path.join(opts.in_dir, zip_filename)
        process_zip_file(zip_file_path, temp_dir)
