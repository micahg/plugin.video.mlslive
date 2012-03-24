"""
@author: Micah Galizia <micahgalizia@gmail.com>

This class provides the helper calls to view the MLS Live streams.
"""

import string, urllib, urllib2, time, xml.dom.minidom
#import datetime
#from datetime import datetime

class MLSGame:
    
    def __init__(self, game_id, game_time, home_team, away_team):
        self.game_id = game_id
        self.time = game_time
        self.home = home_team
        self.away = away_team
        

class MLSLive:
    
    
    def __init__(self):
        """
        Initialize the MLSLive class.
        """
        self.LOGIN_PAGE = 'https://live.mlssoccer.com/mlsmdl/secure/login'
        self.GAMES_PAGE = 'http://live.mlssoccer.com/mlsmdl/servlets/games?format=xml'
        
        # Odd, but the year is still 2011 -- I expect this will change in the future
        self.GAME_PREFIX = 'http://mls.cdnak.neulion.com/mobile/feeds/game/2011/'
        self.GAME_SUFFIX = '_ced.xml'


    def login(self, username, password):
        """
        Login to the MLS Live streaming service.
        
        @param username: the user name to log in with
        @param password: the password to log in with.
        @return: True if authentication is successful, otherwise, False.
        """

        # setup the login values        
        values = { 'username' : username,
                   'password' : password }
        
        req = urllib2.Request(self.LOGIN_PAGE)
        req.add_data(urllib.urlencode(values))
        # make the request and read the response
        try:
            resp = urllib2.urlopen(req)
        except:
            print "Unable to connect to MLS Live login."
            return False

        resp_xml = resp.read()
        dom = xml.dom.minidom.parseString(resp_xml)
        
        result_node = dom.getElementsByTagName('result')[0]
        code_node = result_node.getElementsByTagName('code')[0]
        
        if code_node.firstChild.nodeValue == 'loginsuccess':
            self.cookie = resp.headers.get("Set-Cookie")
            return True
        
        return False
    
    def getGames(self):
        """
        Get the list of games.
        """

        # create the request
        req = urllib2.Request(self.GAMES_PAGE)
        req.add_header('cookie', self.cookie)

        try:
            resp = urllib2.urlopen(req)
        except:
            print "Unable to connect to games list."
            return None
        
        games_xml = resp.read()
        
        # parse the XML that is returned
        dom = xml.dom.minidom.parseString(games_xml)
        result_node = dom.getElementsByTagName('result')[0]

        # the current date (according to the response)
        cur_date_node = result_node.getElementsByTagName('currentDate')[0]
        cur_date = cur_date_node.firstChild.nodeValue
        current_date = time.strptime(cur_date, "%a %b %d %H:%M:%S %Z %Y")
        
        games = []

        # loop over all games
        games_node = result_node.getElementsByTagName('games')[0]
        for game in games_node.getElementsByTagName('game'):
            
            # get the date/time for the game
            time_str = game.getElementsByTagName('gameTime')[0].firstChild.nodeValue
            game_date = time.strptime(time_str, "%Y-%m-%d %H:%M:%S.0")
            
            # skip games not from today
            game_date_str = time.strftime("%Y%m%d", game_date)
            curr_date_str = time.strftime("%Y%m%d", current_date)
            if not game_date_str == curr_date_str:
                continue
            
            # get the id, home and away team abreviations 
            game_id = game.getElementsByTagName('id')[0].firstChild.nodeValue
            away_abr = game.getElementsByTagName('awayTeam')[0].firstChild.nodeValue
            home_abr = game.getElementsByTagName('homeTeam')[0].firstChild.nodeValue
            
            game = MLSGame(game_id, game_date, home_abr, away_abr)
            
            games.append(game)

        # return the games            
        return games
    
    def getGameStreams(self, game_id):
        """
        Get the game streams. This method will parse the game XML for the
        HLS playlist, and then parse that playlist for the different bitrate
        streams.
        
        @param game_id: The ID of the game.
        """
        
        game_xml_url = self.GAME_PREFIX + game_id + self.GAME_SUFFIX
        
        # create the request
        req = urllib2.Request(game_xml_url)

        try:
            resp = urllib2.urlopen(req)
        except:
            print "Unable to connect to games list."
            return None
        
        game_xml = resp.read()
        dom = xml.dom.minidom.parseString(game_xml)
        
        rss_node = dom.getElementsByTagName('rss')[0]
        chan_node = rss_node.getElementsByTagName('channel')[0]
        url = None
        for item in chan_node.getElementsByTagName('item'):
            
            # get the group list and make sure its valid
            group_list = item.getElementsByTagName('media:group')
            if group_list == None or len(group_list) == 0:
                continue
            
            # get the content node and then the URL
            content_node = group_list[0].getElementsByTagName('media:content')[0]
            url = content_node.getAttribute('url')
            break
        
        if url == None:
            print "Unable to get m3u8 playlist."
            return None
            
        return self.getStreamsFromPlayList(url)


    def getStreamsFromPlayList(self, playlist):
        """
        Get the streams from the playlist
        
        @param playlist: The playlist URI
        """
        # create the request
        req = urllib2.Request(playlist)

        # request the games        
        try:
            resp = urllib2.urlopen(req)
        except urllib2.URLError, ue:
            print("URL error trying to open playlist")
            return None
        except urllib2.HTTPError, he:
            print("HTTP error trying to open playlist")
            return None
        
        # store the base URI from the playlist
        prefix=playlist[0:string.rfind(playlist,'/') + 1]
        lines = string.split(resp.read(), '\n')

        # parse the playlist file
        streams = {}
        bandwidth = ""
        for line in lines:
            
            # skip the first line
            if line == "#EXTM3U":
                continue
            
            # is this a description or a playlist
            idx = string.find(line, "BANDWIDTH=")
            if idx > -1:
                # handle the description
                bandwidth = line[idx + 10:len(line)]
            elif len(line) > 0:
                # add the playlist
                streams[bandwidth] = prefix + line

        return streams
