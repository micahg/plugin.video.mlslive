import xbmcplugin, xbmcgui, xbmcaddon, mlslive

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
        game_str = game.game_id + ": " + game.time.strftime("%H:%M") + " "+ \
                   game.away + " at " + game.home
        # add the live list
        li = xbmcgui.ListItem(game_str)
        li.setInfo( type="Video", infoLabels={"Title" : game_str})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url="M3U8 URL HERE",
                                    listitem=li,
                                    isFolder=False)



    # signal the end of the directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


if (len(sys.argv[2]) == 0):
    createMainMenu()