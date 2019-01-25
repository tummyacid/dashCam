from time import sleep
from http.server import BaseHTTPRequestHandler,HTTPServer
import shutil
from picamera import PiCamera
import sys

PORT_NUMBER = 9999
WAIT_TIME = 0.5
BASE_DIR = "/home/pi/timelapse"

def timelapse(interval):
    with PiCamera() as camera:
        camera.resolution = (3280, 2464)
        camera.exposure_mode = "antishake"
        camera.video_stabilization = True
        for filename in camera.capture_continuous(BASE_DIR + '/f{timestamp:%H%M%S%f}.jpg'):
            total, used, free = shutil.disk_usage(BASE_DIR)
            if (free < 10 ** 7):
                print("less than 10 MB of space left, quiting")
                sys.exit()
            sleep(interval)

class showPreview(BaseHTTPRequestHandler):
    def do_GET(self):
        try:    
            
            with PiCamera() as camera:
                camera.capture('/tmp/frame.jpg')
                f = open("/tmp/frame.jpg", 'rb')
                self.send_response(200)
                self.send_header('Content-type', 'image/jpg')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), showPreview)
    print('Started httpserver preview on port ' + str(PORT_NUMBER) )
    #TODO: handle more than one request, keep camera open, detect appropriate shutdown event
    server.handle_request()
    print('Stopped httpserver preview' )
    print('Starting time lapse at interval ' + str(WAIT_TIME) )
    timelapse(WAIT_TIME)

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
