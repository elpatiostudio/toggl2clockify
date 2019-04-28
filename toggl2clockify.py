#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Markus Proeller"
__copyright__ = "Copyright 2019, pieye GmbH (www.pieye.org)"
__maintainer__ = "Markus Proeller"
__email__ = "markus.proeller@pieye.org"

import logging
import os
import json
import argparse
import dateutil
import Clue

parser = argparse.ArgumentParser()
parser.add_argument("--skipClients", help="don't sync workspace clients", action="store_true")
parser.add_argument("--skipProjects", help="don't sync workspace projects", action="store_true")
parser.add_argument("--skipEntries", help="don't sync workspace time entries", action="store_true")
parser.add_argument("--skipTags", help="don't sync tags", action="store_true")
parser.add_argument("--reqTimeout", help="sleep time between clockify web requests", type=float, default=0.01)
args = parser.parse_args()

ok = False
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("toggl2clockify")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

fName = os.path.abspath("config.json")
try:
    f = open(fName, "r")
    ok = True
except:
    logger.error("file %s not found"%(fName))
    
if ok:
    try:
        data = json.load(f)
        ok = True
    except Exception as e:
        logger.error("reading content of json file %s failed with msg: %s"%(fName, str(e)))
        ok = False
    
if ok:
    if "ClockifyKeys" not in data:
        logger.error("json entry 'ClockifyKeys' missing in file %s"%fName)
        ok = False
        
    if ok:
        clockifyTokens = data["ClockifyKeys"]
        if type(clockifyTokens) != type ([]):
            logger.error("json entry 'ClockifyKeys' must be a list of strings")
            ok = False
            
    if ok:
        if "TogglKey" not in data:
            logger.error("json entry 'TogglKey' missing in file %s"%fName)
            ok = False
            
    if ok:
        togglKey = data["TogglKey"]
        if type(togglKey) != type(""):
            logger.error("json entry 'TogglKey' must be a strings")
            ok = False
            
    if ok:
        if "StartTime" not in data:
            logger.error("json entry 'StartTime' missing in file %s"%fName)
            ok = False
    if ok:
        try:
            startTime = dateutil.parser.parse(data["StartTime"])
        except Exception as e:
            logger.error("could not parse 'StartTime' correctly make sure it is a ISO 8601 time string")
            ok = False

    if ok:
        if "Workspaces" in data:
            workspaces = data["Workspaces"]
            if type(workspaces) != type([]):
                logger.error("json entry 'Workspaces' must be a list")
                ok = False
        else:
            workspaces = None
            
    if ok:
        if "ClockifyAdmin" not in data:
            logger.error("json entry 'ClockifyAdmin' missing in file %s"%fName)
            ok = False
        else:
            clockifyAdmin = data["ClockifyAdmin"]
            if type(clockifyAdmin) != type(""):
                logger.error("json entry 'ClockifyAdmin' must be a string")
                ok = False
           
if ok:
    cl = Clue.Clue(clockifyTokens, clockifyAdmin, togglKey, clockifyReqTimeout=args.reqTimeout)
    
    if workspaces == None:
        logger.info("no workspaces specified in json file, I'm trying to import all toggl workspaces...")
        workspaces = cl.getTogglWorkspaces()
        logger.info("The following workspaces were found and will be imported now %s"%str(workspaces))
        
    numWS = len(workspaces)
    idx = 1
    for ws in workspaces:
        logger.info("-------------------------------------------------------------")
        logger.info("Starting to import workspace '%s' (%d of %d)"%(ws, idx, numWS))
        logger.info("-------------------------------------------------------------")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 1 of 4: Import clients")
        logger.info("-------------------------------------------------------------")
        if args.skipClients == False:
            numEntries, numOk, numSkips, numErr = cl.syncClients(ws)
        else:
            numEntries=0
            numOk=0
            numSkips=0
            numErr=0
            logger.info("... skipping phase 1")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 1 of 4 (Import clients) completed (entries=%d, ok=%d, skips=%d, err=%d)"%(numEntries, numOk, numSkips, numErr))
        logger.info("-------------------------------------------------------------")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 2 of 4: Import tags")
        logger.info("-------------------------------------------------------------")
        if args.skipTags == False:
            numEntries, numOk, numSkips, numErr = cl.syncTags(ws)
        else:
            numEntries=0
            numOk=0
            numSkips=0
            numErr=0
            logger.info("... skipping phase 2")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 2 of 4 (Import tags) completed (entries=%d, ok=%d, skips=%d, err=%d)"%(numEntries, numOk, numSkips, numErr))
        logger.info("-------------------------------------------------------------")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 3 of 4: Import projects")
        logger.info("-------------------------------------------------------------")
        if args.skipProjects == False:
            numEntries, numOk, numSkips, numErr = cl.syncProjects(ws)
        else:
            numEntries=0
            numOk=0
            numSkips=0
            numErr=0
            logger.info("... skipping phase 3")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 3 of 4 (Import projects) completed (entries=%d, ok=%d, skips=%d, err=%d)"%(numEntries, numOk, numSkips, numErr))
        logger.info("-------------------------------------------------------------")        
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 4 of 4: Import time entries")
        logger.info("-------------------------------------------------------------")
        if args.skipEntries == False:
            numEntries, numOk, numSkips, numErr = cl.syncEntries(ws, startTime)
        else:
            numEntries=0
            numOk=0
            numSkips=0
            numErr=0
            logger.info("... skipping phase 3")
        
        logger.info("-------------------------------------------------------------")
        logger.info("Phase 4 of 4 (Import entries) completed (entries=%d, ok=%d, skips=%d, err=%d)"%(numEntries, numOk, numSkips, numErr))
        logger.info("-------------------------------------------------------------")
        
        logger.info("finished importing workspace '%s'"%(ws))
        idx+=1