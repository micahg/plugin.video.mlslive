"""
@author: Micah Galizia <micahgalizia@gmail.com>

This class provides the helper calls to view the MLS Live streams.
"""

import urllib, urllib2, xml.dom.minidom, json, cookielib, time, datetime

class MLSLive:

    def __init__(self):
        """
        Initialize the MLSLive class.
        """
        self.LOGIN_PAGE = 'https://live.mlssoccer.com/mlsmdl/secure/login'
        self.GAMES_PAGE_PREFIX = 'http://mobile.cdn.mlssoccer.com/iphone/v5/prod/games_for_week_'
        self.GAMES_PAGE_SUFFIX = '.js'
        
        # Odd, but the year is still 2011 -- I expect this will change in the future
        self.GAME_PREFIX = 'http://mls.cdnak.neulion.com/mobile/feeds/game/2011/'
        self.GAME_SUFFIX = '_ced.xml'

        self.TEAM_PAGE = 'http://mobile.cdn.mlssoccer.com/iphone/v5/prod/teams_2013.js'


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
        
        self.jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        try:
            resp = opener.open(self.LOGIN_PAGE, urllib.urlencode(values))
        except:
            print "Unable to login"
            return False

        resp_xml = resp.read()
        dom = xml.dom.minidom.parseString(resp_xml)
        
        result_node = dom.getElementsByTagName('result')[0]
        code_node = result_node.getElementsByTagName('code')[0]
        
        if code_node.firstChild.nodeValue == 'loginsuccess':
            return True
        
        return False


    def getGames(self, week_offset):
        """
        Get the list of games.
        
        @param week_offset the number of weeks to offset from the previous
                           monday.

        The list returned will contain dictionaries, each of which containing
        game details. The details are as follows:
        - homeTeamScore
        - visitorTeamScore
        - gameID
        - siteName (eg: "PPL Park", the nicest park in the league IMO)
        - television (eg: "MLS LIVE", "NBCSN", "ESPN2"
        - visitorTeamID
        - homeTeamID
        - gameDateTime (eg: "20130302T210000+0000")
        - competitionID (not sure what that does)
        - homeTeamName (pretty home team name)
        - gameStatus ("FINAL","UPCOMING", "LIVE - 50'"
        - visitorTeamName (pretty vistor team name)
        """
        today = datetime.date.today()
        monday = today + datetime.timedelta(days=-today.weekday(), weeks=week_offset)
        monday_str = monday.strftime("%Y-%m-%d")
        games_url = self.GAMES_PAGE_PREFIX + monday_str + self.GAMES_PAGE_SUFFIX

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        try:
            resp = opener.open(games_url)
        except:
            print "Unable to load game list."
            return None

        json_data = resp.read()

        games = json.loads(json_data)['games']

        return games


    def getTeams(self):
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        try:
            resp = opener.open(self.TEAM_PAGE)
        except:
            print "Unable to load game list."
            return None

        json_data = resp.read()

        return json.loads(json_data)['teams']


    def getTeamAbbr(self, teams, id):
        for team in teams:
            if str(team['teamID']) == str(id):
                return team['abbr']
        return  None


    def getGameDateTimeStr(self, game_date_time):
        """
        Convert the date time stamp from GMT to local time
        @param game_date_time the game time (in GMT)
        """

        # We know the GMT offset is 0, so just get rid of the trailing offset
        time_parts = game_date_time.split('+')
        game_t = time.strptime(time_parts[0], "%Y%m%dT%H%M%S")
        game_dt = datetime.datetime.fromtimestamp(time.mktime(game_t))

        # get the different between now and utc
        td = datetime.datetime.utcnow() - datetime.datetime.now()

        # subtract that difference from the game time (to put it into local gime)
        game_dt = game_dt - td

        # return a nice string
        return game_dt.strftime("%m/%d %H:%M")


    def isGameLive(self, game):
        if game['gameStatus'][:4] == 'LIVE':
            return True
        return False


    def isGameUpcomming(self, game):
        if game['gameStatus'][:8] == 'UPCOMING':
            return True
        return False


    def adjustArchiveString(self, title, archive_type):
        new_title = title.split('(')[0]
        return new_title + '(' + archive_type.title().replace('_', ' ') + ')';


    def getGameString(self, game, separator):

        game_str = game['visitorTeamName'] + " " + separator + " " + \
                   game['homeTeamName']

        if game['gameStatus'] == 'FINAL' or game['gameStatus'][:4] == 'LIVE':
            game_str += ' (' + game['gameStatus'].title() + ')'
        else:
            game_str += ' (' + self.getGameDateTimeStr(game['gameDateTime']) + ')'

        return game_str


    def getGameXML(self, game_id):
        game_xml_url = self.GAME_PREFIX + game_id + self.GAME_SUFFIX
        self.jar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        try:
            resp = opener.open(game_xml_url)
        except:
            print "Unable to get game XML configuration"
            return ""

        game_xml = resp.read()
        return game_xml


    def getFinalStreams(self, game_id):
        game_xml = self.getGameXML(game_id)
        dom = xml.dom.minidom.parseString(game_xml)
        rss_node = dom.getElementsByTagName('rss')[0]
        chan_node = rss_node.getElementsByTagName('channel')[0]
        games = {}
        for item in chan_node.getElementsByTagName('item'):
            # get the game type
            game_type = item.getElementsByTagName('nl:type')[0].firstChild.nodeValue

            # get the group list and make sure its valid
            group_list = item.getElementsByTagName('media:group')
            if group_list == None or len(group_list) == 0:
                continue

            # get the content node and then the URL
            content_node = group_list[0].getElementsByTagName('media:content')[0]
            games[game_type] = content_node.getAttribute('url')

        return games


    def getGameLiveStream(self, game_id):
        """
        Get the game streams. This method will parse the game XML for the
        HLS playlist, and then parse that playlist for the different bitrate
        streams.

        @param game_id: The ID of the game.
        """
        game_xml = self.getGameXML(game_id)

        dom = xml.dom.minidom.parseString(game_xml)

        rss_node = dom.getElementsByTagName('rss')[0]
        chan_node = rss_node.getElementsByTagName('channel')[0]
        url = ""
        for item in chan_node.getElementsByTagName('item'):

            # get the group list and make sure its valid
            group_list = item.getElementsByTagName('media:group')
            if group_list == None or len(group_list) == 0:
                continue

            # get the content node and then the URL
            content_node = group_list[0].getElementsByTagName('media:content')[0]
            url = content_node.getAttribute('url')
            break

        return url
