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
import PyQt5.QtCore
from pypylon import pylon
from pypylon import genicam
import time


class CameraGrabber(PyQt5.QtCore.QThread):
    new_image_signal = PyQt5.QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__()
        # Create an pylon image object.
        # self.img = pylon.PylonImage()
        # Create an instant camera object with the camera device found first.
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    def run(self):
        try:
            self.camera.Open()
            # Print the model name of the camera.
            print("Using device ", self.camera.GetDeviceInfo().GetModelName())

            # The parameter MaxNumBuffer can be used to control the count of buffers
            # allocated for grabbing. The default value of this parameter is 10.
            self.camera.MaxNumBuffer = 5

            # Start the grabbing.
            # The camera device is parameterized with a default configuration which
            # sets up free-running continuous acquisition.
            self.camera.StartGrabbing()

            while self.camera.IsGrabbing():
                # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
                grabResult = self.camera.RetrieveResult(1000, pylon.TimeoutHandling_ThrowException)

                # Image grabbed successfully?
                if grabResult.GrabSucceeded():
                    # self.img.AttachGrabResultBuffer(grabResult)
                    self.new_image_signal.emit(grabResult.Array)
                    time.sleep(0.05)
                else:
                    print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                grabResult.Release()
                # self.img.Release()

        except genicam.GenericException as e:
            # Error handling.
            print("An exception occurred.")
            print(e.GetDescription())
            # exitCode = 1
            pass

    def stop(self):
        self.camera.StopGrabbing()
        self.camera.Close()

        # sys.exit(exitCode)
