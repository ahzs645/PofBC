#!/usr/bin/env bash
# Fetches one submodule at the commit this repository pins, shallowly, retrying when the network
# fails. Deploys used to check every submodule out in full through actions/checkout, about 2 GB of
# tool repositories, and a single timeout on one of them failed the whole deploy.
#
#   fetch-submodule.sh <path> [<directory> ...]
#
# With directories, only those (and the repository's top-level files) are checked out: PlateForge's
# embed lives in src/, and its 500 MB of docs and public assets are never used by this site.
# A submodule's own submodules are fetched the same way (brandkit has three).
set -euo pipefail

self="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
path="$1"; shift
sparse=("$@")
url="$(git config -f .gitmodules --get "submodule.${path}.url")"
sha="$(git ls-tree HEAD "$path" | awk '{print $3}')"
if [ -z "$url" ] || [ -z "$sha" ]; then
  echo "::error::${path} is not a submodule of this commit"
  exit 1
fi

# The same retry for every network step: three tries, 10 s then 30 s apart.
retry() {
  local delay=10
  for attempt in 1 2 3; do
    if "$@"; then return 0; fi
    [ "$attempt" = 3 ] && break
    echo "::warning::${path}: attempt ${attempt} failed; retrying in ${delay} s"
    sleep "$delay"; delay=30
  done
  echo "::error::${path}: could not fetch ${sha} from ${url}"
  return 1
}

rm -rf "$path"
git init --quiet "$path"
git -C "$path" remote add origin "$url"
if [ "${#sparse[@]}" -gt 0 ]; then
  git -C "$path" sparse-checkout set "${sparse[@]}"
fi
# GitHub serves any commit by its hash, so the pinned commit is fetched alone, with no history.
retry git -C "$path" fetch --quiet --depth 1 --filter=blob:none origin "$sha"
retry git -C "$path" checkout --quiet --detach FETCH_HEAD

# Nested submodules, which the sparse fetch above never needs.
if [ -f "$path/.gitmodules" ] && [ "${#sparse[@]}" -eq 0 ]; then
  (cd "$path" && git config -f .gitmodules --get-regexp '^submodule\..*\.path$' | while read -r _ nested; do
    "$self" "$nested"
  done)
fi
echo "  ${path} at ${sha:0:7}${sparse:+ (only ${sparse[*]})}"
