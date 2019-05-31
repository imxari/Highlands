#! /usr/bin/env python3
##
# ZeroTier Network Controller
# By Amos <LFlare> Ng
##
from ipaddress import *
import argparse
import atexit
import json
import pickle
import platform
import requests
import sys
import collections

base_api = "http://127.0.0.1:9993"
ctrlr = None


def pprint(obj):
    print(json.dumps(obj, indent=2, separators=(',', ': ')))


def ddict():
    return collections.defaultdict(ddict)


def request(url, payload=None, method="get"):
    """Simple request wrapper

    Takes a couple of variables and wraps around the requests
    module

    Args:
        url: API URL
        method: Query method (default: {"get"})
        payload: JSON payload (default: {None})

    Returns:
        Dataset as result from query
        JSON Object
    """
    r = None
    if payload is not None:
        r = requests.post(
            base_api+url, headers=ctrlr["headers"], json=payload)
    elif method == "get":
        r = requests.get(
            base_api+url, headers=ctrlr["headers"])
    elif method == "delete":
        r = requests.delete(
            base_api+url, headers=ctrlr["headers"])
    return r.json()


def save_ctrlr():
    with open(get_filepath()+"/ctrlr.pickle", "wb") as file:
        pickle.dump(ctrlr, file)


def load_ctrlr():
    global ctrlr
    try:
        with open(get_filepath()+"/ctrlr.pickle", "rb") as file:
            ctrlr = pickle.load(file)
    except:
        ctrlr = ddict()


def get_filepath():
    """Get filepath according to OS"""
    if platform.system() == "Linux":
        return "/var/lib/zerotier-one"
    elif platform.system() == "Darwin":
        return "/Library/Application Support/ZeroTier/One"
    elif platform.system() == "FreeBSD" or platform.system() == "OpenBSD":
        return "/var/db/zerotier-one"
    elif platform.system() == "Windows":
        return "C:\ProgramData\ZeroTier\One"


def set_headers():
    """Sets authentication headers globally

    Automatically detect system and reads authtoken.secret
    to set authenticaiton headers used in request method
    globally.
    """
    with open(get_filepath()+"/authtoken.secret") as file:
        ctrlr["headers"] = {"X-ZT1-Auth": file.read()}


def set_id():
    ctrlr["ztid"] = request("/status").get("address")


def valid_nwid(nwid):
    return nwid is not None and (len(nwid) == 16 or len(nwid) == 6)


def valid_ztid(ztid):
    return ztid is not None and len(ztid) == 10


def alias(alias=None, nwid=None, ztid=None):
    if alias is not None:

        # Set alias
        if valid_nwid(nwid):

            # Set member alias
            if valid_ztid(ztid):
                ctrlr["network"][nwid]["member"][ztid]["alias"] = alias
                return ctrlr["network"][nwid]["member"]

            # Set network alias
            else:
                ctrlr["network"][nwid]["alias"] = alias
                request("/controller/network/"+nwid, {"name": alias})
                return ctrlr["network"]

        # Get from alias
        else:

            # Get member from alias
            if ":" in alias:
                nwalias, ztalias = alias.split(":")
                for x, y in ctrlr["network"].items():
                    if nwalias == y["alias"]:
                        for xx, yy in ctrlr["network"][x]["member"].items():
                            if ztalias == yy["alias"]:
                                return x, xx

            # Get network from alias
            else:
                for x, y in ctrlr["network"].items():
                    if y["alias"] == alias:
                        return x
    else:

        # Get alias
        if valid_nwid(nwid):

            # Get member alias
            if valid_ztid(ztid):
                for x, y in ctrlr["network"].items():
                    if nwid == x:
                        for xx, yy in ctrlr["network"][x]["member"].items():
                            if ztid == xx:
                                return y["alias"], yy["alias"]

            # Get network alias
            else:
                for x, y in ctrlr["network"].items():
                    if nwid == x:
                        return y["alias"]


def net_add(nwid):
    return request("/controller/network/"+nwid, {})


def net_del(nwid):
    if nwid in ctrlr["network"]:
        ctrlr["network"][nwid].clear()
        del ctrlr["network"][nwid]
    return request("/controller/network/"+nwid, method="delete")


def net_info(nwid):
    ctrlr["network"][nwid].update(request("/controller/network/"+nwid))
    return ctrlr["network"][nwid]


def net_ipadd(nwid, ip):
    ipaddrs = list(ip_network(ip).hosts())
    start, end = tuple([str(x) for x in ipaddrs[::len(ipaddrs)-1]])
    net = net_info(nwid)
    net["v4AssignMode"] = {"zt": "true"}
    net["routes"].append({"target": ip, "via": "null"})
    net["ipAssignmentPools"].append({"ipRangeStart": start, "ipRangeEnd": end})
    return request("/controller/network/"+nwid, net)


