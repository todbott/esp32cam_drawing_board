import binascii
import camera
import time
import network
import uos
import machine


import socket

class CameraController:

    def __init__(self) -> None:


        # Here is the LAN thing
        self.sta = network.WLAN(network.STA_IF)

        # And here's the socket
        self.s = None

    def __connectToWiFiAndMakeSocketConnection(self):
        self.sta.active(True)
        self.sta.connect("IODATA-cdbc80-2G", "8186896622346")

        while self.sta.isconnected() == False:
            time.sleep(2)

        time.sleep(1)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('',80)) # specifies that the socket is reachable by any address the machine has available
        self.s.listen(5)     # max of 5 socket connections
        print(self.sta.ifconfig()[0])

    def takePhotoAndSend(self):

        camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)


        ## Other settings:
        # flip up side down
        camera.flip(1)
        # left / right
        camera.mirror(1)

        # framesize
        camera.framesize(camera.FRAME_VGA)
        # The options are the following:
        # FRAME_96X96 FRAME_QQVGA FRAME_QCIF FRAME_HQVGA FRAME_240X240
        # FRAME_QVGA FRAME_CIF FRAME_HVGA FRAME_VGA FRAME_SVGA
        # FRAME_XGA FRAME_HD FRAME_SXGA FRAME_UXGA FRAME_FHD
        # FRAME_P_HD FRAME_P_3MP FRAME_QXGA FRAME_QHD FRAME_WQXGA
        # FRAME_P_FHD FRAME_QSXGA
        # Check this link for more information: https://bit.ly/2YOzizz

        # special effects
        camera.speffect(camera.EFFECT_NONE)
        # The options are the following:
        # EFFECT_NONE (default) EFFECT_NEG EFFECT_BW EFFECT_RED EFFECT_GREEN EFFECT_BLUE EFFECT_RETRO

        # white balance
        camera.whitebalance(camera.WB_NONE)
        # The options are the following:
        # WB_NONE (default) WB_SUNNY WB_CLOUDY WB_OFFICE WB_HOME

        # saturation
        camera.saturation(0)
        # -2,2 (default 0). -2 grayscale 

        # brightness
        camera.brightness(0)
        # -2,2 (default 0). 2 brightness

        # contrast
        camera.contrast(0)
        #-2,2 (default 0). 2 highcontrast

        # quality
        camera.quality(10)
        # 10-63 lower number means higher quality


        uos.mount(machine.SDCard(), "/sd")


        while True:

            conn, addr = self.s.accept()

            request=conn.recv(1024)
            
            # Socket send()
            request = str(request)
            update = request.find('/update')
            print(request)

            if update > -1:
                response = f" {str(binascii.b2a_base64(camera.capture()))[2:-3]}"
            else:
                response = open("cam.html", "r").read().replace(" {", "{{").replace(" }", "}}").format(b = f" {str(binascii.b2a_base64(camera.capture()))[2:-3]}")

            # Create a socket reply, and actually send the response
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')      
            
          
            conn.sendall(response)
        
            # Socket close()
            conn.close()



cc = CameraController()

cc.__connectToWiFiAndMakeSocketConnection()
cc.takePhotoAndSend()