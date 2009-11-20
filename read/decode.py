import os
import sys
import re
import math
import time
import glob
import array
import urllib
import os.path
import httplib
import urlparse
import tempfile
import commands
import StringIO
import mimetypes
import subprocess
import xml.etree.ElementTree
import PIL.Image
import PIL.ImageFilter
import matchup

class CodeReadException(Exception):
    pass

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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
        
        return 0
        
        # reading QR code
        updateStepLocal(4, 10)
        
        qrcode = extractCode(image, markers)

        qrcode_name = 'qrcode.jpg'
        qrcode_bytes = StringIO.StringIO()
        qrcode_image = qrcode.copy()
        qrcode_image.save(qrcode_bytes, 'JPEG')
        qrcode_bytes = qrcode_bytes.getvalue()
        appendScanFile(scan_id, qrcode_name, qrcode_bytes, apibase, password)
    
        print_id, north, west, south, east = readCode(qrcode)
        print 'code contents:', 'Print', print_id, (north, west, south, east)
        
        # tiling and uploading
        updateStepLocal(5, 180)

        gym = ModestMaps.OpenStreetMap.Provider()
        
        topleft = gym.locationCoordinate(ModestMaps.Geo.Location(north, west))
        bottomright = gym.locationCoordinate(ModestMaps.Geo.Location(south, east))
        
        print 'coordinates:', topleft, bottomright
        
        # make a geotiff and worldfile
        warped_bytes, world_bytes = createGeoTIFF(image, gym, topleft, bottomright, markers, gdaldir)
        appendScanFile(scan_id, 'utm.tif', warped_bytes, apibase, password)
        appendScanFile(scan_id, 'utm.tfw', world_bytes, apibase, password)
        
        # make a smallish preview image
        preview_name = 'preview.jpg'
        preview_bytes = StringIO.StringIO()
        preview_image = image.copy()
        preview_image.thumbnail((409, 280), PIL.Image.ANTIALIAS)
        preview_image.save(preview_bytes, 'JPEG')
        preview_bytes = preview_bytes.getvalue()
        appendScanFile(scan_id, preview_name, preview_bytes, apibase, password)
        
        # make a largish image
        large_name = 'large.jpg'
        large_bytes = StringIO.StringIO()
        large_image = image.copy()
        large_image.thumbnail((900, 900), PIL.Image.ANTIALIAS)
        large_image.save(large_bytes, 'JPEG')
        large_bytes = large_bytes.getvalue()
        appendScanFile(scan_id, large_name, large_bytes, apibase, password)
        
        renders = {}
        
        min_zoom, max_zoom = 20, 0
        
        for zoom in range(20, 0, -1):
            localTopLeft = topleft.zoomTo(zoom)
            localBottomRight = bottomright.zoomTo(zoom)

            zoom_renders = tileZoomLevel(image, localTopLeft, localBottomRight, markers, renders)
            
            for (coord, tile_image) in zoom_renders:
                x, y, z = coord.column, coord.row, coord.zoom
                tile_name = '%(z)d/%(x)d/%(y)d.jpg' % locals()
                
                tile_bytes = StringIO.StringIO()
                tile_image.save(tile_bytes, 'JPEG')
                tile_bytes = tile_bytes.getvalue()

                appendScanFile(scan_id, tile_name, tile_bytes, apibase, password)
            
                renders[str(coord)] = tile_image
                
                min_zoom = min(coord.zoom, min_zoom)
                max_zoom = max(coord.zoom, max_zoom)
        
        print 'min:', topleft.zoomTo(min_zoom)
        print 'max:', bottomright.zoomTo(max_zoom)
        
        # finished!
        updateScan(apibase, password, scan_id, print_id, topleft.zoomTo(min_zoom), bottomright.zoomTo(max_zoom))
        updateStepLocal(6, None)

    except CodeReadException:
        print 'Failed QR code, maybe will try again?'
        updateStepLocal(98, 10)
    
    except KeyboardInterrupt:
        raise

    except:
        # an error
        updateStepLocal(99, 90)

        raise

    return 0

