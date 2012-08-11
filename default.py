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

GAME_IMAGE_PREFIX = 'http://e2.cdnl3.neulion.com/mls/ced/images/roku/HD/'

def getPrettyTitle(game):
    """
    Get the pretty title of the game.
    
    @param game: The game
    """
    pretty = time.strftime("%H:%M", game.time) + " "
    
    # append the pretty name if we know the away team, otherwise, use the abbr
    if game.away in team_string.keys():
        pretty += __language__(team_string[game.away])
    else:
        pretty += game.away
    pretty += " " + __language__(30008) + " "
    
    # append the pretty name if we know the home team, otherwise, use the abbr
    if game.home in team_string.keys():
        pretty += __language__(team_string[game.home])
    else:
        pretty += game.home
    
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

        # get the pretty title        
        game_str = getPrettyTitle(game)

        # add the live list
        game_img = GAME_IMAGE_PREFIX + game.away + "_at_" + game.home + ".jpg";
        li = xbmcgui.ListItem(game_str, iconImage=game_img)

        li.setInfo( type="Video", infoLabels={"Title" : game_str})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=game.stream,
                                    listitem=li,
                                    isFolder=False)



    # signal the end of the directory
    xbmcplugin.endOfDirectory(int(sys.argv[1]))


if (len(sys.argv[2]) == 0):
    createMainMenu()
