

# A VOIR https://stackoverflow.com/questions/37749378/integrate-opencv-webcam-into-a-kivy-user-interface

from jnius import autoclass
from time import sleep
from kivy.app import App
import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.utils import platform
from jnius import autoclass
from oscpy.server import OSCThreadServer
from oscpy.client import OSCClient

package_name = 'aaaa'
package_domain = 'org.test'
service_name = 'myservice'

service_class = '{}.{}.Service{}'.format(package_domain, package_name, service_name.title())

osc = None

class CameraExample(App):

    def start_osc(self):
        global osc
        def callback(*values):
            print("<<<<<<>>>>>>  got values: {}".format(values))

        print("STARTING OSC SERVER>>>>>>>>>>>>>>>>>")
        osc = OSCThreadServer()
        sock = osc.listen(address='0.0.0.0', port=8888, default=True)
        osc.bind(b'/address', callback)


    def build(self):
        self.start_osc()

        Environment = autoclass('android.os.Environment')
        sdpath = Environment.getExternalStorageDirectory()
        print(">>>>>>>>>>", repr(sdpath))

        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA, Permission.RECORD_AUDIO, Permission.WRITE_EXTERNAL_STORAGE])
        
        layout = BoxLayout(orientation='vertical')

        # Create a button for taking photograph
        self.camaraClick = Button(text="START")
        self.camaraClick.size_hint=(.5, .2)
        self.camaraClick.pos_hint={'x': .25, 'y':.75}
        self.camaraClick.bind(on_press=self.onCameraClick)
        layout.add_widget(self.camaraClick)

        self.camaraDeclick = Button(text="STOP")
        self.camaraDeclick.size_hint=(.5, .2)
        self.camaraDeclick.pos_hint={'x': .25, 'y':.75}
        self.camaraDeclick.bind(on_press=self.onCameraDeclick)
  
        layout.add_widget(self.camaraDeclick)

        # return the root widget

        return layout

    def on_pause(self):
        print ("<<<<<<<<<<<<<<<<<<<<<<<<< ON PAUSE")
        return True

    def on_resume(self):
        print ("<<<<<<<<<<<<<<<<<<<<<<<<< ON RESUME")

    def on_start(self):
        print ("<<<<<<<<<<<<<<<<<<<<<<<<< ON START")

    def on_stop(self):
        print ("<<<<<<<<<<<<<<<<<<<<<<<<< ON STOP")
    

    # Take the current frame of the video as the photo graph       

    def start_service(self):
        #from plyer import notification
        #Context = autoclass('android.content.Context')
        #print(">>>>>>\n\n ", repr(Context.NOTIFICATION_SERVICE))

        #notification.notify(title="hallo", message="sdsdsd", toast=False)

        if platform == 'android':

            
            print ("MAIN ---------> STARTING SERVICE")

            service = autoclass(service_class)
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(mActivity, argument)
             
            #service.setAutoRestartService(True)
            
            #from jnius import autoclass
            #PythonService = autoclass('org.kivy.android.PythonService')
            #PythonService.mService.setAutoRestartService(True)
    
    def stop_service(self):
        if platform == 'android':
            print ("MAIN ---------> STOPPING SERVICE")
            service = autoclass(service_class)
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            service.stop(mActivity)
    
    def onCameraClick(self, *args):

        address = "0.0.0.0"
        port = 8888
        osc = OSCClient(address, port)
        for i in range(10):
            print (" SENDING OSC", i)
            osc.send_message(b'/address', [i])


        self.start_service()
        
    def onCameraDeclick(self, *args):
    
        self.stop_service()
    
        """
        import android
        android.start_service(title='service name',
                              description='service description',
                              arg='argument to service')
                          
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        PythonService.mService.setAutoRestartService(True)
        """
        """                    
        # get the needed Java classes
        MediaRecorder = autoclass('android.media.MediaRecorder')
        AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

        # create out recorder
        mRecorder = MediaRecorder()
        mRecorder.setAudioSource(AudioSource.MIC)
        mRecorder.setOutputFormat(OutputFormat.MPEG_4)
        mRecorder.setOutputFile('/sdcard/test_recording.mp4')
        mRecorder.setAudioEncoder(AudioEncoder.AMR_NB)
        mRecorder.prepare()

        # record 5 seconds
        mRecorder.start()
        sleep(2)
        mRecorder.stop()
        mRecorder.release()
        """
        

       

