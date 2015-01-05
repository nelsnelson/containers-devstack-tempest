containers-devstack-tempest
===========================

This code attempts to orchestrate the deployment of the devstack-gate tests to a single public cloud vm, and executes them.

## Setup

    rm -rf .venv

    virtualenv .venv
    source .venv/bin/activate
    pip install --upgrade --requirement requirements.txt

    cp config.sample .config

## Running

    ./stack.py

    # To delete any existing vms created with this script
    ./stack.py --reset

## Questions?

[nels.nelson@rackspace.com](mailto:nels.nelson@rackspace.com)
