
import asyncio
import publicaddr
import logging
import sys
import os

from publicaddr_ovhcloud import ovhapi

logger = logging.getLogger("monitor")

async def monitor(every, zone, subdomains, ovh_ep, ovh_ak, ovh_as, ovh_ck, has_ipv6):
    cur_ip4 = "127.0.0.1"
    cur_ip6 = "::1"

    ovhclient = ovhapi.Client(
        endpoint=ovh_ep,
        application_key=ovh_ak,
        application_secret=ovh_as,
        consumer_key=ovh_ck,
    )

    while True:
        try:
            if has_ipv6:
                publicip = publicaddr.lookup(ip=publicaddr.IPv6)
            else:
                publicip = publicaddr.lookup()
            logger.debug("current ip4=%s ip6=%s" % (cur_ip4, cur_ip6))
            logger.debug("your public ip4=%s ip6=%s" % (publicip["ip4"], publicip["ip6"]))

            if publicip["ip4"] is not None:
                if publicip["ip4"] != cur_ip4:
                    logger.debug("updating your public ip4")
                    ovhclient.add_records(zone=zone, subdomains=subdomains, rdata=publicip["ip4"], rtype="A")
                    cur_ip4 = publicip["ip4"]

            if has_ipv6:
                if publicip["ip6"] is not None:
                    if publicip["ip6"] != cur_ip6:
                        logger.debug("updating your public ip6")
                        ovhclient.add_records(zone=zone, subdomains=subdomains, rdata=publicip["ip6"], rtype="AAAA")
                        cur_ip6 = publicip["ip6"]
        except Exception as e:
            logger.error("%s" % e)

        logger.debug("re-checking in %s seconds" % every)
        await asyncio.sleep(every)

def setup_logger(debug):
    loglevel = logging.DEBUG if debug else logging.INFO
    logfmt = '%(asctime)s %(levelname)s %(message)s'
    
    logger.setLevel(loglevel)
    logger.propagate = False
    
    lh = logging.StreamHandler(stream=sys.stdout )
    lh.setLevel(loglevel)
    lh.setFormatter(logging.Formatter(logfmt))    
    
    logger.addHandler(lh)

def start_monitor():
    # default values
    debug = False
    delay_every = 3600
    ovh_ep= "ovh-eu"

    # read environment variables
    debug_env = os.getenv('PUBLICADDR_OVHCLOUD_DEBUG')
    if debug_env is not None:
        debug = bool( int(debug_env) )

    # enable logger
    setup_logger(debug=debug)

    has_ipv6_env = os.getenv('PUBLICADDR_OVHCLOUD_HAS_IPV6')
    if has_ipv6_env is not None:
        has_ipv6 = bool( int(has_ipv6_env) )
        
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

    # run the monitor
    try:
        asyncio.run(monitor(every=delay_every, 
                            zone=zone, subdomains=subdomains,
                            ovh_ep=ovh_ep, ovh_ak=ovh_ak, 
                            ovh_as=ovh_as, 
                            ovh_ck=ovh_ck,
                            has_ipv6=has_ipv6))
    except KeyboardInterrupt:
        logger.debug("exit called")
