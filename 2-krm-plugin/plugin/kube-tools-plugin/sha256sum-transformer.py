#!/usr/bin/env python3

import hashlib
import yaml
import io, sys, os
import logging

def addAnnotation(item, annotation, value):
    logger = logging.getLogger(__name__)
    try:
        item['spec']['template']['metadata'].setdefault('annotations', {})[annotation] = value
        logger.debug(item['metadata']['name'])
    except KeyError:
        logger.exception("Could not annotate: %s", str(item))
        raise

def calculateChecksum(files):
    logger = logging.getLogger(__name__)
    #main function, add for all file paths in spec checksum
    m = hashlib.sha256()
    for item in files:
        for dirpath, dnames, fnames in os.walk(item):
            for file in fnames:
                with open(os.path.join(dirpath, file), "rb") as f:
                    logger.debug(file)
                    #TODO this would not work well for big files
                    m.update(f.read())
    return m.hexdigest()

def run_transformer():
    logger = logging.getLogger(__name__)
    #kustomize KRM sends resourcelist via stdin
    resourcelist = yaml.safe_load(sys.stdin.read())

    #function's config is embedded in the resourcelist
    config = resourcelist["functionConfig"]

    logger.debug(yaml.safe_dump(config))

    files = config['spec']['files']
    checksum = calculateChecksum(files)

    if 'annotation' in config['spec']:
        annotation = config['spec']['annotation']

    for item in resourcelist['items']:
        if 'kind' in config['spec']:
            #update every kind with checksum
            for kind in config['spec']['kind']:
                if item['kind'] == kind:
                    addAnnotation(item,annotation,checksum)

    logger.debug(yaml.safe_dump(resourcelist))

    #now output the updated resourcelist, kustomize will filter the items
    print(yaml.safe_dump(resourcelist))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    run_transformer()
