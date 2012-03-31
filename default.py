import xbmcplugin, xbmcgui, xbmcaddon, mlslive, urllib, time, re

__settings__ = xbmcaddon.Addon(id='plugin.video.mlslive')
__language__ = __settings__.getLocalizedString

team_string = { "CHI" : 30981,
                "CHV" : 30982,
                "COL" : 30983,
                "CLB" : 30984,
                "DC"  : 30985,
                "DAL" : 30986, 
                "HOU" : 30987,
                "KC"  : 30988,
                "LA"  : 30989,
                "MTL" : 30990,
                "NE"  : 30991,
                "NY"  : 30992,
                "PHI" : 30993,
                "POR" : 30994,
                "RSL" : 30995,
                "SJ"  : 30996,
                "SEA" : 30997,
                "TOR" : 30998,
                "VAN" : 30999 }

team_imgs = { "CHI" : "http://upload.wikimedia.org/wikipedia/en/8/84/Chicago_Fire_Soccer_Club.svg",
              "CHV" : "http://upload.wikimedia.org/wikipedia/en/f/f0/Chivas_USA_logo.svg",
              "COL" : "http://upload.wikimedia.org/wikipedia/en/2/2b/Colorado_Rapids_logo.svg",
              "CLB" : "http://upload.wikimedia.org/wikipedia/en/f/f8/Columbus_Crew_logo.svg",
              "DC"  : "http://upload.wikimedia.org/wikipedia/en/a/a4/DCUnited.png",
              "DAL" : "http://upload.wikimedia.org/wikipedia/en/c/c9/FC_Dallas_logo.svg", 
              "HOU" : "http://upload.wikimedia.org/wikipedia/en/0/0c/Houston_Dynamo_logo.svg",
              "KC"  : "http://upload.wikimedia.org/wikipedia/en/f/fc/Sportingkansascity.png",
              "LA"  : "http://upload.wikimedia.org/wikipedia/en/7/70/Los_Angeles_Galaxy_logo.svg",
              "MTL" : "http://upload.wikimedia.org/wikipedia/en/b/b0/MTL_Impact.png",
              "NE"  : "http://upload.wikimedia.org/wikipedia/en/d/d6/New_England_Revolution_logo.svg",
              "NY"  : "http://upload.wikimedia.org/wikipedia/en/5/51/New_York_Red_Bulls_logo.svg",
              "PHI" : "http://upload.wikimedia.org/wikipedia/en/7/7b/PhiladelphiaUnion.png",
              "POR" : "http://upload.wikimedia.org/wikipedia/en/d/db/PortlandTimbersMLSLogo.png",
              "RSL" : "http://upload.wikimedia.org/wikipedia/en/f/f8/Real_Salt_Lake_shield_logo.svg",
              "SJ"  : "http://upload.wikimedia.org/wikipedia/en/6/69/SanJoseEarthquakes_2008.png",
              "SEA" : "http://upload.wikimedia.org/wikipedia/en/2/27/Seattle_Sounders_FC.svg",
              "TOR" : "http://upload.wikimedia.org/wikipedia/en/7/7c/Toronto_FC_Logo.svg",
              "VAN" : "http://upload.wikimedia.org/wikipedia/en/5/5d/Vancouver_Whitecaps_FC_logo.svg" }

def getPrettyTitle(game):
    """
    Get the pretty title of the game.
    
    @param game: The game
    """
    pretty = time.strftime("%H:%M", game.time) + " "
    pretty += __language__(team_string[game.away])
    pretty += " " + __language__(30008) + " "
    pretty += __language__(team_string[game.home])
    
    return pretty 


def createMainMenu():
    """
    Create the main menu consisting of the days games
    """    

    # get the user name
    username = __settings__.getSetting("username")
    if len(username) == 0:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30000), __language__(30001))
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),
                                  succeeded=False)
        return None

    # get the password
    password = __settings__.getSetting("password")
    if len(password) == 0:
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30002), __language__(30003))
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),
                                  succeeded=False)
        return None

    # authenticate with MLS live
    my_mls = mlslive.MLSLive()
    if not my_mls.login(username, password):
        dialog = xbmcgui.Dialog()
        dialog.ok(__language__(30004), __language__(30005))
        xbmcplugin.endOfDirectory(handle = int(sys.argv[1]),
                                  succeeded=False)

    for game in my_mls.getGames():
        game_url = sys.argv[0] + "?id=" + urllib.quote_plus(game.game_id)
        #game_str = game.game_id + ": " + time.strftime("%H:%M", game.time) + \
        #           " "+ game.away + " at " + game.home
        game_str = getPrettyTitle(game)

        # add the live list
        if game.home in team_imgs.keys():
            li = xbmcgui.ListItem(game_str, iconImage=team_imgs[game.home])
        else:
            li = xbmcgui.ListItem(game_str)

        li.setInfo( type="Video", infoLabels={"Title" : game_str})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=game_url,
                                    listitem=li,
                                    isFolder=True)



    # signal the end of the directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def createStreamMenu(game_id):
    """
    Create the list of streams (each available bitrate).
    """

    my_mls = mlslive.MLSLive()
    streams = my_mls.getGameStreams(game_id)
    
    if streams == None:
        dialog = xbmcgui.Dialog()
        dialog.ok("Error", "No streams yet.")
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        return
    
    bitrates = []
    for k in streams.keys():
        bitrates.append(int(k))
    bitrates.sort()
    bitrates.reverse()

    for bitrate in bitrates:
        stream_id = str(bitrate)
        title = str(float(bitrate) / float(1000000)) + " Mbps"
        li = xbmcgui.ListItem(title)
        li.setInfo( type="Video", infoLabels={"Title" : title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=streams[stream_id],
                                    listitem=li,
                                    isFolder=False)

    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))


if (len(sys.argv[2]) == 0):
    createMainMenu()
else:
    id_match = re.match('\?id\=(\d*)', sys.argv[2])
    if id_match != None:
        try:
            game_id = id_match.group(1)
            createStreamMenu(game_id)
        except Exception, e:
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "Unable to match ID")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
