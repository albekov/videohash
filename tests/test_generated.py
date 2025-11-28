import pytest

from videohash import VideoHash

from .utils import generate_video_with_lavfi, scale_video


@pytest.fixture
def temp_video_dir(tmp_path):
    return tmp_path


def test_lavfi_testsrc(temp_video_dir):
    video_path = str(temp_video_dir / "testsrc.mp4")
    generate_video_with_lavfi(video_path, "testsrc=duration=3:size=640x480:rate=30")

    vh = VideoHash(path=video_path)
    # We don't assert exact hash yet, just stability and no errors
    assert vh.hash is not None
    assert len(vh.hash) == 66  # 64 bits + 0b prefix
    vh.delete_storage_path()


def test_lavfi_smptebars(temp_video_dir):
    video_path = str(temp_video_dir / "smptebars.mp4")
    generate_video_with_lavfi(video_path, "smptebars=duration=3:size=640x480:rate=30")

    vh = VideoHash(path=video_path)
    assert vh.hash is not None
    vh.delete_storage_path()


def test_lavfi_color(temp_video_dir):
    video_path = str(temp_video_dir / "color.mp4")
    generate_video_with_lavfi(video_path, "color=c=red:duration=3:size=640x480:rate=30")

    vh = VideoHash(path=video_path)
    assert vh.hash is not None
    vh.delete_storage_path()


@pytest.mark.slow
@pytest.mark.parametrize("duration", [1, 3, 5, 15, 30])
def test_similarity_different_quality(temp_video_dir, duration):
    # Use smptebars as it has distinct features but no text that might get garbled
    high_res_path = str(temp_video_dir / "high_res.mp4")
    low_res_path = str(temp_video_dir / "low_res.mp4")

    # Generate high resolution video (HD)
    generate_video_with_lavfi(high_res_path, f"smptebars=duration={duration}:size=1280x720:rate=30")

    # Scale down to low resolution (QVGA)
    scale_video(high_res_path, low_res_path, 320, 240)

    vh_high = VideoHash(path=high_res_path)
    vh_low = VideoHash(path=low_res_path)

    # They should be similar (allow some tolerance for scaling artifacts)
    diff = vh_high - vh_low
    print(f"Hamming distance: {diff}")
    # Default threshold is ~10 bits (15% of 64). Scaling artifacts can cause slightly more.
    assert diff <= 12

    vh_high.delete_storage_path()
    vh_low.delete_storage_path()
