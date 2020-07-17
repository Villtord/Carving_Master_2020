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
from PyQt5.QtCore import QTimer
from pypylon import pylon
from pypylon import genicam
from PIL import Image
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtCore import QThreadPool
import time


# from updater_test import Image_Updater


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    progress
    int progress complete,from 0-100
    """
    new_image_signal = pyqtSignal(tuple)


class CameraGrabber(QRunnable):
    def __init__(self, ax, canvas, *args, **kwargs):
        super(self.__class__, self).__init__()
        self.subplot = ax
        self.canvas = canvas
        "Connect camera"
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        # The parameter MaxNumBuffer can be used to control the count of buffers
        # allocated for grabbing. The default value of this parameter is 10.
        self.camera.MaxNumBuffer = 25
        self.camera.ExposureTime = 300000   # exposure
        self.camera.PixelFormat = "RGB8"  # options: Mono8, BayerRG8, BayerRG12, BayerRG12p, YCbCr422_8, BGR8, RGB8.
        try:
            self.camera.Gain = 5
        except genicam.LogicalErrorException:
            self.camera.GainRaw = self.camera.GainRaw.Max

    @pyqtSlot()
    def run(self):
        # Start the grabbing.
        # The camera device is parameterized with a default configuration which
        # sets up free-running continuous acquisition.
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        while self.camera.IsGrabbing():
            try:
                grabResult = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)
                # Image grabbed successfully?
                if grabResult.GrabSucceeded():
                    # print("SizeX: ", grabResult.Width)
                    # print("SizeY: ", grabResult.Height)
                    pil_image = Image.fromarray(grabResult.Array)
                    # binned_image = pil_image.reduce(4)
                    binned_image = pil_image.resize((int(pil_image.width / 4), int(pil_image.height / 3)))
                    self.subplot.cla()
                    self.subplot.imshow(binned_image)
                    self.canvas.draw()
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
