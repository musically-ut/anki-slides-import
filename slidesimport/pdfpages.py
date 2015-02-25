from wand.image import Image
import unittest

class PdfPages:
    def __init__(self, pdfFileName, resolution=(120, 120)):
        self.pdf = Image(filename=pdfFileName, resolution=resolution)

    def getPageAsPng(self, pageNumber, width=640):
        """Return the given page as a pdf wand.image.Image."""
        # The page numbers are indexed with base 0, while page numbers start
        # from 1.
        img = Image(image = self.pdf.sequence[pageNumber - 1])
        img.resize(width, long(width * img.height / (1.0 * img.width)))
        return img.convert('png')


class TestPdfPages(unittest.TestCase):
    def testOnVegFoodInJapan(self):
        p = PdfPages('./slidesimport/test/Veg-food-in-Japan.pdf')
        slide12 = Image(filename='./slidesimport/test/slide-12.png')
        self.assertEqual(p.getPageAsPng(12), slide12)