def appendScanFile(scan_id, file_path, file_contents, apibase, password):
    """ Upload a file via the API append.php form input provision thingie.
    """

    s, host, path, p, q, f = urlparse.urlparse(apibase)
    
    query = urllib.urlencode({'scan': scan_id, 'password': password, 'dirname': os.path.dirname(file_path)})
    
    req = httplib.HTTPConnection(host, 80)
    req.request('GET', path + '/append.php?' + query)
    res = req.getresponse()
    
    html = xml.etree.ElementTree.parse(res)
    
    for form in html.findall('*/form'):
        form_action = form.attrib['action']
        
        inputs = form.findall('.//input')
        
        file_inputs = [input for input in inputs if input.attrib['type'] == 'file']
        
        fields = [(input.attrib['name'], input.attrib['value'])
                  for input in inputs
                  if input.attrib['type'] != 'file' and 'name' in input.attrib]
        
        files = [(input.attrib['name'], os.path.basename(file_path), file_contents)
                 for input in inputs
                 if input.attrib['type'] == 'file']

        if len(files) == 1:
            post_type, post_body = encodeMultipartFormdata(fields, files)
            
            s, host, path, p, query, f = urlparse.urlparse(urlparse.urljoin(apibase, form_action))
            
            req = httplib.HTTPConnection(host, 80)
            req.request('POST', path+'?'+query, post_body, {'Content-Type': post_type, 'Content-Length': str(len(post_body))})
            res = req.getresponse()
            
            assert res.status in range(200, 308), 'POST of file to %s resulting in status %s instead of 2XX/3XX' % (host, res.status)

            return True
        
    raise Exception('Did not find a form with a file input, why is that?')

def createGeoTIFF(image, provider, topleft, bottomright, markers, gdaldir):
    """
    """
    coordinatePoint, pointCoordinate, magnification = coordinatePointTransforms(topleft, bottomright, markers)

    ul = pointCoordinate(ModestMaps.Core.Point(0, 0))
    lr = pointCoordinate(ModestMaps.Core.Point(*image.size))
    
    diameter = math.pow(2, topleft.zoom)
    earth = 6378137
    scale = diameter / (earth * math.pi * 2)
    utm_zone = round((provider.coordinateLocation(ul).lon + 183) / 6)
    
    ulx, uly = ul.column - diameter/2, diameter/2 - ul.row
    lrx, lry = lr.column - diameter/2, diameter/2 - lr.row
    
    print 'utm zone %(utm_zone)d, ullr:' % locals(), (ulx, uly, lrx, lry)
    
    handle, image_file = tempfile.mkstemp('.jpg', 'decode-geotiff-')
    image.save(image_file, 'JPEG')
    os.close(handle)
    
    handle, virtual_file = tempfile.mkstemp('.vrt', 'decode-geotiff-')
    os.close(handle)
    
    handle, warped_file = tempfile.mkstemp('.tif', 'decode-geotiff-')
    world_file = warped_file[:-4] + '.tfw'
    os.close(handle)
    
    cmd = gdaldir.rstrip('/')+'/gdal_translate', '-of', 'VRT', '-a_srs', '+proj=merc +lon_0=0 +k=%(scale).12f +x_0=0 +y_0=0 +a=%(earth)d +b=%(earth)d +towgs84=0,0,0,0,0,0,0 +units=m +no_defs' % locals(), '-a_ullr', str(ulx), str(uly), str(lrx), str(lry), image_file, virtual_file
    translate = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    translate.wait()
    
    cmd = gdaldir.rstrip('/')+'/gdalwarp', '-of', 'GTIFF', '-t_srs', '+proj=utm +zone=%(utm_zone)d' % locals(), '-dstnodata', '204', '-co', 'COMPRESS=JPEG', '-co', 'TFW=YES', virtual_file, warped_file
    warp = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    warp.wait()

    warped_bytes = open(warped_file, 'r').read()
    world_bytes = open(world_file, 'r').read()
    
    os.unlink(image_file)
    os.unlink(virtual_file)
    os.unlink(warped_file)
    os.unlink(world_file)
    
    return warped_bytes, world_bytes

