# midi_filename_to_title
Changes the track name meta event in the midi file to match the file name.

This is intended to get the Disklavier MIDI files from the Kuhmann Directory to be formatted in such a way that they can be easily viewed (and played) on a Yamaha Disklavier Enspire system.

The core operations performed here:

1. Convert MIDI to format 0 (only a single track)
2. Remove existing 'track_name' meta-events
3. Set a new 'track_name' meta-event using the filename.

It so happens that the filenames are very well organized but the track information display poorly on Disklavier Enspire without these changes.

## Dependancies

This uses the `mido` python library to manipulate the midi files.
  Get it with `pip install mido`
