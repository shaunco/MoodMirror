# from https://stackoverflow.com/questions/5524179/how-to-detect-motion-between-two-pil-images-wxpython-webcam-integration-exampl
import math, sys, numpy as np
import PIL.Image, PIL.ImageChops

sys.modules["Image"]      = PIL.Image
sys.modules["ImageChops"] = PIL.ImageChops

#from scipy.misc   import imread
#from scipy.linalg import norm
#from scipy        import sum, average


DEFAULT_DEVICE_WIDTH  = 640
DEFAULT_DEVICE_HEIGHT = 480

"""
class Images:

    def __init__(self, image1, image2, threshold=98, grayscale=True):
        if type(image1) == str:
            self.image1 = sys.modules["Image"].open(image1)
            self.image2 = sys.modules["Image"].open(image2)
        if grayscale:
            self.image1 = self.DoGrayscale(imread(image1).astype(float))
            self.image2 = self.DoGrayscale(imread(image2).astype(float))
        else:
            self.image1    = imread(image1).astype(float)
            self.image2    = imread(image2).astype(float)
        self.threshold = threshold

    def DoComparison(self, image1=None, image2=None):
        if image1: image1 = self.Normalize(image1)
        else:      image1 = self.Normalize(self.image1)
        if image2: image2 = self.Normalize(image2)
        else:      image2 = self.Normalize(self.image2)
        diff = image1 - image2
        m_norm = sum(abs(diff))
        z_norm = norm(diff.ravel(), 0)
        return (m_norm, z_norm)

    def DoGrayscale(self, arr):
        if len(arr.shape) == 3:
            return average(arr, -1)
        else:
            return arr

    def Normalize(self, arr):
        rng = arr.max()-arr.min()
        amin = arr.min()
        return (arr-amin)*255/rng
"""

class Images2:

    def __init__(self, image1, image2, threshold=98, grayscale=True):
        self.image1 = image1
        if type(image1) == str:
            self.image1 = sys.modules["Image"].open(self.image1)
        self.image2 = image2
        if type(image2) == str:
            self.image2 = sys.modules["Image"].open(image2)
        self.threshold = threshold

    def DoComparison(self, image1=None, image2=None):
        if not image1: image1 = self.image1
        if not image2: image2 = self.image2
        diffs = sys.modules["ImageChops"].difference(image1, image2)
        return self.ImageEntropy(diffs)

    def ImageEntropy(self, image):
        w,h = image.size
        a = np.array(image.convert('RGB')).reshape((w*h,3))
        h,e = np.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)
        prob = h/np.sum(h) # normalize
        prob = prob[prob>0] # remove zeros
        return -np.sum(prob*np.log2(prob))


    def OldImageEntropy(self, image):
        histogram   = image.histogram()
        histlength  = sum(histogram)
        probability = [float(h) / histlength for h in histogram]
        return -sum([p * math.log(p, 2) for p in probability if p != 0])



class Images3:

    def __init__(self, image1, image2, threshold=8):
        self.image1 = image1
        if type(image1) == str:
            self.image1 = sys.modules["Image"].open(self.image1)
        self.image2 = image2
        if type(image2) == str:
            self.image2 = sys.modules["Image"].open(image2)
        self.threshold = threshold

    def DoComparison(self, image1=None, image2=None):
        if not image1: image1 = self.image1
        if not image2: image2 = self.image2
        image = image1
        monoimage1 = image1.convert("P", palette=sys.modules["Image"].ADAPTIVE, colors=2)
        monoimage2 = image2.convert("P", palette=sys.modules["Image"].ADAPTIVE, colors=2)
        imgdata1   = monoimage1.getdata()
        imgdata2   = monoimage2.getdata()

        changed = 0
        i = 0
        acc = 3

        while i < DEFAULT_DEVICE_WIDTH * DEFAULT_DEVICE_HEIGHT:
            now  = imgdata1[i]
            prev = imgdata2[i]
            if now != prev:
                x = (i % DEFAULT_DEVICE_WIDTH)
                y = (i / DEFAULT_DEVICE_HEIGHT)
                try:
                    #if self.view == "normal":
                    image.putpixel((x,y), (0,0,256))
                    #else:
                    #    monoimage.putpixel((x,y), (0,0,256))
                except:
                    pass
                changed += 1
            i += 1
        percchange = float(changed) / float(DEFAULT_DEVICE_WIDTH * DEFAULT_DEVICE_HEIGHT)
        return percchange