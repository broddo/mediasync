# mediasync
This is a simple Python script to sync user accounts and their respective TV show and movies watch statuses between 'MediaBrowser' derivatives such as Emby and Jellyfin. It can sync from Emby to Jellyfin, Jellyfin to Emby and indeed Emby to Emby and Jellyfin to Jellyfin. 

This project was inspired by [Emby2Jelly](https://github.com/Marc-Vieg/Emby2Jelly) 

Similar to Emby2Jelly, the script matches items in both libraries using their provider IDs (Tvdb, Imdb, etc) so be sure that both servers recognise all their files and that their metadata is up-to-date. If no match is found using proivder IDs, the script will match an item using its path. This method is particularly useful if both servers are pointing at the same source files. 

## Requirements
Emby server Version : **4.7.10.0**

Jellyfin server Version : **10.8.8**

Python **3.9**

The script should work on older versions of both Emby and Jellyfin as their respective APIs haven't changed much. 

## Installation
I've provided a setup.py file so that the script can be installed. Just run the following from the root of the project directory to install it:
```
python3 -m pip install .
```

Once installed, the script can be run by typing:
```
mediasync settings.json sync
```

If you choose not to install, just run mediasyncmain.py file from the mediasync directory instead:
```
python3 mediasync.py settings.json sync
```

## Configuration
A JSON settings file is required in order to provide the script with the API keys and URLs of your servers. An example of this file is provided in the repository, called `settings.json`. You will need to create API keys in both your source and destination servers. Please refer to Emby/Jellyfin documentation in order to find out how to do this. 

Here is an example configuration. 

```
{
    "source": {
        "type": "Emby",
        "apikey": "12eedf87b52d42a20a0c970f701fdfa4",
        "url": "https://emby.myserver.com"
    },
    "destination": {
        "type": "Jellyfin",
        "apikey": "ebcb271e854c4f97b1f9a80db87078f6",
        "url": "localhost:8096/jellyfin"
    },
}
```

## Options
### Sync option 
```
mediasync settings.json sync
```
The sync option synchronizes the watch-list from the source server to the destination server. Missing users are created on the destination server and given a long random password by default (a default password can be provided with the -p option).

### Diff option
```
mediasync settings.json diff
```
The diff option compares media items on the source server to the destination server. Any items that cannot be matched are printed out for the user to examine. This can be useful to run first to make sure that the majority of your files have been recognized correctly by your media servers
