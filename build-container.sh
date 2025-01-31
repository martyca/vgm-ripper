#!/bin/bash
docker build -t vgm-ripper .

echo "Container image 'vgm-ripper' buid, run by running the following command:"
echo 'docker run -it -v $(pwd):/downloads vgm-ripper https://downloads.khinsider.com/game-soundtracks/album/minecraft --quality high'