def net_ipdel(nwid, ip):
    ipaddrs = list(ip_network(ip).hosts())
    start, end = tuple([str(x) for x in ipaddrs[::len(ipaddrs)-1]])
    net = net_info(nwid)
    net["v4AssignMode"] = {"zt": "true"}
    net["routes"] = [
        x for x in net["routes"]
        if x["target"] != ip]
    net["ipAssignmentPools"] = [
        x for x in net["ipAssignmentPools"]
        if x["ipRangeStart"] != start or x["ipRangeEnd"] != end]
    return request("/controller/network/"+nwid, net)


def net_list():
    nwids = request("/controller/network")
    new_nwids = dict()
    for nwid in nwids:
        new_nwids[nwid] = alias(nwid=nwid)
    return new_nwids


def net_pooladd(nwid, ip):
    ipaddrs = list(ip_network(ip).hosts())
    start, end = tuple([str(x) for x in ipaddrs[::len(ipaddrs)-1]])
    net = net_info(nwid)
    net["v4AssignMode"] = {"zt": "true"}
    net["ipAssignmentPools"].append({"ipRangeStart": start, "ipRangeEnd": end})
    return request("/controller/network/"+nwid, net)


def net_pooldel(nwid, ip):
    ipaddrs = list(ip_network(ip).hosts())
    start, end = tuple([str(x) for x in ipaddrs[::len(ipaddrs)-1]])
    net = net_info(nwid)
    net["v4AssignMode"] = {"zt": "true"}
    net["ipAssignmentPools"] = [
        x for x in net["ipAssignmentPools"]
        if x["ipRangeStart"] != start or x["ipRangeEnd"] != end]
    return request("/controller/network/"+nwid, net)


def net_routeadd(nwid, ip):
    net = net_info(nwid)
    net["routes"].append({"target": ip[0], "via": ip[1]})
    return request("/controller/network/"+nwid, net)


def net_routedel(nwid, ip):
    net = net_info(nwid)
    net["routes"] = [
        x for x in net["routes"]
        if x["target"] != ip]
    return request("/controller/network/"+nwid, net)


def member_auth(nwid, ztid):
    net = net_info(nwid)
    member = net["member"][ztid]
    member["authorized"] = "true"
    return request("/controller/network/"+nwid+"/member/"+ztid, member)


def member_deauth(nwid, ztid):
    net = net_info(nwid)
    member = net["member"][ztid]
    member["authorized"] = "false"
    return request("/controller/network/"+nwid+"/member/"+ztid, member)

def member_activebridge(nwid, ztid):
    net = net_info(nwid)
    member = net["member"][ztid]
    member["activeBridge"] = "true"
    return request("/controller/network/"+nwid+"/member/"+ztid, member)

def member_inactivebridge(nwid, ztid):
    net = net_info(nwid)
    member = net["member"][ztid]
    member["activeBridge"] = "false"
    return request("/controller/network/"+nwid+"/member/"+ztid, member)


def member_delete(nwid, ztid):
    del ctrlr["network"][nwid]["member"][ztid]
    return request(
        "/controller/network/"+nwid+"/member/"+ztid,
        method="delete"
    )


def member_info(nwid, ztid):
    net = net_info(nwid)
    member = net["member"][ztid]
    member.update(request("/controller/network/"+nwid+"/member/"+ztid))
    return member


def member_ipset(nwid, ztid, ip):
    member = member_info(nwid, ztid)
    member["ipAssignments"] = [ip]
    member = request("/controller/network/"+nwid+"/member/"+ztid, member)
    return member


def member_ipadd(nwid, ztid, ip):
    member = member_info(nwid, ztid)
    member["ipAssignments"].append(ip)
    member = request("/controller/network/"+nwid+"/member/"+ztid, member)
    return member


def member_ipdel(nwid, ztid, ip):
    member = member_info(nwid, ztid)
    if ip in member["ipAssignments"]:
        member["ipAssignments"].remove(ip)
    member = request("/controller/network/"+nwid+"/member/"+ztid, member)
    return member


def member_list(nwid):
    ztids = request("/controller/network/"+nwid+"/member")
    new_ztids = dict()
    for ztid in ztids:
        new_ztids[ztid] = dict()
        new_ztids[ztid]["ipAssignments"] = ", ".join(
            member_info(nwid, ztid)["ipAssignments"])

        try:
            new_ztids[ztid]["alias"] = ":".join(alias(nwid=nwid, ztid=ztid))
        except TypeError:
            new_ztids[ztid]["alias"] = alias(nwid=nwid, ztid=ztid)
    return new_ztids


def main():
    # Load/Create controller and set atexit argument
    load_ctrlr()
    atexit.register(save_ctrlr)

    # Populate current fields
    set_headers()
    set_id()

if __name__ == "__main__":
    main()