import os
import sys
import re
import math
import time
import json
import glob
import urllib
import os.path
import tempfile
import commands
import StringIO
import subprocess
import PIL.Image
import PIL.ImageFilter
import matchup

class CodeReadException(Exception):
    pass

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Affine:
    def __init__(self, a=1, b=0, c=0, d=0, e=1, f=0):
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.d = float(d)
        self.e = float(e)
        self.f = float(f)

    def __str__(self):
        return str(((self.a, self.b, self.c), (self.d, self.e, self.f)))

    def __repr__(self):
        return str(self)

    def project(self, x, y):
        return self.a * x + self.b * y + self.c, self.d * x + self.e * y + self.f

    def multiply(self, o):
        return Affine(self.a * o.a + self.d * o.b, self.b * o.a + self.e * o.b, self.c * o.a + self.f * o.b + o.c,
                      self.a * o.d + self.d * o.e, self.b * o.d + self.e * o.e, self.c * o.d + self.f * o.e + o.f)

    def translate(self, dx, dy):
        return self.multiply(Affine(1, 0, dx, 0, 1, dy))

    def scale(self, sx, sy):
        return self.multiply(Affine(sx, 0, 0, 0, sy, 0))

    def rotate(self, theta):
        return self.multiply(Affine(math.cos(theta), -math.sin(theta), 0, math.sin(theta), math.cos(theta), 0))

class Marker:
    def __init__(self, basepath):
        data = open(basepath + '.sift', 'r')
        self.features = [matchup.row2feature(row) for row in data]

        point = open(basepath + '.txt', 'r')
        self.anchor = Point(*[int(c) for c in point.read().split()])

    def locateInFeatures(self, features):
        """
        """
        start = time.time()
        
        matches = matchup.find_matches(features, self.features)
        matches_graph = matchup.group_matches(matches, features, self.features)
        needles = matchup.find_needles(matches, matches_graph, features, self.features)
        
        print >> sys.stderr, 'Found', len(needles), 'needles',
        print >> sys.stderr, 'in %.2f sec.' % (time.time() - start)
        
        assert len(needles) == 1, 'Got %d needle matches instead of 1' % len(needles)
        fs1, fs2, transform = needles[0]
        
        print >> sys.stderr, (self.anchor.x, self.anchor.y),

        x, y = transform(self.anchor.x, self.anchor.y)
        print >> sys.stderr, '->', '(%.2f, %.2f)' % (x, y),

        self.anchor = Point(x, y)

def main(url, markers):
    """
    """
    try:
        image, features, scale = siftImage(url)
        
        for (name, marker) in markers.items():
            print >> sys.stderr, name, '...',
            marker.locateInFeatures(features)
    
            x, y = int(marker.anchor.x / scale), int(marker.anchor.y / scale)
            print >> sys.stderr, '->', (x, y)
    
            marker.anchor = Point(x, y)
        
        qrcode = extractCode(image, markers)
        qrcode.save('qrcode.jpg', 'JPEG')
        
        info = readCode(qrcode)
        
        for field in info:
            field['scan'] = '%(name)s-small.jpg' % field, '%(name)s-large.jpg' % field
            x, y = field['bbox'][0] - 6, field['bbox'][1] - 6
            w, h = field['bbox'][2] + 6 - x, field['bbox'][3] + 6 - y
            extractBox(image, markers, x, y, w, h, 1).save(field['scan'][0], 'JPEG')
            extractBox(image, markers, x, y, w, h, 3).save(field['scan'][1], 'JPEG')
    
        print >> sys.stdout, json.dumps(info, indent=2)
        
        return 0

    except CodeReadException:
        print >> sys.stderr, 'Failed QR code, maybe will try again?'
        return 1
    
    except KeyboardInterrupt:
        raise

    except:
        raise

def siftImage(url):
    """
    """
    print >> sys.stderr, 'download...',
    
    bytes = StringIO.StringIO(urllib.urlopen(url).read())
    image = PIL.Image.open(bytes).convert('RGBA')
    
    print >> sys.stderr, image.size
    
    handle, sift_filename = tempfile.mkstemp(prefix='decode-', suffix='.sift')
    os.close(handle)
        
    handle, pgm_filename = tempfile.mkstemp(prefix='decode-', suffix='.pgm')
    os.close(handle)
    
    # fit to 1000x1000
    scale = min(1., 1000. / max(image.size))
    
    # write the PGM
    pgm_size = int(image.size[0] * scale), int(image.size[1] * scale)
    image.convert('L').resize(pgm_size, PIL.Image.ANTIALIAS).save(pgm_filename)
    
    print >> sys.stderr, 'sift...', pgm_size,
    
    basedir = os.path.dirname(os.path.realpath(__file__)).replace(' ', '\ ')
    status, output = commands.getstatusoutput("%(basedir)s/bin/sift --peak-thresh=8 -o '%(sift_filename)s' '%(pgm_filename)s'" % locals())
    data = open(sift_filename, 'r')
    
    assert status == 0, 'Sift execution returned %s instead of 0' % status
    
    features = [matchup.row2feature(row) for row in data]

    print >> sys.stderr, len(features), 'features'
    
    os.unlink(sift_filename)
    os.unlink(pgm_filename)
    
    return image, features, scale

