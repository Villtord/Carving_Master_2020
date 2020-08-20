# -*- coding: utf-8 -*-
"""
GUI image from camera
https://github.com/basler/pypylon/blob/master/samples/guiimagewindow.py
"""

from pypylon import pylon
from pypylon import genicam
import time

try:
    imageWindow = pylon.PylonImageWindow()
    imageWindow.Create(1)
    # Create an instant camera object with the camera device found first.
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()

    # Print the model name of the camera.
    print("Using device ", camera.GetDeviceInfo().GetModelName())
    
    camera.MaxNumBuffer = 5
    camera.ExposureTime = 300000   # exposure
    camera.PixelFormat = "RGB8"  # options: Mono8, BayerRG8, BayerRG12, BayerRG12p, YCbCr422_8, BGR8, RGB8.
    camera.Gain = 5

    # Start the grabbing of c_countOfImagesToGrab images.
    # The camera device is parameterized with a default configuration which
    # sets up free-running continuous acquisition.
    camera.StartGrabbingMax(10000, pylon.GrabStrategy_LatestImageOnly)

    while camera.IsGrabbing():
        # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        # Image grabbed successfully?
        if grabResult.GrabSucceeded():
            imageWindow.SetImage(grabResult)
            imageWindow.Show()
        else:
            print("Error: ",
                  grabResult.ErrorCode)  # grabResult.ErrorDescription does not work properly in python could throw UnicodeDecodeError
        grabResult.Release()
        time.sleep(0.05)

        if not imageWindow.IsVisible():
            camera.StopGrabbing()

    # camera has to be closed manually
    camera.Close()
    # imageWindow has to be closed manually
    imageWindow.Close()

except genicam.GenericException as e:
    # Error handling.
    print("An exception occurred.")
    print(e.GetDescription())