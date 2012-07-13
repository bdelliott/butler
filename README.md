butler
======

Scripts for moving and re-encoding Tivo videos.


Notes:

-Media Access Key: "Tivo secret key for web server access"
-Set MAK environ variable to Media Access Key

-Tivo exports 2 MPEG file types: PS
-http://www.tivocommunity.com/tivo-vb/showthread.php?t=446728

-Tivo web URL: https://<tivo>/nowplaying/index.html

TiVo MPEG PS URL response headers:

DEBUG 2012-07-13 15:09:10,840 net: 
{'transfer-encoding': 'chunked',
 'connection': 'close',
 'tivo-estimated-length': '1038090240',
 'content-type': 'video/x-tivo-mpeg',
 'server': 'tivo-httpd-1:20.2.1.2-01-2:748'}
