import os
from math import ceil, sqrt

from PIL import Image

from .exceptions import CollageOfZeroFramesError
from .utils import does_path_exists

# Module to create collage from list of images, the
# images are the extracted frames of the input video.


def make_collage(
    image_list: list[str],
    output_path: str,
    collage_image_width: int = 1024,
) -> None:
    """
    Creates the collage from list of images.

    Collage that should be as close to the shape of a square.

    The images are arranged by timestamp of the frames, their
    index in the image_list is based on thier timestamp on the
    video. The image with the index 2 is a frame from the 3rd
    second and an index 39 is from at the 40th second. The index
    is one less due to zero-based indexing.


    Let's say we have a list with 9 images.

    As the images should be arranged in a way to resemble a
    square, we take the square root of 9 and that is 3. Now
    we need to make a 3x3 frames collage.

    Arrangement should be:
    Img1 Img2 Img3
    Img4 Img5 Img6
    Img7 Img8 Img9

    If the number of images is not a perfect square, calculate the
    square root and round it up to the nearest integer (ceiling).
    The grid is filled by distributing the available images
    evenly across the total number of cells in the grid.

    If number of images is 13, which is not a perfect square.

    sqrt(13) = 3.605551275463989
    ceil(3.605551275463989) = 4

    Thus the image should be 4x4 frames of collage.

    Arrangement should be:
    -----------------------------
    |  Img1  Img2  Img3   Img4  |
    |  Img5  Img6  Img7   Img8  |
    |  Img9  Img10 Img11  Img12 |
    |  Img13 Img14 Img15  Img16 |
    -----------------------------

    Note: The indices in the example above (Img1...Img16) represent
    the positions in the grid. The actual images are selected from
    the input list to fill these positions. There are no empty spaces.

    :param image_list: A python list containing the list of absolute
                       path of images that are to be added in the collage.
                       The order of images is kept intact and is very important.

    :param output_path: Absolute path of the collage including
                        the image name. (This is where the collage is saved.)
                        Example: '/home/username/projects/collage.jpeg'.

    :param collage_image_width: An integer specifying the image width of the
                                output collage. Default value is 1024 pixels.

    :return: None

    :rtype: NoneType
    """
    number_of_images = len(image_list)

    images_per_row_in_collage = int(ceil(sqrt(number_of_images)))

    if number_of_images == 0:
        raise CollageOfZeroFramesError("Can not make a collage of zero images.")

    output_path_dir = os.path.dirname(output_path) + "/"
    if not does_path_exists(output_path_dir):
        raise FileNotFoundError("Directory at which output collage is to be saved does not exists.")

    # arbitrarily selecting the first image from the list, index 0
    with Image.open(image_list[0]) as first_frame_image_in_list:
        # Find the width and height of the first image of the list.
        # Assuming all the images have same size.
        frame_image_width, frame_image_height = first_frame_image_in_list.size

    # scale is the ratio of collage_image_width and product of
    # images_per_row_in_collage with frame_image_width.

    # The scale will always lie between 0 and 1, which implies that
    # the images are always going to get downsized.
    scale = (collage_image_width) / (images_per_row_in_collage * frame_image_width)

    # Calculating the scaled height and width for the frame image.
    scaled_frame_image_width = ceil(frame_image_width * scale)
    scaled_frame_image_height = ceil(frame_image_height * scale)

    # Set the number of rows equal to the number of images per row.
    # This ensures the collage is a square (or as close as possible).
    number_of_rows = images_per_row_in_collage

    # Multiplying the height of one downsized image with number of rows.
    # Height of 1 downsized image is product of scale and frame_image_height
    # Total height is number of rows times the height of one downsized image.
    collage_image_height = ceil(scale * frame_image_height * number_of_rows)

    # Create an image of passed collage_image_width and calculated collage_image_height.
    # The downsized images will be pasted on this new base image.
    # The image is 0,0,0 RGB(black).
    collage_image = Image.new("RGB", (collage_image_width, collage_image_height))

    # keep track of the x and y coordinates of the resized frame images

    frames_count = number_of_rows * images_per_row_in_collage
    # iterate the frames and paste them on their position on the collage_image
    for j in range(number_of_rows):
        for i in range(images_per_row_in_collage):
            frame_index = j * images_per_row_in_collage + i
            # Calculate the image index based on the frame index.
            # We use linear interpolation to map the grid position (frame_index)
            # to the image list index.
            # Formula: frame_index * (total_images / total_grid_slots)
            # This ensures even distribution and includes the last image.
            image_index = int(frame_index * len(image_list) / frames_count)
            frame_path = image_list[image_index]

            # open the frame image, must open it to resize it using the thumbnail method
            frame = Image.open(frame_path)

            # scale the opened frame images
            frame = frame.resize((scaled_frame_image_width, scaled_frame_image_height), Image.Resampling.LANCZOS)

            # set the value of x to that of i's value.
            # i is set to 0 if we are on the first column.
            x = i * scaled_frame_image_width

            # Calculate y coordinate based on the current row index j.
            y = j * scaled_frame_image_height

            # paste the frame image on the newly created base image(base image is black)
            collage_image.paste(frame, (x, y))
            frame.close()

    # save the base image with all the scaled frame images embeded on it.
    collage_image.save(output_path)
    collage_image.close()
