##########################################################################
# Copyright (c) 2024 Reinhard Caspary                                    #
# <reinhard.caspary@phoenixd.uni-hannover.de>                            #
# This program is free software under the terms of the MIT license.      #
##########################################################################

from scidatacontainer import load_config
from dhmclient import HoloClient

HOST = "192.168.22.2"
PORT = 27182

config = load_config(
    author = "Reinhard Caspary",
    email = "reinhard.caspary@phoenixd.uni-hannover.de",
    organization = "Leibniz Universität Hannover",
    orcid = "0000-0003-0460-6088")

with HoloClient(host=HOST, port=PORT, config=config, oplmode="both") as client:
    cid = 178
    configs = client.ConfigList
    name = dict(configs)[cid]
    client.Config = cid
    print("Objective: %s [%d]" % (name, cid))

    m = client.motorScan(show=True)
    print("Motor pos: %.1f µm (set: %.1f µm)", (client.MotorPos, m))

    client.getImage(opt=True, show=True)

    dc = client.container(opt=True, show=True)
    dc.write("hologram.zdc")
    print(dc)

    shutter = client.CameraShutter
    shutterus = client.CameraShutterUs
    print("Shutter: %.1f us [%d]" % (shutterus, shutter))

    print("Done.")
