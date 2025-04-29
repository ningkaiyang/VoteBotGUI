#!/bin/bash

# Determine the script's directory to reliably find voteBot.js
# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# node "${SCRIPT_DIR}/voteBot.js"

# Simpler approach assuming it's run from the correct directory or node path is set
# The looping and delay logic is now handled inside voteBot.js
node voteBot.js