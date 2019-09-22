# -*- coding: utf-8 -*-

from djoro_regulation_server.djoro_regulation_server import DjoroRegulationServer

djoro = DjoroRegulationServer()
djoro.start("localhost", 9100)
