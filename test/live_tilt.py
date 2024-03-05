##########################################################################
# Copyright (c) 2024 Reinhard Caspary                                    #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from nanofactorytools import image

from dhmclient import HoloClient
import hologram


author = "Reinhard Caspary"
email = "reinhard.caspary@phoenixd.uni-hannover.de"

run = False

############################################################################
# Utility functions
############################################################################

def on_close(event):

    global run
    run = False
    print("Quitting...")


def getImage(holo):

    ref = hologram.refHolo(holo, 16, 2)
    print("First order coordinates: %d, %d [%.1f%%]" % (ref.fx, ref.fy, 100*ref.weight))

    maxpixel = 255
    numof = np.count_nonzero(holo >= maxpixel)
    print("Overflow pixels: %d" % numof)
    
    spectrum = np.fft.fftshift(np.fft.fft2(holo.astype(np.float64)))
    spectrum = np.log(np.abs(spectrum))
    
    img = spectrum
    vmax = 0.5*np.max(img)
    img = np.where(img > vmax, vmax, img) 
    img = image.normcolor(img)
    
    h, w = img.shape
    r0 = 310
    img = utils.drawCircle(img, 0, 0, 310, utils.CV_RED, 1)
    
    rmax = np.sqrt(ref.fx**2 + ref.fy**2) - r0
    rmax = min(rmax, abs(ref.fx), w//2-abs(ref.fx), abs(ref.fy), h//2-abs(ref.fy))
    print("Maximum radius: %d pixels" % rmax)
    if rmax > 0:
        img = utils.drawCircle(img, ref.fx, ref.fy, rmax, utils.CV_RED, 1)
        img = utils.drawCircle(img, -ref.fx, -ref.fy, rmax, utils.CV_RED, 1)
    img = utils.drawCross(img, ref.fx, ref.fy, 30, utils.CV_RED, 1)
    img = utils.drawCross(img, -ref.fx, -ref.fy, 30, utils.CV_RED, 1)
    return img


def showImage(ax, img, win):

    h, w, d = img.shape
    border = 20
    img = utils.addBorder(img, border, 127)
    extent = [-w//2-border, w//2+border-1, -h//2-border, h//2+border-1]

    if win is None:
        win = ax.imshow(img[:,:,::-1], origin="lower", extent=extent)
    else:
        win.set_data(img[:,:,::-1])
    plt.pause(0.1)
    return win


############################################################################
# Main function
############################################################################

if __name__ == "__main__":

    #path = utils.mkdir("test/tilt")
    opt = True
    
    fig, ax = plt.subplots()
    fig.canvas.mpl_connect("close_event", on_close)
        
    with HoloClient() as client:
        cid = 180
        configs = client.ConfigList
        name = dict(configs)[cid]
        client.Config = cid
        print("Objective: %s [%d]" % (name, cid))

        if opt:
            print("Run OPL Motor Scan...")
            client.motorScan(show=True)
            print("Motor pos:", client.MotorPos)

            print("Optimize Camera Exposure Time...")
            client.getImage(opt=True, show=True)
            #client.CameraShutter = client.CameraShutter-2
            shutter = client.CameraShutter
            shutterus = client.CameraShutterUs
            print("Shutter: %.1f us [%d]" % (shutterus, shutter))
        
        print("Start Spectrum Display Loop...")
        run = True
        win = None
        while (run):
            holo, count = client.getImage()
            img = getImage(holo)
            win = showImage(ax, img, win)
            #plt.pause(0.1)

        print("Done.")
