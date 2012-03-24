import xbmcplugin, xbmcgui, xbmcaddon, mlslive, urllib, time, re

__settings__ = xbmcaddon.Addon(id='plugin.video.mlslive')
__language__ = __settings__.getLocalizedString


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
        game_str = game.game_id + ": " + time.strftime("%H:%M", game.time) + \
                   " "+ game.away + " at " + game.home
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
    
    print "CREATE STREAM MENU\n"
    
    my_mls = mlslive.MLSLive()
    streams = my_mls.getGameStreams(game_id)
    
    print "STREAMS\n"
    
    if streams == None:
        dialog = xbmcgui.Dialog()
        dialog.ok("Error", "No streams yet.")
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        return
    
    for k in streams.keys():
        print "BITRATE '" + k + "'\n"
        li = xbmcgui.ListItem(k)
        li.setInfo(type="Video", infoLabels={"Title" : k})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=streams[k],
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
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok("Error", "Unable to match ID")
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
#elif sys.argv[2] == '?id=FINAL':