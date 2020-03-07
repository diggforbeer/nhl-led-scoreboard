import requests
import datetime
import json
from utils import convert_time
import debug

NHL_API_URL = "http://statsapi.web.nhl.com/api/v1/"
NHL_API_URL_BASE = "http://statsapi.web.nhl.com"

COLORS = {"1":"206,17,38","2":"0,83,155","3":"0,56,168","4":"247,73,2","5":"252,181,20","6":"252,181,20","7":"0,38,84","8":"175,30,45","9":"197,32,50","10":"0,32,91","12":"226,24,54","13":"4,30,66","14":"0,40,104","15":"200,16,46","16":"207,10,44","17":"206,17,38","18":"255,184,28","19":"0,47,135","20":"200,16,46","21":"111,38,61","22":"252,76,0","23":"0,32,91","24":"252,76,2","25":"0,104,71","26":"162,170,173","28":"0,109,117","29":"0,38,84","30":"2,73,48","52":"4,30,66","53":"140,38,51","54":"185,151,91"}

# TEST_URL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2018-01-02&endDate=2018-01-02"
def get_teams():
    """
        Function to get a list of all the teams information
        The info for each team are store in multidimensional dictionary like so:
        {
            team ID{
                team name,
                location,
                abbreviation,
                conference name,
                division name
            }
        }
        This make it a lot simpler to call each info of a specific team as all info in the API are associated with a team ID
    """
    url = '{0}/teams'.format(NHL_API_URL)
    response = requests.get(url)
    results = response.json()
    teams = {}
    try:
        for team in results['teams']:
            team_id = str(team['id'])
            info_dict = {'name': team['teamName'], 'location': team['locationName'],
                         'abbreviation': team['abbreviation'], 'conference': team['conference']['name'],
                         'division': team['division']['name'], 'rgb': COLORS[team_id]}
            teams[team['id']] = info_dict
        return teams
    except requests.exceptions.RequestException:
        print("Error encountered getting teams info, Can't reach the NHL API")


def fetch_live_stats(link):
    """ Function to get the live stats of the current game """
    url = '{0}{1}'.format(NHL_API_URL_BASE, link)
    response = requests.get(url)
    stuff = response.json()
    try:
        current_period = int(stuff['liveData']['linescore']['currentPeriod'])
        home_sog = int(stuff['liveData']['linescore']['teams']['home']['shotsOnGoal'])
        away_sog = int(stuff['liveData']['linescore']['teams']['away']['shotsOnGoal'])
        home_powerplay = int(stuff['liveData']['linescore']['teams']['home']['powerPlay'])
        away_powerplay = int(stuff['liveData']['linescore']['teams']['away']['powerPlay'])
        try:
            time_remaining = stuff['liveData']['linescore']['currentPeriodTimeRemaining']
        except KeyError:
            time_remaining = "00:00"
        return current_period, home_sog, away_sog, home_powerplay, away_powerplay, time_remaining
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")


def fetch_games():
    """
    Function to get a list of games

    request stats in json form from the schedule section of the NHL API URL
    create a list to store all the games
    loop through the games received and store the info in the created list:
        - for each games:
            - the ID of the game
            - the link to the complete stats of that game
            - the Home team
            - the Home team score
            - the Away team
            - the Away team score
            - game status

    finally return the list of games

    game_list = list of all the games and the number of games.
    url = the location where we can find the list of games.
    """

    url = '{0}schedule'.format(NHL_API_URL)

    game_list = []
    try:
        game_data = requests.get(url)
        game_data = game_data.json()
        games = game_data['dates'][0]['games']
        for game in range(len(games)):
            live_stats_link = game_data['dates'][0]['games'][game]['link']
            game_id = int(game_data['dates'][0]['games'][game]['gamePk'])
            home_team_id = int(game_data['dates'][0]['games'][game]['teams']['home']['team']['id'])
            home_score = int(game_data['dates'][0]['games'][game]['teams']['home']['score'])
            away_team_id = int(game_data['dates'][0]['games'][game]['teams']['away']['team']['id'])
            away_score = int(game_data['dates'][0]['games'][game]['teams']['away']['score'])
            game_status = int(game_data['dates'][0]['games'][0]['status']['statusCode'])
            game_time = convert_time(game_data["dates"][0]["games"][game]["gameDate"]).strftime("%I:%M")

            gameInfo = {"gameid": game_id, "full_stats_link": live_stats_link, "home_team_id": home_team_id,
                        "home_score": home_score, "away_team_id": away_team_id, "away_score": away_score,
                        'game_status': game_status, 'game_time': game_time}

            game_list.append(gameInfo)
        return game_list
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
        return 0
    except IndexError:
        print("No Game today")
        return game_list