def encodeMultipartFormdata(fields, files):
    """ fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        
        Adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
    """
    BOUNDARY = '----------multipart-boundary-multipart-boundary-multipart-boundary$'
    CRLF = '\r\n'

    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    bytes = array.array('c')

    for (key, value) in fields:
        bytes.fromstring('--' + BOUNDARY + CRLF)
        bytes.fromstring('Content-Disposition: form-data; name="%s"' % key + CRLF)
        bytes.fromstring(CRLF)
        bytes.fromstring(value + CRLF)

    for (key, filename, value) in files:
        bytes.fromstring('--' + BOUNDARY + CRLF)
        bytes.fromstring('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename) + CRLF)
        bytes.fromstring('Content-Type: %s' % (mimetypes.guess_type(filename)[0] or 'application/octet-stream') + CRLF)
        bytes.fromstring(CRLF)
        bytes.fromstring(value + CRLF)

    bytes.fromstring('--' + BOUNDARY + '--' + CRLF)

    return content_type, bytes.tostring()

def updateStep(apibase, password, scan_id, step_number, message_id, timeout):
    """
    """
    s, host, path, p, q, f = urlparse.urlparse(apibase)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    params = urllib.urlencode({'scan': scan_id, 'step': step_number, 'password': password})
    
    req = httplib.HTTPConnection(host, 80)
    req.request('POST', path + '/step.php', params, headers)
    res = req.getresponse()
    
    assert res.status == 200, 'POST to step.php %s/%d resulting in status %s instead of 200' % (scan_id, step_number, res.status)
    
    # TODO: move this responsibility to step.php
    if step_number == 6 or res.read().strip() == 'Too many errors':
        # magic number for "finished"
        params = urllib.urlencode({'id': message_id, 'password': password, 'delete': 'yes'})

    else:
        params = urllib.urlencode({'id': message_id, 'password': password, 'timeout': timeout})
    
    req = httplib.HTTPConnection(host, 80)
    req.request('POST', path + '/dequeue.php', params, headers)
    res = req.getresponse()
    
    assert res.status == 200, 'POST to dequeue.php resulting in status %s instead of 200' % res.status
    
    return

def updateScan(apibase, password, scan_id, print_id, min_coord, max_coord):
    """
    """
    s, host, path, p, q, f = urlparse.urlparse(apibase)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    query = urllib.urlencode({'id': scan_id})
    params = urllib.urlencode({'print_id': print_id,
                               'password': password,
                               'min_row': min_coord.row, 'max_row': max_coord.row,
                               'min_column': min_coord.column, 'max_column': max_coord.column,
                               'min_zoom': min_coord.zoom, 'max_zoom': max_coord.zoom})
    
    req = httplib.HTTPConnection(host, 80)
    req.request('POST', path + '/scan.php?' + query, params, headers)
    res = req.getresponse()
    
    assert res.status == 200, 'POST to scan.php resulting in status %s instead of 200' % res.status

    return

def coordinatePointTransforms(topleft, bottomright, markers):
    """ Get transform functions coordinatePoint and pointCoordinate
    """
    assert topleft.zoom == bottomright.zoom, "Top-left and bottom-right zooms don't match up as they should: %s vs. %s" % (topleft.zoom, bottomright.zoom)
    
    zoom = topleft.zoom
    
    # transformation from coordinate space to pixel space
    
    top, left, bottom, right = topleft.row, topleft.column, bottomright.row, bottomright.column
    
    assert top < bottom, 'Top is not less-than bottom as it should be: %.2f vs. %.2f' % (top, bottom)
    assert left < right, 'Left is not less-than right as it should be: %.2f vs. %.2f' % (left, right)
    
    ax1, bx1, cx1 = linearSolution(left,    top, markers['Header'].anchor.x,
                                   right,   top, markers['Hand'].anchor.x,
                                   left, bottom, markers['CCBYSA'].anchor.x)
    
    ay1, by1, cy1 = linearSolution(left,    top, markers['Header'].anchor.y,
                                   right,   top, markers['Hand'].anchor.y,
                                   left, bottom, markers['CCBYSA'].anchor.y)

    magnification = math.hypot(ax1, bx1) / 256

    coordinatePoint = lambda c: ModestMaps.Core.Point(ax1 * c.column + bx1 * c.row + cx1, ay1 * c.column + by1 * c.row + cy1)
    
    ax2, bx2, cx2 = linearSolution(markers['Header'].anchor.x, markers['Header'].anchor.y, left,
                                   markers['Hand'].anchor.x,   markers['Hand'].anchor.y,   right,
                                   markers['CCBYSA'].anchor.x, markers['CCBYSA'].anchor.y, left)
    
    ay2, by2, cy2 = linearSolution(markers['Header'].anchor.x, markers['Header'].anchor.y, top,
                                   markers['Hand'].anchor.x,   markers['Hand'].anchor.y,   top,
                                   markers['CCBYSA'].anchor.x, markers['CCBYSA'].anchor.y, bottom)

    pointCoordinate = lambda p: ModestMaps.Core.Coordinate(ay2 * p.x + by2 * p.y + cy2, ax2 * p.x + bx2 * p.y + cx2, zoom)
    
    return coordinatePoint, pointCoordinate, magnification

def tileZoomLevel(image, topleft, bottomright, markers, renders):
    """ Generator of coord, tile tuples
    """
    coordinatePoint, pointCoordinate, magnification = coordinatePointTransforms(topleft, bottomright, markers)

    zoom = topleft.zoom
    
    if .65 < magnification and magnification < 20:
    
        print >> sys.stderr, zoom,
        
        for row in range(int(topleft.container().row), int(bottomright.container().row) + 1):
            for column in range(int(topleft.container().column), int(bottomright.container().column) + 1):
                coord = ModestMaps.Core.Coordinate(row, column, zoom)
                
                # the tile image itself
                tile_img = extractTile(image, coord, coordinatePoint, renders)
                yield (coord, tile_img)

                print >> sys.stderr, '.',

        print >> sys.stderr, ''

def extractTile(image, coord, coordinatePoint, renders):
    """
    """
    topleft = coordinatePoint(coord)
    topright = coordinatePoint(coord.right())
    bottomleft = coordinatePoint(coord.down())
    
    # transformation from tile image space to pixel space
    axt, bxt, cxt = linearSolution(0, 0, topleft.x, 512, 0, topright.x, 0, 512, bottomleft.x)
    ayt, byt, cyt = linearSolution(0, 0, topleft.y, 512, 0, topright.y, 0, 512, bottomleft.y)
    
    # pull the original pixels out
    tile_pixels = image.transform((512, 512), PIL.Image.AFFINE, (axt, bxt, cxt, ayt, byt, cyt), PIL.Image.BICUBIC)
    tile_img = PIL.Image.new('L', tile_pixels.size, 0xCC).convert('RGB')
    tile_img.paste(tile_pixels, (0, 0), tile_pixels)

    # interpolate in some of the previous renders; these may look better
    for (x, y, c) in ((0, 0, coord.zoomBy(1)), (256, 0, coord.zoomBy(1).right()), (0, 256, coord.zoomBy(1).down()), (256, 256, coord.zoomBy(1).down().right())):
        if renders.has_key(str(c)):
            tile_img.paste(renders[str(c)], (x, y))

    tile_img = tile_img.resize((256, 256), PIL.Image.ANTIALIAS)
    
    return tile_img

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

def extractCode(image, markers):
    """
    """
    # transformation from ideal space to printed image space.
    # markers are positioned with Header at upper left, Hand at upper right, and CCBYSA at lower left
    
    distance_across = math.hypot(markers['Hand'].anchor.x - markers['Header'].anchor.x, markers['Hand'].anchor.y - markers['Header'].anchor.y)
    distance_down = math.hypot(markers['CCBYSA'].anchor.x - markers['Header'].anchor.x, markers['CCBYSA'].anchor.y - markers['Header'].anchor.y)
    aspect = distance_across / distance_down
    orientation = aspect > 1 and 'landscape' or 'portrait'
    
    print >> sys.stderr, 'aspect', aspect, 'orientation', orientation
    
    right = orientation == 'portrait' and 540 or 720
    bottom = orientation == 'portrait' and 720 or 540
    
    ax, bx, cx = linearSolution(0,      0, markers['Header'].anchor.x,
                                right,  0, markers['Hand'].anchor.x,
                                0, bottom, markers['CCBYSA'].anchor.x)
    
    ay, by, cy = linearSolution(0,      0, markers['Header'].anchor.y,
                                right,  0, markers['Hand'].anchor.y,
                                0, bottom, markers['CCBYSA'].anchor.y)
    
    # candidate location of the QR code on the printed image:
    # top-left, top-right, bottom-left corner of QR code.
    xys = [(right - 63, bottom - 63), (right, bottom - 63), (right - 63, bottom)]

    corners = [Point(ax * x + bx * y + cx, ay * x + by * y + cy)
               for (x, y) in xys]

    # projection from extracted QR code image space to source image space
    
    ax, bx, cx = linearSolution(50,  50, corners[0].x,
                                450, 50, corners[1].x,
                                50, 450, corners[2].x)
    
    ay, by, cy = linearSolution(50,  50, corners[0].y,
                                450, 50, corners[1].y,
                                50, 450, corners[2].y)

    # extract the code part
    justcode = image.convert('RGBA').transform((500, 500), PIL.Image.AFFINE, (ax, bx, cx, ay, by, cy), PIL.Image.BICUBIC)
    
    # paste it to an output image
    qrcode = PIL.Image.new('RGB', justcode.size, (0xCC, 0xCC, 0xCC))
    qrcode.paste(justcode, (0, 0), justcode)
    
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
    print decoded
    
    if decoded.startswith('http://'):
    
        html = xml.etree.ElementTree.parse(urllib.urlopen(decoded))
        
        print_id, north, west, south, east = None, None, None, None, None
        
        for span in html.findall('body/span'):
            if span.get('id') == 'print-info':
                for subspan in span.findall('span'):
                    if subspan.get('class') == 'print':
                        print_id = subspan.text
                    elif subspan.get('class') == 'north':
                        north = float(subspan.text)
                    elif subspan.get('class') == 'south':
                        south = float(subspan.text)
                    elif subspan.get('class') == 'east':
                        east = float(subspan.text)
                    elif subspan.get('class') == 'west':
                        west = float(subspan.text)
    
        return print_id, north, west, south, east

    else:
        #image.show()

        raise CodeReadException('Attempt to read QR code failed')

if __name__ == '__main__':
    url = sys.argv[1]
    markers = {}
    
    for basename in ('GMDH02_00364', 'GMDH02_00647'):
        basepath = os.path.dirname(os.path.realpath(__file__)) + '/' + basename
        markers[basename] = Marker(basepath)
    
    sys.exit(main(url, markers))
