import xbmcplugin, xbmcgui, xbmcaddon, mlslive, urllib, time, re

__settings__ = xbmcaddon.Addon(id='plugin.video.mlslive')
__language__ = __settings__.getLocalizedString


GAME_IMAGE_PREFIX = 'http://e2.cdnl3.neulion.com/mls/ced/images/roku/HD/'


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

    # get the teams
    teams = my_mls.getTeams()

    for game in my_mls.getGames(0):

        # get the pretty title        
        game_str = my_mls.getGameString(game, __language__(30008))

        # get the home/away images
        home = my_mls.getTeamAbbr(teams, game['homeTeamID'])
        vist = my_mls.getTeamAbbr(teams, game['visitorTeamID'])
        game_img = GAME_IMAGE_PREFIX + vist + "_at_" + home + ".jpg";

        li = xbmcgui.ListItem(game_str, iconImage=game_img)

        stream = my_mls.getGameStream(game['gameID'])

        li.setInfo( type="Video", infoLabels={"Title" : game_str})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=stream,
                                    listitem=li,
                                    isFolder=False)



    # signal the end of the directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


if (len(sys.argv[2]) == 0):
    createMainMenu()
