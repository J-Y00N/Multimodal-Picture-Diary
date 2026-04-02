from PIL import Image

from picture_diary.multimodal.reference_image import prepare_reference_image


def test_prepare_reference_image_resizes_to_requested_shape() -> None:
    image = Image.new("RGB", (1024, 768), color="white")
    prepared = prepare_reference_image(image, width=768, height=512)
    assert prepared.size == (768, 512)


def test_prepare_reference_image_snaps_to_multiple_of_eight() -> None:
    image = Image.new("RGB", (999, 777), color="white")
    prepared = prepare_reference_image(image, width=515, height=513)
    assert prepared.size == (512, 512)
