#!/bin/bash
colonies fs sync -l /openeo/src -d ./src --yes
colonies function submit --spec mail.json --follow
