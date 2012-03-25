import xbmcplugin, xbmcgui, xbmcaddon, mlslive, urllib, time, re

__settings__ = xbmcaddon.Addon(id='plugin.video.mlslive')
__language__ = __settings__.getLocalizedString

team_string = { "CHI" : 30981,
                "CHV" : 30982,
                "COL" : 30983,
                "CLB" : 30984,
                "DC" : 30985,
                "DAL" : 30986, 
                "HOU" : 30987,
                "KC" : 30988,
                "LA" : 30989,
                "MTL" : 30990,
                "NE" : 30991,
                "NY" : 30992,
                "PHI" : 30993,
                "POR" : 30994,
                "RSL" : 30995,
                "SJ" : 30996,
                "SEA" : 30997,
                "TOR" : 30998,
                "VAN" : 30999 }

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
#?id=429877
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
