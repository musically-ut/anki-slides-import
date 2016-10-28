from wand.image import Image
import unittest

class PdfPages:
    def __init__(self, pdfFileName, resolution=(120, 120)):
        self.pdf = Image(filename=pdfFileName, resolution=resolution)

    def getPageAsPng(self, pageNumber, width=640):
        """Return the given page as a png wand.image.Image."""
        # The page numbers are indexed with base 0, while page numbers start
        # from 1.
        img = Image(image = self.pdf.sequence[pageNumber - 1])
        img.resize(width, int(width * img.height / (1.0 * img.width)))
        return img.convert('png')
    
    def getCroppedPageAsPng(self, pageNumber, cropPercentValues, width=640):
        """Return the given page as a cropped png wand.image.Image."""
        # The page numbers are indexed with base 0, while page numbers start
        # from 1.
        img = Image(image = self.pdf.sequence[pageNumber - 1])
        img.resize(width, int(width * img.height / (1.0 * img.width)))
        wmin = int((cropPercentValues[0][0] / 100.0) * img.width)
        wmax = int((cropPercentValues[0][1] / 100.0) * img.width)
        hmin = int((cropPercentValues[1][0] / 100.0) * img.height)
        hmax = int((cropPercentValues[1][1] / 100.0) * img.height)
        return img[wmin:wmax, hmin:hmax].convert('png')


class TestPdfPages(unittest.TestCase):
    def testOnVegFoodInJapan(self):
        p = PdfPages('./slidesimport/test/Veg-food-in-Japan.pdf')
        slide12 = Image(filename='./slidesimport/test/slide-12.png')
        self.assertEqual(p.getPageAsPng(12), slide12)

