"""
Set up a minimal HTTP Server to preview a Toasty-generated
tile pyramid
"""
import os
import sys
from time import time
try:
    from SimpleHTTPServer import SimpleHTTPRequestHandler, test
    from cStringIO import StringIO
except:  # python 3.X
    from http.server import SimpleHTTPRequestHandler, test
    from io import BytesIO

from . import gen_wtml


class SimpleWWTHandler(SimpleHTTPRequestHandler):

    def serve_string(self, contents):
        if sys.version_info.major == 2:
            return StringIO(contents)

        return BytesIO(contents.encode('UTF-8'))

    @property
    def wtml(self):
        if not hasattr(self, '_wtml'):
            base_dir = sys.argv[-1]
            depths = next(os.walk(base_dir))[1]
            max_depth = max(map(int, depths))
            self._wtml = gen_wtml(base_dir, max_depth)
        return self._wtml

    def send_head(self):
        if self.path == '/toasty.wtml':
            self.send_response(200)
            self.send_header("Content-type", 'text/xml')
            self.send_header("Content-Length", str(len(self.wtml)))
            self.send_header("Last-Modified",
                             self.date_time_string(int(time())))
            self.end_headers()
            return self.serve_string(self.wtml)

        if self.path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header("Content-type", 'text/html')
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Last-Modified",
                             self.date_time_string(int(time())))
            self.end_headers()
            return self.serve_string(html)

        return SimpleHTTPRequestHandler.send_head(self)


html = """
<html>
<head>
<title> Toasty Viewer </title>
<style type="text/css">
html, body {
height: 100%;
overflow: hidden;
}

body {
padding: 0;
margin: 0;
}

#canvas {
padding: 0;
margin: 0 0 0px 0;
}

#UI {
position: relative;
top: -40px;
left: 20px;
}

div {margin: 0 0 0px 0; padding: 0;}

</style>

<script src="http://www.worldwidetelescope.org/scripts/wwtsdk.aspx"></script>
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
</head>

<body onload="init();" onresize="resize_canvas();" style="background-color:#000000">
<script type="text/javascript">

function init() {
 wwt = wwtlib.WWTControl.initControl("WWTCanvas");
 wwt.add_ready(wwtReady);
 resize_canvas();
}

function resize_canvas() {
    div = document.getElementById("WWTCanvas");

    if (div.style.width != (window.innerWidth).toString() + "px") {
        div.style.width = (window.innerWidth).toString() + "px";
        }

    if (div.style.height != (window.innerHeight).toString() + "px") {
        div.style.height = ((window.innerHeight)).toString() + "px";
        }
}

function wwtReady() {
   wwt.settings.set_showCrosshairs(true);
   wwt.settings.set_showConstellationFigures(false);
   wwt.settings.set_showConstellationBoundries(false);
   wwt.loadImageCollection('/toasty.wtml');
   wwt.add_collectionLoaded(set_layers);
   $('#select-foreground').change(function(e){
      wwt.setBackgroundImageByName(this.value)
      });
   $('#opacity').change(function(e){
      wwt.setForegroundOpacity(this.value);
      });
}

function set_layers() {
   wwt.setBackgroundImageByName('Wise All Sky (Infrared)');
   wwt.setForegroundImageByName('Toasty map');
   wwt.setForegroundOpacity(50);
}
</script>

<div id="WWTCanvas" style="width: 750px; height: 750px; border-style: none; border-width: 0px;">
</div>
<div id="UI">

<select id="select-foreground">
<option value="Digitized Sky Survey (Color)"> Optical </option>
<option value="WMAP ILC 5-Year Cosmic Microwave Background"> WMAP 5-Year </option>
<option value="SFD Dust Map (Infrared)"> SFD </option>
<option value="IRIS: Improved Reprocessing of IRAS Survey (Infrared)"> IRIS </option>
<option value="Hydrogen Alpha Full Sky Map"> H-alpha </option>
</select>

<input id='opacity' type="range" name="opacity" min="10" max="100">

</div>
</body>
</html>
"""

if __name__ == "__main__":
    sys.argv.insert(1, '8000')
    test(HandlerClass=SimpleWWTHandler)
