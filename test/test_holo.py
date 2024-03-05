##########################################################################
# Copyright (c) 2024 Reinhard Caspary                                    #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

from scidatacontainer import load_config
from nanofactorysystem import getLogger, mkdir
from dhmclient import HoloClient

config = load_config(
    author = "Reinhard Caspary",
    email = "reinhard.caspary@phoenixd.uni-hannover.de",
    organization = "Leibniz Universität Hannover",
    orcid = "0000-0003-0460-6088")

args = {
    "host": "192.168.22.2",
    "port": 27182,
    "oplmode": "both",
    }

path = mkdir("test/holo")
logger = getLogger(logfile="%s/console.log" % path)

with HoloClient(logger=logger, config=config, **args) as client:
    
    logger.info("Select objective.")
    cid = 178
    configs = client.ConfigList
    name = dict(configs)[cid]
    client.Config = cid
    logger.info("Objective: %s [%d]" % (name, cid))

    logger.info("Motor scan.")
    opl = client.motorScan()
    logger.info("Motor pos: %.1f µm (set: %.1f µm)" % (client.MotorPos, opl.m))

    logger.info("Get hologram container.")
    dc = client.container(opt=True)
    fn = "%s/hologram.zdc" % path
    logger.info("Store hologram container file '%s'" % fn)
    dc.write(fn)
    print(dc)

    logger.info("Test camera shutter.")
    shutter = client.CameraShutter
    shutterus = client.CameraShutterUs
    logger.info("Shutter: %.1f us [%d]" % (shutterus, shutter))

    logger.info("Done.")
