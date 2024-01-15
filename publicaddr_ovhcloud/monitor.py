
import asyncio
import publicaddr
import logging
import sys
import os
import argparse
import signal

from dotenv import load_dotenv
from publicaddr_ovhcloud import ovhapi

logger = logging.getLogger("monitor")
loop = asyncio.get_event_loop()
shutdown_task = None

async def monitor(every, zone, subdomains, ovh_ep, ovh_ak, ovh_as, ovh_ck, has_ipv6, use_protocol, start_shutdown):
    cur_ip4 = "127.0.0.1"
    cur_ip6 = "::1"

    ovhclient = ovhapi.Client(
        endpoint=ovh_ep,
        application_key=ovh_ak,
        application_secret=ovh_as,
        consumer_key=ovh_ck,
    )

    while not start_shutdown.is_set():
        try:
            providers = publicaddr.ALL
            ip = None

            if use_protocol == "http":
                providers = publicaddr.HTTPS
            if use_protocol == "dns":
                providers = publicaddr.DNS
            if use_protocol == "stun":
                providers = publicaddr.STUN

            if not has_ipv6:
                ip = ip=publicaddr.IPv4

            logger.debug("publicaddr: get public has_ipv6=%s protocols=%s" % (has_ipv6, providers))
            publicip = await asyncio.to_thread(publicaddr.lookup, providers=providers, ip=ip)

            logger.debug("publicaddr: previous ip4=%s ip6=%s" % (cur_ip4, cur_ip6))
            logger.debug("publicaddr: current public ip4=%s ip6=%s" % (publicip["ip4"], publicip["ip6"]))
        except Exception as e:
            logger.error("publicaddr: %s" % e)

        try:
            if publicip["ip4"] is not None:
                if publicip["ip4"] != cur_ip4:
                    logger.debug("ovh: updating your public ip4 dns record")
                    ovhclient.add_records(zone=zone, subdomains=subdomains, rdata=publicip["ip4"], rtype="A")
                    cur_ip4 = publicip["ip4"]

            if has_ipv6:
                if publicip["ip6"] is not None:
                    if publicip["ip6"] != cur_ip6:
                        logger.debug("ovh: updating your public ip6 dns record")
                        ovhclient.add_records(zone=zone, subdomains=subdomains, rdata=publicip["ip6"], rtype="AAAA")
                        cur_ip6 = publicip["ip6"]
        except Exception as e:
            logger.error("ovh: %s" % e)

        logger.debug("re-checking in %s seconds" % every)
        try:
            await asyncio.wait_for(start_shutdown.wait(), timeout=every)
        except asyncio.TimeoutError:
            pass

def setup_logger(debug):
    loglevel = logging.DEBUG if debug else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'
    
    logger.setLevel(loglevel)
    logger.propagate = False
    
    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))    
    
    logger.addHandler(lh)

async def shutdown(signal, loop, start_shutdown):
    """perform graceful shutdown"""
    logger.debug("starting shutting down process")
    start_shutdown.set()

    current_task = asyncio.current_task()
    tasks = [
        task for task in asyncio.all_tasks()
        if task is not current_task
    ]

    logger.debug("waiting for all tasks to exit")
    await asyncio.gather(*tasks, return_exceptions=True)

    logger.debug("all tasks have exited, stopping event loop")
    loop.stop()

def start_monitor():
    # default values
    debug = False
    delay_every = 3600
    ovh_ep= "ovh-eu"
    has_ipv6 = True

    # read config from environnement file ?
    options = argparse.ArgumentParser()
    options.add_argument("-e", help="env config file") 

    args = options.parse_args()
    if args.e != None:
        load_dotenv(dotenv_path=args.e)

    # read environment variables
    debug_env = os.getenv('PUBLICADDR_OVHCLOUD_DEBUG')
    if debug_env is not None:
        debug = bool( int(debug_env) )

    # enable logger
    setup_logger(debug=debug)

    has_ipv6_env = os.getenv('PUBLICADDR_OVHCLOUD_HAS_IPV6')
    if has_ipv6_env is not None:
        has_ipv6 = bool( int(has_ipv6_env) )

    use_protocol = os.getenv('PUBLICADDR_OVHCLOUD_USE_PROTOCOL')

    delay_env = os.getenv('PUBLICADDR_OVHCLOUD_UPDATE')
    if delay_env is not None:
        delay_every = int(delay_env)

    subdomains_env = os.getenv('PUBLICADDR_OVHCLOUD_SUBDOMAINS')
    if subdomains_env is None:
        logger.error("missing env variable PUBLICADDR_OVHCLOUD_SUBDOMAINS")
        sys.exit(1)
    subdomains = subdomains_env.split(",")

    ovh_ep_env = os.getenv('PUBLICADDR_OVHCLOUD_ENDPOINT')
    if ovh_ep_env is None:
        logger.error("missing env variable PUBLICADDR_OVHCLOUD_ENDPOINT")
        sys.exit(1)
    ovh_ep = ovh_ep_env

    zone = os.getenv('PUBLICADDR_OVHCLOUD_ZONE')
    if zone is None:
        logger.error("missing env variable PUBLICADDR_OVHCLOUD_ZONE")
        sys.exit(1)

    ovh_ak = os.getenv('PUBLICADDR_OVHCLOUD_APPLICATION_KEY')
    if ovh_ak is None:
        logger.error("missing env variable PUBLICADDR_OVHCLOUD_APPLICATION_KEY")
        sys.exit(1)

    ovh_as = os.getenv('PUBLICADDR_OVHCLOUD_APPLICATION_SECRET')
    if ovh_as is None:
        logger.error("missing env variable PUBLICADDR_OVHCLOUD_APPLICATION_SECRET")
        sys.exit(1)

    ovh_ck = os.getenv('PUBLICADDR_OVHCLOUD_CONSUMER_KEY')
    if ovh_ck is None:
        logger.error("missing env variable PUBLICADDR_OVHCLOUD_CONSUMER_KEY")
        sys.exit(1)

    # prepare shutdown handling
    start_shutdown = asyncio.Event()
    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(
            shutdown(sig, loop, start_shutdown)
        ))

    # run monitor
    loop.create_task(
                    monitor(
                        every=delay_every, 
                        zone=zone, 
                        subdomains=subdomains,
                        ovh_ep=ovh_ep, 
                        ovh_ak=ovh_ak, 
                        ovh_as=ovh_as, 
                        ovh_ck=ovh_ck,
                        has_ipv6=has_ipv6,
                        use_protocol=use_protocol,
                        start_shutdown=start_shutdown
                        )
                    )

    # run event loop 
    try:
       loop.run_forever()
    finally:
       loop.close()
    
    logger.debug("app terminated")