def linearSolution(r1, s1, t1, r2, s2, t2, r3, s3, t3):
    """ Solves a system of linear equations.

          t1 = (a * r1) + (b + s1) + c
          t2 = (a * r2) + (b + s2) + c
          t3 = (a * r3) + (b + s3) + c

        r1 - t3 are the known values.
        a, b, c are the unknowns to be solved.
        returns the a, b, c coefficients.
    """

    # make them all floats
    r1, s1, t1, r2, s2, t2, r3, s3, t3 = map(float, (r1, s1, t1, r2, s2, t2, r3, s3, t3))

    a = (((t2 - t3) * (s1 - s2)) - ((t1 - t2) * (s2 - s3))) \
      / (((r2 - r3) * (s1 - s2)) - ((r1 - r2) * (s2 - s3)))

    b = (((t2 - t3) * (r1 - r2)) - ((t1 - t2) * (r2 - r3))) \
      / (((s2 - s3) * (r1 - r2)) - ((s1 - s2) * (r2 - r3)))

    c = t1 - (r1 * a) - (s1 * b)
    
    return a, b, c

def extractBox(image, markers, x, y, width, height, magnify):
    """
    """
    top = markers['GMDH02_00364']
    bottom = markers['GMDH02_00647']
    
    theta = math.atan2(bottom.anchor.x - top.anchor.x, bottom.anchor.y - top.anchor.y) * -1
    scale = math.hypot(bottom.anchor.x - top.anchor.x, bottom.anchor.y - top.anchor.y) / (756 - 36)
    
    # a transformation matrix from print space (points) to scan space (pixels)
    matrix = Affine().translate(-36, -36).scale(scale, scale).rotate(theta).translate(top.anchor.x, top.anchor.y)
    
    top_left = matrix.project(x, y)
    top_right = matrix.project(x + width, y)
    bottom_left = matrix.project(x, y + height)

    # projection from extracted QR code image space to source image space
    
    w, h = width * magnify, height * magnify
    
    ax, bx, cx = linearSolution(0, 0, top_left[0],
                                w, 0, top_right[0],
                                0, h, bottom_left[0])
    
    ay, by, cy = linearSolution(0, 0, top_left[1],
                                w, 0, top_right[1],
                                0, h, bottom_left[1])

    return image.convert('RGBA').transform((w, h), PIL.Image.AFFINE, (ax, bx, cx, ay, by, cy), PIL.Image.BICUBIC)

def extractCode(image, markers):
    """
    """
    # extract the code part
    justcode = extractBox(image, markers, 504-18, 684-18, 108, 108, 5)
    
    # paste it to an output image
    qrcode = PIL.Image.new('RGB', justcode.size, (0xCC, 0xCC, 0xCC))
    qrcode.paste(justcode, (0, 0), justcode)
    
    return qrcode
    
    # raise contrast
    lut = [0x00] * 112 + [0xFF] * 144 # [0x00] * 112 + range(0x00, 0xFF, 8) + [0xFF] * 112
    qrcode = qrcode.convert('L').filter(PIL.ImageFilter.BLUR).point(lut)
    
    return qrcode

def readCode(image):
    """
    """
    decode = 'java', '-classpath', ':'.join(glob.glob('lib/*.jar')), 'qrdecode'
    decode = subprocess.Popen(decode, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    
    image.save(decode.stdin, 'PNG')
    decode.stdin.close()
    decode.wait()
    
    decoded = decode.stdout.read().strip()
    print >> sys.stderr, decoded
    
    if decoded.startswith('http://'):
        return json.load(urllib.urlopen(decoded))

    else:
        raise CodeReadException('Attempt to read QR code failed')

if __name__ == '__main__':
    scan_url = sys.argv[1]
    markers = {}
    
    for basename in ('GMDH02_00364', 'GMDH02_00647'):
        basepath = os.path.dirname(os.path.realpath(__file__)) + '/' + basename
        markers[basename] = Marker(basepath)
    
    sys.exit(main(scan_url, markers))
