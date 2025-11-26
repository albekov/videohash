import subprocess


def generate_video_with_lavfi(output_path: str, lavfi_str: str = "testsrc=duration=5:size=1280x720:rate=30"):
    """
    Generates a video file using ffmpeg's lavfi (Libavfilter) input virtual device.
    """
    command = [
        "ffmpeg",
        "-f",
        "lavfi",
        "-i",
        lavfi_str,
        "-y",  # Overwrite output files without asking
        output_path,
    ]
    # Suppress output unless there's an error
    subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def scale_video(input_path: str, output_path: str, width: int, height: int):
    """
    Scales a video to the specified dimensions using ffmpeg.
    """
    command = [
        "ffmpeg",
        "-i",
        input_path,
        "-vf",
        f"scale={width}:{height}",
        "-y",
        output_path,
    ]
    subprocess.check_call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
