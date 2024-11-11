#!/usr/bin/env python3
"""This script allows to automatically paste generated images on random backgrounds."""

import os
import random
import argparse
from PIL import Image
from tqdm import tqdm


def darken_image(image, factor):
    """Darken the image by a given factor (0.0 - 1.0)."""
    # Ensure the factor is between 0 and 1
    factor = max(0, min(factor, 1))

    # Create a new image with the same size and mode as the original
    darkened_image = Image.new("RGBA", image.size)

    # Darken each pixel in the image
    for x in range(image.width):
        for y in range(image.height):
            r, g, b, a = image.getpixel((x, y))
            # Apply the darkness factor
            darkened_image.putpixel((x, y), (int(r * factor), int(g * factor), int(b * factor), a))

    return darkened_image

def main():
    # Get and parse all given arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--images",
                        type=str,
                        help="Path to object images to paste.")
    parser.add_argument("-b",
                        "--backgrounds",
                        type=str,
                        help="Path to background images to paste on.")
    parser.add_argument("-t",
                        "--types",
                        default=('jpg', 'jpeg', 'png'),
                        type=str,
                        nargs='+',
                        help="File types to consider. Default: jp[e]g, png.")
    parser.add_argument(
        "-w",
        "--overwrite",
        action="store_true",
        help=
        "Merges images and backgrounds, overwriting original files. Default: False."
    )
    parser.add_argument("-o",
                        "--output",
                        default="output",
                        type=str,
                        help="Output directory. Default: 'output'.")
    args = parser.parse_args()

    # Create an output directory if `overwrite` is not selected
    if not args.overwrite:
        if args.output == "output":
            os.makedirs(os.path.join(args.images, "output"), exist_ok=True)
        else:
            os.makedirs(args.output, exist_ok=True)

    # Go through all files in given `images` directory
    for file_name in tqdm(os.listdir(args.images)):
        # Matching files to given `types` and opening images
        if file_name.lower().endswith(args.types):
            img_path = os.path.join(args.images, file_name)
            img = Image.open(img_path)
            img_w, img_h = img.size

            # Selecting and opening a random image file from given `backgrounds` directory to use as background
            background_path = random.choice([
                os.path.join(args.backgrounds, p)
                for p in os.listdir(args.backgrounds)
                if p.lower().endswith(args.types)
            ])
            background = Image.open(background_path).convert('RGBA').resize([img_w, img_h])
            #background = Image.open(background_path).convert('RGBA').resize([960, 544])

            # Darken the background randomly
            if random.random() < 0.3: #at 0.3 probability apply transformation of darkening to background
                darkness_factor = random.uniform(0.4, 0.9)  # Random factor between 0.4 and 0.9
                background = darken_image(background, darkness_factor)
            # Pasting the current image on the selected background
            #background.paste(img, mask=img.convert('RGBA'))
            background.paste(img, mask=img)


            # Overwrites original image with merged one if `overwrite` is selected
            if args.overwrite:
                background.save(img_path)
            # Else store merged image in default or provided `output` directory
            else:
                output_filename = file_name  # Retain the original filename
                if args.output == "output":
                    output_path = os.path.join(args.images, "output", output_filename)
                else:
                    output_path = os.path.join(args.output, output_filename)

                background.save(output_path)


if __name__ == "__main__":
    main()