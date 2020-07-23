"""
Last update: 22 July 2020
Created: 10 July 2020

Camera class which runs in a separate thread.

@author: Victor Rogalev
"""
from pypylon import pylon
from pypylon import genicam
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
import time


class CameraGrabber(QRunnable):
    def __init__(self, imv, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.imageWindow = imv
        "Connect camera"
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera.Open()
            print("Using device ", self.camera.GetDeviceInfo().GetModelName())
            # The parameter MaxNumBuffer can be used to control the count of buffers
            # allocated for grabbing. The default value of this parameter is 10.
            self.camera.MaxNumBuffer = 5
            self.camera.ExposureTime = 300000   # exposure
            self.camera.PixelFormat = "RGB8"  # options: Mono8, BayerRG8, BayerRG12, BayerRG12p, YCbCr422_8, BGR8, RGB8.
            self.camera.Gain = 5
        except Exception as e:
            # Error handling.
            print("An exception occurred. Can not connect camera or set up camera parameters")
            print(e)
            pass

    @pyqtSlot()
    def run(self):
        # Start the grabbing.
        try:
            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            while self.camera.IsGrabbing():
                try:
                    grabResult = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
                    # Image grabbed successfully?
                    if grabResult.GrabSucceeded():
                        self.imageWindow.setImage(grabResult.Array)
                    else:
                        print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                    time.sleep(0.02)
                    grabResult.Release()
                except genicam.GenericException as e:
                    # Error handling.
                    print("An exception occurred.")
                    print(e.GetDescription())
                    # exitCode = 1
                    pass
        except Exception as e:
            print ("An exception occurred. No camera image")
            print (Exception)
            pass

    def stop(self):
        self.camera.StopGrabbing()
        self.camera.Close()
