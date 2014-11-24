#!/bin/bash
_ci() {
    echo -e "\033[34;1m[INFO] ${1}\033[m"
}
_ce() {
    echo -e "\033[31;1m[ERROR] ${1}\033[m" 1>&2
}

ag="$@"

_cmd() {
    [ `which $1` ] && {
	_ci "================================== $1 ===================================="
        _ci "$1 test" && \
	$1 setup.py test && {
	    _ci "$1 bdist_egg"
	    $1 setup.py bdist_egg $ag && \
	    _ci "$1 sdist" && \
	    $1 setup.py sdist $ag #&& \
	    #_ci "$1 bdist_wininst" && \
	    #$1 setup.py bdist_wininst $ag
        }
    } || _ce "$1 not found"
}

_cmd python2
_cmd python3
