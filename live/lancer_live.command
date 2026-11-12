#!/bin/bash
# Lance le village : le serveur (relié à ton live TikTok) + une fenêtre Chrome où le son démarre tout seul.
cd "$(dirname "$0")"
[ -d node_modules ] || npm install
npm start &
sleep 3
open -na "Google Chrome" --args --user-data-dir=/tmp/village-live --autoplay-policy=no-user-gesture-required \
  --app=http://localhost:3000 --window-size=540,960
wait
