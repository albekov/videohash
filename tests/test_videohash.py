import os

import pytest

from videohash.exceptions import DidNotSupplyPath, StoragePathDoesNotExist
from videohash.utils import create_and_return_temporary_directory
from videohash.videohash import VideoHash

this_dir = os.path.dirname(os.path.realpath(__file__))


def test_all():
    video_path = os.path.join(this_dir, os.path.pardir, "assets", "rocket.mkv")
    videohash1 = VideoHash(path=video_path, frame_interval=3)
    videohash1.delete_storage_path()
    hash1 = videohash1.hash
    hash_hex1 = videohash1.hash_hex
    assert hash1 == "0b1111100000101000111111111111101110111110010011010000001100000011"
    assert str(videohash1) == "0b1111100000101000111111111111101110111110010011010000001100000011"
    assert hash_hex1 == "0xf828fffbbe4d0303"
    assert videohash1 - "0b1111100000101000111111111111101110111110010011010000001100000011" == 0
    assert hash_hex1 in repr(videohash1)
    assert hash1 in repr(videohash1)
    assert (len(videohash1) - 2) == videohash1.bits_in_hash
    with pytest.raises(AssertionError):
        assert videohash1 != hash_hex1

    with pytest.raises(TypeError):
        _ = videohash1 - None

    with pytest.raises(ValueError):
        _ = videohash1 - hash1[0:-2]

    with pytest.raises(TypeError):
        _ = videohash1 - ("XX" + hash1[2:])

    with pytest.raises(TypeError):
        _ = videohash1 - True

    videohash2 = VideoHash(path=video_path, frame_interval=3)
    hash2 = videohash2.hash
    hash_hex2 = videohash2.hash_hex
    assert hash2 == "0b1111100000101000111111111111101110111110010011010000001100000011"
    assert hash_hex2 == "0xf828fffbbe4d0303"

    videohash3 = VideoHash(path=video_path)
    hash3 = videohash3.hash
    hash_hex3 = videohash3.hash_hex
    assert hash3 == "0b0101100001010111111110101111101101000010010011100000001100000011"
    assert hash_hex3 == "0x5857fafb424e0303"

    assert hash1 == hash2
    assert videohash1.is_similar(videohash2)
    assert videohash1 == videohash2.bitlist

    assert hash_hex1 == hash_hex2
    assert videohash1 - hash_hex3 != 2

    assert videohash1 == videohash2
    assert videohash1 - videohash3 != 2

    videohash4 = VideoHash(path=video_path, download_worst=True)
    hash4 = videohash4.hash

    assert hash4 != hash1
    assert hash4 != hash2
    assert hash4 == hash3

    assert videohash1 != videohash4
    assert videohash2 != videohash4
    assert videohash3 == videohash4
    assert videohash3.is_similar(videohash4)

    with pytest.raises(ValueError):
        # not padded with 0x
        VideoHash.hex2bin("741fcfff8f780000", 64)

    with pytest.raises(ValueError):
        # not padded with 0b
        VideoHash.bin2hex("010101001")

    with pytest.raises(ValueError):
        # hamming distance not defined for unequal length bitlists
        _ = videohash1 - [1, 0, 1, 1, 1]

    class FakeVideoHashForTesting(VideoHash):
        def __init__(self, hash=None):
            self.hash = hash

    fake_videohash_object = FakeVideoHashForTesting(hash="0b0011010")
    fake_videohash_object.hamming_distance(string_a="0b1011010", string_b="0b1011010")

    fake_videohash_object = FakeVideoHashForTesting()
    with pytest.raises(ValueError):
        # hamming_distance is not defined.
        fake_videohash_object.hamming_distance(string_a="abc", string_b="abcd")

    with pytest.raises(ValueError):
        # hamming_distance is not defined.
        fake_videohash_object.hamming_distance(bitlist_a=[1, 0, 1, 1, 0], bitlist_b=[1, 0, 1, 1])

    with pytest.raises(DidNotSupplyPath):
        VideoHash(path=None)

    with pytest.raises(StoragePathDoesNotExist):
        storage_path = os.path.join(
            create_and_return_temporary_directory(),
            ("thisdirdoesnotexist" + os.path.sep),
        )
        VideoHash(path=video_path, storage_path=storage_path)

    with pytest.raises(ValueError):
        VideoHash(path=create_and_return_temporary_directory())

    with pytest.raises(ValueError):
        path = os.path.join(create_and_return_temporary_directory(), "file_extension_less_video")
        VideoHash(path=path)
