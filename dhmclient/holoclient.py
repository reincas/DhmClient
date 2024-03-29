##########################################################################
# Copyright (c) 2024 Reinhard Caspary                                    #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

import logging
from types import SimpleNamespace
import numpy as np
from scidatacontainer import timestamp, load_config

from .dhmclient import DhmClient
from .rawholo import HoloContainer
from .exposure import optImage
from .motorscan import motorScan
from .hologram import refHolo


class HoloClient(DhmClient):

    """ Client class to access the remote server HoloServ with high
    level functionality. It delivers the hologram as HoloContainer
    object. """

    contrastQuantile = 0.05


    def __init__(self, system, logger=None, **kwargs):

        # Store logger
        self.log = logger or logging
        self.log.info("Initializing HoloClient.")

        # Store system object
        self.system = system

        # Store user data dictionary
        self.user = self.system.user
        self.config = load_config(
            author = self.user.get("name", None),
            email = self.user.get("email", None),
            organization = self.user.get("organization", None),
            orcid = self.user.get("orcid", None))

        # Exposure optimization parameter
        self.maxof = kwargs.pop("maxof", 9)

        # OPL scan parameters
        args = kwargs.pop("hologram", {})
        self.opl = SimpleNamespace(
            mode = str(args.pop("oplmode", "both")),
            steps = int(args.pop("oplsteps", 11)),
            dm = float(args.pop("opldm", 250.0)),
            thresh = float(args.pop("oplthresh", 0.2)),
            minc = float(args.pop("oplminc", 0.001)),
            minm = float(args.pop("oplminms", 5.0)),
            opt = bool(args.pop("oplopt", True)),
            timestamp = None,
            m = None,
            m0 = None,
        )

        # Reference parameters
        self.ref = SimpleNamespace(
            blur = int(kwargs.pop("refblur", 16)),
            order = int(kwargs.pop("reforder", 2)),
            timestamp = None,
            )

        # Initialize parent class
        host = args.pop("host", None)
        port = args.pop("port", None)
        super().__init__(host, port)

        # Select objective
        logger.info("Select objective.")
        cid = self.system.objective["dhmId"]
        configs = self.ConfigList
        name = dict(configs)[cid]
        self.Config = cid
        logger.info("Objective: %s [%d]" % (name, cid))
        
        # Done
        self.log.info("Initialized HoloClient.")
        

    def getImage(self, opt=True):

        """ Grab a camera image with maximized exposure time limited by
        a maximum of self.maxof overflow pixels if opt is True. Return
        the total number of images grabbed by the algorithm as second
        parameter. Return a camera image using the current exposure
        time, if opt is False. """

        if opt:
            img, count = optImage(self, self.maxof, self.log)
        else:
            img = self.CameraImage
            count = None
        return img, count


    def motorScan(self, m0=None):

        """ Perform a scan of the optical path length (OPL) motor. The
        interference contrast is maximized by balancing the path lengths
        of object and reference beam. """

        opl = self.opl
        opl.m, opl.m0 = motorScan(self, mode=opl.mode, steps=opl.steps,
                                  dm=opl.dm, thresh=opl.thresh, init=m0,
                                  minc=opl.minc, minm=opl.minm, opt=opl.opt,
                                  logger=self.log)
        return opl


    def refImage(self, blur=None, order=None, img=None):

        """ Take and evaluate a reference image. Determine the spectral
        location of the first diffraction order and apply a polynomial fit
        to the phase of the wave field. """

        ref = self.ref
        if blur is not None:
            ref.blur = int(blur)
        if order is not None:
            ref.order = int(order)
        if img is None:
            img = self.CameraImage

        refHolo(img, blur=ref.blur, order=ref.order, ref=ref)

        ref.x, ref.y, ref.z = self.system.position("XYZ")
        ref.motor = self.MotorPos
        ref.shutter = self.CameraShutter

        ref.timestamp = timestamp()
        return ref


    def parameters(self, holo, count):

        # Current DHM parameters
        params = super().parameters()

        # Median values
        q = [self.contrastQuantile, 0.5, 1.0-self.contrastQuantile]
        imin, imedian, imax = np.quantile(holo, q, method="nearest")

        # Overflow and underflow pixels
        numuf = np.count_nonzero(holo <= 0)
        numof = np.count_nonzero(holo >= 255)

        # Add OPL scan parameters
        params["opl"] = {
            "mode": self.opl.mode,
            "shortSteps": self.opl.steps,
            "stepSizeUm": self.opl.dm,
            "contrastThreshold": self.opl.thresh,
            "minContrast": self.opl.minc,
            "minSpanUm": self.opl.minm,
            "optMode": self.opl.opt,
            "initPositionUm": self.opl.m0,
            "scanResultUm": self.opl.m,
           }

        # Add some basic image evaluation data
        params["image"] = {
            "optCount": count,
            "maxOverflow": self.maxof,
            "minValue": int(np.min(holo)),
            "maxValue": int(np.max(holo)),
            "avgerageValue": float(np.average(holo)),
            "contrastQuantile": self.contrastQuantile,
            "lowQuantileValue": int(imin),
            "medianValue": int(imedian),
            "highQuantileValue": int(imax),
            "underflowPixel": numuf,
            "overflowPixel": numof,
            }

        # Done.
        return params


    def container(self, opt=True, config=None, **kwargs):

        """ Return a HoloContainer with current hologram image. """

        # Hologram image
        holo, count = self.getImage(opt=opt)

        # Hologram parameters
        params = self.parameters(holo, count)

        # Stage positions
        x, y, z = self.system.position("XYZ")
        items = { "meas/stage.json": {
            "xPositionUm": x,
            "yPositionUm": y,
            "zPositionUm": z}}

        # Return container object
        config = config or self.config
        return HoloContainer(holo=holo, params=params, items=items, config=config, **kwargs)
