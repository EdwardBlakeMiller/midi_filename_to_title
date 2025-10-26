import os
import argparse
import mido

def change_midi_title(input_file, output_file, new_title):
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
        print(f"Title of '{input_file}' changed to '{new_title}' and saved as '{output_file}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("in_dir")
    parser.add_argument("out_dir")
    parser.add_argument("-remove_substring")

    opts = parser.parse_args()

    os.makedirs(opts.out_dir, exist_ok=True)

    for ifile, filename in enumerate(os.listdir(opts.in_dir), start=1):
        full_path = os.path.join(opts.in_dir, filename)
        print(f"Working on {full_path}")
        if not os.path.isfile(full_path):
            print(f"Skipping {full_path}")
            continue

        desired_title = os.path.splitext(os.path.basename(full_path))[0]

        if opts.remove_substring and opts.remove_substring in desired_title:
            desired_title = desired_title.replace(opts.remove_substring, "")

        orig_basename, orig_ext = os.path.splitext(full_path)

        new_filename = os.path.join(opts.out_dir, os.path.basename(full_path))

        change_midi_title(full_path, new_filename, desired_title)
