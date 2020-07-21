# ===============================================================================
#    This sample illustrates how to grab and process images using the CInstantCamera class.
#    The images are grabbed and processed asynchronously, i.e.,
#    while the application is processing a buffer, the acquisition of the next buffer is done
#    in parallel.
#
#    The CInstantCamera class uses a pool of buffers to retrieve image data
#    from the camera device. Once a buffer is filled and ready,
#    the buffer can be retrieved from the camera object for processing. The buffer
#    and additional image data are collected in a grab result. The grab result is
#    held by a smart pointer after retrieval. The buffer is automatically reused
#    when explicitly released or when the smart pointer object is destroyed.
# ===============================================================================

from pypylon import pylon
from pypylon import genicam
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
import time
import numpy as np


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    progress
    int progress complete,from 0-100
    """
    new_image_signal = pyqtSignal(tuple)


class CameraGrabber(QRunnable):
    def __init__(self, imv, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.imageWindow = imv
        "Connect camera"
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        # The parameter MaxNumBuffer can be used to control the count of buffers
        # allocated for grabbing. The default value of this parameter is 10.
        self.camera.MaxNumBuffer = 5
        self.camera.ExposureTime = 300000   # exposure
        self.camera.PixelFormat = "RGB8"  # options: Mono8, BayerRG8, BayerRG12, BayerRG12p, YCbCr422_8, BGR8, RGB8.
        self.camera.Gain = 5

    @pyqtSlot()
    def run(self):
        # Start the grabbing.
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        while self.camera.IsGrabbing():
            try:
                grabResult = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
                # Image grabbed successfully?
                if grabResult.GrabSucceeded():
                    numpy_image = np.array(grabResult.Array)
                    factor = 4
                    small_image = numpy_image.reshape((grabResult.Height // factor, factor,
                                                       grabResult.Width// factor, factor, 3)).max(3).max(1)
                    # small_image = numpy_image.reshape((grabResult.Height // factor, factor,
                    #                                    grabResult.Width// factor, factor, 3)).mean(3).mean(1)
                    self.imageWindow.setImage(small_image)
                else:
                    print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                time.sleep(0.05)
                grabResult.Release()
            except genicam.GenericException as e:
                # Error handling.
                print("An exception occurred.")
                print(e.GetDescription())
                # exitCode = 1
                pass

    def stop(self):
        self.camera.StopGrabbing()
        self.camera.Close()
