#!/usr/bin/python

import argparse
import sys
import os
import glob
import ffmpy

def create_arg_parser():
    """Creates and returns the ArgumentParser object."""
    parser = argparse.ArgumentParser(description='Convert .dav files in the input directory to MP4 using FFmpeg.')
    parser.add_argument('inputDirectory', help='Path to the input directory.')
    parser.add_argument('--deleteOriginal', default=False, action="store_true",
                        help='Delete the original file after successful conversion.')
    return parser

def list_files(input_dir):
    """Lists all .dav files in the specified directory."""
    return glob.glob(os.path.join(input_dir, "*.dav"))

def transcode_file(input_file):
    """Transcodes the input .dav file to MP4 format."""
    output_file = os.path.splitext(input_file)[0] + ".mp4"
    ffmpeg_command = ffmpy.FFmpeg(
        inputs={input_file: '-analyzeduration 100M -probesize 50M'},
        outputs={output_file: '-c:v libx264 -preset fast -strict -2 -y'}
    )
    
    try:
        print(f"Running command: {ffmpeg_command.cmd}")
        ffmpeg_command.run()
    except ffmpy.FFRuntimeError as e:
        print(f"Error processing file {input_file}: {e}")
        print("Skipping this file due to transcoding errors.")

def check_file(input_file, delete_original):
    """Checks the transcoded file and optionally deletes the original."""
    output_file = os.path.splitext(input_file)[0] + ".mp4"

    if not os.path.exists(output_file):
        print(f"Transcoded file not found: {output_file}")
        return

    original_size = os.path.getsize(input_file)
    transcoded_size = os.path.getsize(output_file)
    size_min = original_size * 0.25
    size_max = original_size * 1.2

    if transcoded_size < size_min or transcoded_size > size_max:
        print("Transcoded file size is outside reasonable limits.")
        print(f"Original size: {original_size} bytes")
        print(f"Transcoded size: {transcoded_size} bytes")
    else:
        print(f"File successfully transcoded: {output_file}")
        if delete_original:
            os.remove(input_file)
            print(f"Original file deleted: {input_file}")

if __name__ == "__main__":
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    input_dir = parsed_args.inputDirectory

    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        sys.exit(1)

    files = list_files(input_dir)
    if not files:
        print("No .dav files found in the specified directory.")
        sys.exit(0)

    files.sort()
    for file in files:
        transcode_file(file)
        check_file(file, parsed_args.deleteOriginal)
