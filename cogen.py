#!/usr/bin/env python
import os, sys, json, distutils.core

config = json.load(open(os.path.join(os.path.dirname(__file__), 'configuration.json')))

print config
