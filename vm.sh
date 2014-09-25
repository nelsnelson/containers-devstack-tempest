#! /usr/bin/env bash

source .novaconfig

nova boot --poll --image "${IMAGE}" --flavor "${FLAVOR}" devstack-tempest-01