# Start the Camera App

if __name__ == '__main__':

     CameraExample().run()  
     
     

    
'''


from kivy.app import App

import os

from kivy.uix.camera import Camera

from kivy.uix.boxlayout import BoxLayout

from kivy.uix.button import Button

 

class CameraExample(App):


    def build(self):
    
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.CAMERA])

        layout = BoxLayout(orientation='vertical')

       

        # Create a camera object

        self.cameraObject            = Camera(index=0, play=True)

        #self.cameraObject.play       = True

        self.cameraObject.resolution = (640,480) # Specify the resolution

        # Create a button for taking photograph

        self.camaraClick = Button(text="Take Photo")

        self.camaraClick.size_hint=(.5, .2)

        self.camaraClick.pos_hint={'x': .25, 'y':.75}

 

        # bind the button's on_press to onCameraClick

        self.camaraClick.bind(on_press=self.onCameraClick)

       

        # add camera and button to the layout

        layout.add_widget(self.cameraObject)

        layout.add_widget(self.camaraClick)

       

        # return the root widget

        return layout

 

    # Take the current frame of the video as the photo graph       

    def onCameraClick(self, *args):
        print("\n\n>>>>>>>>>>>>>>>>>", os.getcwd())
        self.cameraObject.export_to_png('selfie.png')

       

       

# Start the Camera App

if __name__ == '__main__':

     CameraExample().run()       
'''


"""
'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')


class CameraClick(BoxLayout):
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png("IMG_{}.png".format(timestr))
        print("Captured")


class TestCamera(App):

    def build(self):
        return CameraClick()


TestCamera().run()
"""


"""

'''
Basic Picture Viewer
====================

This simple image browser demonstrates the scatter widget. You should
see three framed photographs on a background. You can click and drag
the photos around, or multi-touch to drop a red dot to scale and rotate the
photos.

The photos are loaded from the local images directory, while the background
picture is from the data shipped with kivy in kivy/data/images/background.jpg.
The file pictures.kv describes the interface and the file shadow32.png is
the border to make the images look like framed photographs. Finally,
the file android.txt is used to package the application for use with the
Kivy Launcher Android application.

For Android devices, you can copy/paste this directory into
/sdcard/kivy/pictures on your Android device.

The images in the image directory are from the Internet Archive,
`https://archive.org/details/PublicDomainImages`, and are in the public
domain.

'''
import os
import kivy
kivy.require('1.0.6')

from glob import glob
from random import randint
from os.path import join, dirname
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty

from Crypto.Random import get_random_bytes

import sqlite3


con = sqlite3.connect('mydatabase.db')

cursorObj = con.cursor()


from cryptography.fernet import Fernet



class Picture(Scatter):
    '''Picture is the class that will show the image with a white border and a
    shadow. They are nothing here because almost everything is inside the
    picture.kv. Check the rule named <Picture> inside the file, and you'll see
    how the Picture() is really constructed and used.

    The source property will be the filename to show.
    '''

    source = StringProperty(None)


class PicturesApp(App):

    mytext = StringProperty("")

    def build(self):
        
        # the root is created in pictures.kv
        root = self.root

        # get any files into images directory
        curdir = dirname(__file__)
        for filename in glob(join(curdir, 'images', '*')):
            try:
                # load the image
                picture = Picture(source=filename, rotation=randint(-30, 30))
                # add to the main field
                root.add_widget(picture)
            except Exception as e:
                Logger.exception('Pictures: Unable to load <%s>' % filename)
                
        self.mytext = str(os.getcwd()) + " - " + repr(get_random_bytes(10))

    def on_pause(self):
        return True


if __name__ == '__main__':
    PicturesApp().run()
"""
