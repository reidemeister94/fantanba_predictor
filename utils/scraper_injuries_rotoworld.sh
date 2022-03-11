#!/bin/bash

curl -S http://www.rotoworld.com/teams/injuries/nba/all/ | \
pup 'div#cp1_pnlInjuries tr json{}' | \
jq '[.[] | {name: .children[0].children[0].text, pos: .children[2].text, status: .children[3].text, date: .children[4].text, injury: .children[5].text, returns: .children[6].text} | select(.date != null)]' > ../data/injuries_rotoworld.json
