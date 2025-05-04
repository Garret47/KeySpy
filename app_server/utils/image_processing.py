import logging
import struct
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


class ImageFromBytesXServer:
    HEADER_SIZE = 12

    def __init__(self, data: bytes):
        self.width, self.height, self.bpp = struct.unpack("!III", data[:self.HEADER_SIZE])
        logger.debug(f"Extracted dimensions: {self.width}x{self.height}, bpp: {self.bpp}")
        self.mode = "RGB" if self.bpp == 24 else "RGBA"
        logger.debug(f"Determined image mode: '{self.mode}' based on bpp value")
        self.image = self._decode(data[self.HEADER_SIZE:])
        logger.info("Image created successfully from byte data")

    def _decode(self, data_image: bytes):
        img = Image.frombytes(self.mode, (self.width, self.height), data_image)
        rgb = img.split()
        return Image.merge(self.mode, (rgb[2], rgb[1], rgb[0], *rgb[3:]))


class TkImage:
    @staticmethod
    def from_image(img: Image, size: tuple):
        logger.debug(f"Preparing Tkinter-compatible image. Target preview size: {size}")
        resized = img.copy()
        resized.thumbnail(size)
        return ImageTk.PhotoImage(resized)


class ImageManagerX(ImageFromBytesXServer, TkImage):

    def __init__(self, data: bytes, size: tuple):
        super().__init__(data)
        self.tk_image = TkImage.from_image(self.image, size)

    def save(self, filename: str):
        try:
            self.image.save(filename)
            logger.info(f"Screenshot successfully saved to: {filename}")
        except Exception as e:
            logger.warning(f"Failed to save screenshot: {e}")