def fetch_overview(team_id):
    """ Function to get the score of the game live depending on the chosen team.
    Inputs the team ID and returns the score found on web. """

    # Set URL depending on team selected
    url = '{0}schedule?expand=schedule.linescore&teamId={1}'.format(NHL_API_URL, team_id)

    try:
        game_data = requests.get(url)
        game_data = game_data.json()

        period = game_data['dates'][0]['games'][0]['linescore']['currentPeriodOrdinal']
        time = game_data['dates'][0]['games'][0]['linescore']['currentPeriodTimeRemaining']
        home_team_id = int(game_data['dates'][0]['games'][0]['teams']['home']['team']['id'])
        home_score = int(game_data['dates'][0]['games'][0]['teams']['home']['score'])
        away_team_id = int(game_data['dates'][0]['games'][0]['teams']['away']['team']['id'])
        away_score = int(game_data['dates'][0]['games'][0]['teams']['away']['score'])
        game_status = int(game_data['dates'][0]['games'][0]['status']['statusCode'])
        game_time = convert_time(game_data["dates"][0]["games"][0]["gameDate"]).strftime("%I:%M")

        current_game_overview = {'period': period, 'time': time, 'home_team_id': home_team_id, 'home_score': home_score,
                                 'away_team_id': away_team_id, 'away_score': away_score, 'game_status': game_status,
                                 'game_time': game_time}

        return current_game_overview
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
        return 0
    except KeyError:
        print("missing data from the game. Game has not begun or is not scheduled today.")

def fetch_fav_team_schedule(team_id):
    """ Function to get the summary of a scheduled game. """
    # Set URL depending on team selected
    now = datetime.datetime.now()
    url = '{0}schedule?teamId={1}&date={2}'.format(NHL_API_URL, team_id,now.strftime("%Y-%m-%d"))

    try:
        game_data = requests.get(url)
        game_data = game_data.json()

        home_team_id = int(game_data['dates'][0]['games'][0]['teams']['home']['team']['id'])
        away_team_id = int(game_data['dates'][0]['games'][0]['teams']['away']['team']['id'])

        game_time = convert_time(game_data["dates"][0]["games"][0]["gameDate"]).strftime("%I:%M")

        current_game_schedule = {'home_team_id': home_team_id, 'away_team_id': away_team_id, 'game_time': game_time}

        return current_game_schedule
    except requests.exceptions.RequestException:
        print("Error encountered, Can't reach the NHL API")
        return 0
    except KeyError:
        print("missing data from the game. Game has not begun or is not scheduled today.")


def check_season():
    """ Function to check if in season. Returns True if in season, False in off season. """
    # Get current time
    now = datetime.datetime.now()
    if now.month in (7, 8):
        return False
    else:
        return True


def check_if_game(team_id):
    """ Function to check if there is a game now with chosen team. Returns True if game, False if NO game. """
    # Set URL depending with team selected
    now = datetime.datetime.now()
    url = '{0}schedule?teamId={1}&date={2}'.format(NHL_API_URL, team_id,now.strftime("%Y-%m-%d"))
    try:
        game_data = requests.get(url)
        game_data = game_data.json()
        game = game_data["totalGames"]
        debug.info(game_data)
        if game != 0:
            status = int(game_data["dates"][0]["games"][0]['status']['statusCode'])
            return status
        else:
            return False
    except requests.exceptions.RequestException:
        # Return True to allow for another pass for test
        print("Error encountered, Can't reach the NHL API")
        return False

def fetch_team(team_id):
    url = '{0}/teams/{1}'.format(NHL_API_URL,team_id)

    try:
        teams = requests.get(url)
        teams = teams.json()
        #debug.info(teams)
        return teams["teams"][0]
    except requests.exceptions.RequestException:
        # Return True to allow for another pass for test
        print("Error encountered, Can't reach the NHL API")
        return False

def fetch_wildcard_standings(team_id):
    team = fetch_team(team_id)
    teams = get_teams()
    #debug.info(teams)
    url = '{0}/standings/wildCardWithLeaders'.format(NHL_API_URL)
    try:
        schedule_data = requests.get(url)
        schedule_data = schedule_data.json()
        #debug.info(schedule_data)
        wildcard = ""
        divison = ""

        for item in schedule_data["records"]:
            #debug.info(item)
            if (item["conference"]["id"] == team["conference"]["id"]):
                if (item["standingsType"] == "wildCard"):
                    wildcard = item["teamRecords"]
            if 'division' in item:
                if (item["division"]["id"] == team["division"]["id"]):
                    divison = item["teamRecords"]

        #add abrev back to team so we can use it.  Not sure why they left it out
        for item in wildcard:
            teamId = int(item["team"]["id"])
            item["team"]["abbreviation"] = teams[teamId]["abbreviation"]
            item["team"]["r"] = int(teams[teamId]["rgb"].split(',')[0])
            item["team"]["g"] = int(teams[teamId]["rgb"].split(',')[1])
            item["team"]["b"] = int(teams[teamId]["rgb"].split(',')[2])
            
        for item in divison:
            teamId = int(item["team"]["id"])
            item["team"]["abbreviation"] = teams[teamId]["abbreviation"]
            item["team"]["r"] = int(teams[teamId]["rgb"].split(',')[0])
            item["team"]["g"] = int(teams[teamId]["rgb"].split(',')[1])
            item["team"]["b"] = int(teams[teamId]["rgb"].split(',')[2])

        current_wildcard_standings_by_divison = {'wildcard': wildcard, 'divison': divison}
        #debug.info(json.dumps(current_wildcard_standings_by_divison, indent=2))
        return current_wildcard_standings_by_divison
    except requests.exceptions.RequestException:
        # Return True to allow for another pass for test
        print("Error encountered, Can't reach the NHL API")
        return False
    
