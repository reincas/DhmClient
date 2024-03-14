##########################################################################
# Copyright (c) 2024 Reinhard Caspary                                    #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

from nanofactorysystem import System, getLogger, mkdir
from dhmclient import HoloClient

args = {
    "attenuator": {
        "fitKind": "quadratic",
        },
    "controller": {
        "zMax": 25700.0,
        },
    "sample": {
        "name": "#1",
        "orientation": "top",
        "substrate": "boro-silicate glass",
        "substrateThickness": 700.0,
        "material": "SZ2080",
        "materialThickness": 75.0,
        },
    "hologram": {
        "host": "192.168.22.2",
        "port": 27182,
        "oplmode": "both",
        },
    }

user = "Reinhard"
objective = "Zeiss 20x"
path = mkdir("test/holo")
logger = getLogger(logfile="%s/console.log" % path)
with System(user, objective, logger, **args) as system:
    dc = system.container()
    dc.write("%s/system.zdc" % path)

    with HoloClient(system, logger, **args) as client:
        
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
