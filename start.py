#!/usr/bin/env python3

import os
import sys
import time

from config import *
from proxy import log, Privoxy

PROXY_LIST_TXT = "proxy-list.txt"
PROXY_LIST_PY = "proxy-list.py"

TORS = int(os.environ.get("TORS", 5))
HEADS = int(os.environ.get("HEADS", 1))


def main():
    log.info("========================================")
    log.info("Medusa Proxy")
    log.info("%s" % (VERSION,))
    log.info("========================================")

    privoxy = [Privoxy(TORS, i) for i in range(HEADS)]

    log.info("Writing proxy list.")
    with open(PROXY_LIST_TXT, "wt") as file:
        for http in privoxy:
            file.write("http://127.0.0.1:%d\n" % http.port)
    log.info("Done.")

    log.info("Serving proxy list.")
    os.spawnl(os.P_NOWAIT, os.curdir + os.sep + PROXY_LIST_PY, PROXY_LIST_PY)

    while True:
        for i in range(3):
            log.info("Testing proxies.")
            for http in privoxy:
                log.info(f"* Privoxy {http.id}")
                socks = http.haproxy
                for proxy in socks.proxies:
                    if not proxy.working:
                        log.warning("Restarting.")
                        proxy.restart()

            log.info("Sleeping.")
            time.sleep(60)

        for http in privoxy:
            http.cycle()


try:
    main()
except KeyboardInterrupt:
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
