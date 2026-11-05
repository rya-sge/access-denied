#!/bin/sh
# Regenerates every result quoted in the article. Runs offline, standard library only.
set -e
cd "$(dirname "$0")"
(cd vectors && sha256sum --check --quiet ssz-test-vectors-v0.1.0.tar.gz.sha256)
python3 -I python/check_vectors.py | tee results/vectors.txt
python3 -I python/check_mainnet.py | tee results/mainnet.txt
python3 -I python/examples.py > results/examples.txt
python3 -I python/measure_sizes.py > results/sizes.txt
python3 -I python/measure_hashing.py > results/hashing.txt
python3 -I python/gen_fixtures.py
forge test --offline -vv | tee results/forge.txt | tail -3
