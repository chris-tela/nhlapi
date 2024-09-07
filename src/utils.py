import time
from . import models
from fastapi import HTTPException, status


teams = ["ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL", "DAL", "DET", "EDM", 
         "FLA", "LAK", "MIN", "MTL", "NJD", "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SJS", 
         "SEA", "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WSH", "WPG"]

pacific = ["ANA", "CGY", "EDM", "LAK", "SJS", "SEA", "VAN", "VGK"]
central = ["CHI", "COL", "DAL", "MIN", "NSH", "STL", "WPG", "UTA"]
atlantic = ["BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR"]
metropolitan = ["CAR", "CBJ", "NJD", "NYI", "NYR", "PHI", "PIT", "WSH"]


# list for current team
current_team = []

def convert_to_abbreviation(team: str):
    dic = {
        "Anaheim Ducks": "ANA",
        "Arizona Coyotes": "ARI",
        "Atlanta Thrashers": "ATL",
        "Boston Bruins": "BOS",
        "Buffalo Sabres": "BUF",
        "Calgary Flames": "CGY",
        "Carolina Hurricanes": "CAR",
        "Chicago Blackhawks": "CHI",
        "Colorado Avalanche": "COL",
        "Columbus Blue Jackets": "CBJ",
        "Dallas Stars": "DAL",
        "Detroit Red Wings": "DET",
        "Edmonton Oilers": "EDM",
        "Florida Panthers": "FLA",
        "Hartford Whalers": "HFD",
        "Los Angeles Kings": "LAK",
        "Minnesota North Stars": "MNS",
        "Minnesota Wild": "MIN",
        "Montréal Canadiens": "MTL",
        "Nashville Predators": "NSH",
        "New Jersey Devils": "NJD",
        "New York Islanders": "NYI",
        "New York Rangers": "NYR",
        "Ottawa Senators": "OTT",
        "Philadelphia Flyers": "PHI",
        "Phoenix Coyotes": "PHX",
        "Pittsburgh Penguins": "PIT",
        "Quebec Nordiques": "QUE",
        "San Jose Sharks": "SJS",
        "Seattle Kraken": "SEA",
        "St. Louis Blues": "STL",
        "Tampa Bay Lightning": "TBL",
        "Toronto Maple Leafs": "TOR",
        "Utah Hockey Club" : "UTA",
        "Vancouver Canucks": "VAN",
        "Vegas Golden Knights": "VGK",
        "Washington Capitals": "WSH",
        "Winnipeg Jets": "WPG",
        "Winnipeg Jets (1979)": "WIN"
    }
    return dic[team]
    


def update_current_team() -> str:
    # clear list to get new team
    if len(current_team) > 0:
        current_team.clear()
    # remove first entry from teams list
    curr = teams.pop(0)
    # append item to current_team list
    current_team.append(curr)

def get_base_url(current_team):
    # get url without year range
    return f"https://api-web.nhle.com/v1/roster/{current_team}/"
    

def update_new_team():
    # update current team removes old team being checked with new team
    update_current_team()
    # get base_url
    base_url = get_base_url(current_team[0])
    return base_url

# get json_url returns full url
def get_json_url(base_url, season) -> str:
    # gets year_range (reads txt file)
    return f"{base_url}{season}" 

def convert(inches):
    feet = inches // 12
    inch = inches % 12
    return f"{feet}'{inch}"


# gets age of player by comparing date of birth to current date and finding age from there
def get_age(year: int, month: int, day: int):
    t = time.localtime()
    curr_year = int(t.tm_year)
    curr_month = int(t.tm_mon)
    curr_day = int(t.tm_mday)
    
    if curr_month > month or curr_month == month and curr_day > day:
        age = curr_year - year

    elif curr_month == month and curr_day == day:
        age = curr_year - year

    elif curr_month == month and curr_day < day or curr_month < month:
        age = (curr_year - year) - 1
    else:
        raise Exception("Invalid DOB of player!")
    return age


# get past teams of player
def get_past_teams(teams):
    list_of_teams = []
    for team in teams:
        past_league = team["leagueAbbrev"]
        # check if past league player played in was the nhl, and if the list already contains that team
        if past_league == "NHL":
            curr_team = convert_to_abbreviation(team["teamName"]["default"])
            if not list_of_teams.__contains__(curr_team):
                list_of_teams.append(curr_team)
    return list_of_teams

def get_division(team: str):
    if pacific.__contains__(team):
        return "PW"
    
    elif central.__contains__(team):
        return "CW"
    
    elif metropolitan.__contains__(team):
        return "ME"
    
    elif atlantic.__contains__(team):
        return "AE"
    
    else:
        return Exception("Player does not belong on a team")
    
def get_awards(response):
    try:
       award_details = response["awards"]
    except Exception:
        return {"no data": 0}
    else:
        awards = {}
        for trophies in award_details:
            awards[trophies["trophy"]["default"]] = len(trophies["seasons"])
        return awards
        
# return data of player
def get_skater(id, response):
    try:
        stats = response["careerTotals"]["regularSeason"]
    # in the case where a skater/goalie has not played an nhl game
    except Exception:
        skater = models.Skaters(
            skater_id = id,
            games_played = 0,
            goals = 0,
            assists = 0,
            points = 0,
            awards = {"no data": 0}
        )
    else:
        goals = stats["goals"]
        assists = stats["assists"]
        gamesPlayed = stats["gamesPlayed"]
        points = stats["points"]
        try: 
            skater = models.Skaters(
                skater_id = id,
                games_played = gamesPlayed,
                goals = goals,
                assists = assists,
                points = points,
                awards = get_awards(response)
            )
        except Exception:
            # raise exception if unique constraint is violated
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    finally:
        return skater
       # db.commit()

# return data of goalie

# def get_goalie(id, response, db: Session = Depends(get_db)):
#     try:
#         stats = response["featuredStats"]["regularSeason"]["subSeason"]
#     # in the case where a skater/goalie has not played an nhl game
#     except Exception:
#         goalie = models.Goalies(
#             goalie_id = id,
#             games_played = 0,
#             goals_against_avg = None,
#             save_percentage = None,
#             wins = 0,
#             shutouts = 0
#         )
#     else:
#         gamesPlayed = stats["gamesPlayed"]
#         gaa = stats["goalsAgainstAvg"]
#         savePercentage = stats["savePctg"]
#         wins = stats["wins"]
#         shutouts = stats["shutouts"]
#         try:
#             goalie = models.Goalies(
#                 goalie_id = id,
#                 games_played = gamesPlayed,
#                 goals_against_avg = round(gaa, 2),
#                 save_percentage = round(savePercentage, 2),
#                 wins = wins,
#                 shutouts = shutouts
#             )
#         except Exception:
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT)   
#     finally:
#         db.merge(goalie)
#         #db.commit()  

def get_draft(id, response):
    try:
        draft_details = response["draftDetails"]
    # case of an undrafted player
    except Exception:
        draftee = models.Draft(
            player_id = id,
            drafted_by = None,
            year = None,
            round = None,
            pick = None
        )
    else:
        year = draft_details["year"]
        team = draft_details["teamAbbrev"]
        round = draft_details["round"]
        pick = draft_details["pickInRound"]

        try:
            draftee = models.Draft(
                player_id = id,
                drafted_by = team,
                year = year,
                round = round,
                pick = pick
            )
        
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)   
    finally:
        return draftee



