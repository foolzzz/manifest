#!/usr/bin/python

# Copyright 2016 <github.com/duanqz>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Generate local_manifests

Usage: $local_manifest.py [URL] [BRANCH]
         - URL: url of the remote local_manifests. If not present, url of current manifest will be used
         - BRANCH: branch of the remote local_manifests. If not present, default branch will be used
"""

import os
import sys
import re
import subprocess


def _find_top_dir():
    """
    :return: the absolute path of '.repo'
    """

    # If '.repo' not exists in current directory, then go to the parent directory
    d = os.path.abspath(os.curdir)
    old = d
    while d != "/" and not os.path.exists(os.path.join(d, ".repo")):
        d = os.path.abspath(os.path.pardir)
        os.chdir(d)
    os.chdir(old)

    return os.path.join(d, ".repo")


def _get_output(cmd):
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=open(os.devnull, 'w')).communicate()


def _adjust_url(top, url):
    if url is not None:
        return url

    # Phase 1: Change to manifests directory
    old = os.path.abspath(os.curdir)
    manifest_dir = os.path.join(top, "manifests")
    os.chdir(manifest_dir)

    # Phase 2: Execute command 'git config -l'
    cmd = 'git config -l'
    out, err = _get_output(cmd)
    os.chdir(old)

    if err is not None:
        print "Can not find git command."
        return None

    # Phase 3: Match out current url with regex
    url_regex = re.compile("\nremote.*url\s*=\s*(?P<url>.*)\n")
    url_match = url_regex.search(out)

    if url_match is None:
        print "Not in a android git repository."
        return None

    # Phase 4: Retrieve the remote url
    url = url_match.group("url")
    url = url.replace("manifests.git", "local_manifests.git")
    return url


def generate(url=None, branch=None):
    """
    Generate local_manifests
    :return 0 means
    """

    top = _find_top_dir()
    url = _adjust_url(top, url)
    if url is None:
        print "Can not find url of the remote local_manifests repository."
        return False

    local_dir = os.path.join(top, "local_manifests")
    # clone the url to generate local_manifests directory
    cmd = "git clone %s %s" % (url, local_dir)

    if branch is not None:
        cmd += " -b %s" % branch

    print "Run %s" % cmd
    return os.system(cmd) == 0

if __name__ == '__main__':
    local_manifests_url = local_manifests_branch = None
    argc = len(sys.argv)
    if argc > 1:
        if sys.argv[1] in ("-h", "--help"):
            print __doc__
            sys.exit(1)
        elif sys.argv[1].startswith("http") or sys.argv[1].startswith("git") or sys.argv[1].startswith("ssh"):
            local_manifests_url = sys.argv[1]
        else:
            local_manifests_branch = sys.argv[1]

    if argc > 2:
        local_manifests_branch = sys.argv[2]

    if generate(local_manifests_url, local_manifests_branch):
        exit(0)
    else:
        exit(1)