#!/usr/bin/env bash

mkdir -p keystore
cp ../tests/data/alice.key keystore
cp ../tests/data/bob.key keystore

echo '[aut]' > .autrc
echo "rpc_endpoint = ${RPC_URL:-https://rpc1.piccadilly.autonity.org/}" >> .autrc
echo 'keystore = keystore' >> .autrc
echo 'keyfile = keystore/alice.key' >> .autrc
