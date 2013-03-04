import xbmcplugin, xbmcgui, xbmcaddon, urllib, urlparse, mlslive

__settings__ = xbmcaddon.Addon(id='plugin.video.mlslive')
__language__ = __settings__.getLocalizedString


GAME_IMAGE_PREFIX = 'http://e2.cdnl3.neulion.com/mls/ced/images/roku/HD/'


def createFinalMenu(my_mls, values_string):
    print "MICAH '" + values_string + "'"
    values = dict(urlparse.parse_qsl(values_string))
    streams = my_mls.getFinalStreams(values['id'])
    for key in streams.keys():
        title = my_mls.adjustArchiveString(values['title'], key)
        li = xbmcgui.ListItem(title, iconImage=values['image'])
        li.setInfo( type="Video", infoLabels={"Title" : title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=streams[key],
                                    listitem=li,
                                    isFolder=False)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def createMainMenu(my_mls):
    """
    Create the main menu consisting of the days games
    """

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

        if my_mls.isGameLive(game):
            stream = my_mls.getGameLiveStream(game['gameID'])

            li.setInfo( type="Video", infoLabels={"Title" : game_str})
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                        url=stream,
                                        listitem=li,
                                        isFolder=False)
        elif my_mls.isGameUpcomming(game):
            li.setInfo( type="Video", infoLabels={"Title" : game_str})
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                        listitem=li,
                                        isFolder=False)
        else:
            values = { 'image' : game_img,
                       'title' : game_str,
                       'id' : game['gameID'] }
            url = sys.argv[0] + "?" + urllib.urlencode(values);

            li.setInfo( type="Video", infoLabels={"Title" : game_str})
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                        url=url,
                                        listitem=li,
                                        isFolder=True)

    # signal the end of the directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def authenticate():
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
        return None

    return my_mls

my_mls = authenticate()

if my_mls == None:
    print "ERROR: Unable to authenticate"
elif (len(sys.argv[2]) == 0):
    createMainMenu(my_mls)
elif sys.argv[2][:3] == '?id':
    createFinalMenu(my_mls, sys.argv[2][1:])
