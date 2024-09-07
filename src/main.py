
from fastapi import FastAPI, Depends 
# allows me to access fastapi from my local host
from fastapi.middleware.cors import CORSMiddleware
#extract fields from body, and convert to a python dictionary
from .database import get_db
from . import models
from .utils import update_current_team, update_new_team, get_base_url, get_json_url, convert, get_age, get_past_teams, get_division, get_skater, get_draft
from .utils import teams, current_team
from .utils import HTTPException, status
# allows you to easily send requests to external urls 
import requests
from sqlalchemy.orm import Session
from sqlalchemy import func


head = "http://127.0.0.1:8000"
app = FastAPI()

# allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    
    return {"message": "hello world!"}

# # response object, all information IS contained in this object
# # .post, .put, .delete, etc 


#GETs information from each season of a team (roster, year, abbreviation, etc)
@app.post("/teams")
async def team_data(db: Session = Depends(get_db)):
    update_current_team()
    list_of_seasons = requests.get(f"https://api-web.nhle.com/v1/roster-season/{current_team[0]}").json()
    base_url = get_base_url(current_team[0])



    while len(teams) > 0 and len(list_of_seasons) > 0:
        link = get_json_url(base_url, list_of_seasons[0])
        list_of_seasons.pop(0)
        print(link)
            
            # try-except loop to cycle through years where team didnt exist for whatever reason (lockout, before inaugration year, etc)
        try:
            r = requests.get(link, stream=True)
            response = r.json() 
        # if JSON error, continously increment years until after 2024
        except requests.exceptions.JSONDecodeError:
            raise HTTPException(status_code=r.status_code, detail ="failed to fetch data!")
            # if r.status_code != 200:
            #     raise HTTPException(status_code=r.status_code, detail ="failed to fetch data!")
            
        teamName = link.split('/')[-2]
        teamYear = str(link.split('/')[-1])


        # gather data from JSON response
        player_id_list = []
        names = []
        for player in response["forwards"]:
                player_id_list.append(player["id"])
                names.append(player["firstName"]["default"] + " " + player["lastName"]["default"])
        
        for player in response["defensemen"]:
            player_id_list.append(player["id"])
            names.append(player["firstName"]["default"] + " " + player["lastName"]["default"])
        # for player in response["goalies"]:
        #     player_id_list.append(player["id"])
        #     names.append(player["firstName"]["default"] + " " + player["lastName"]["default"])
        team = models.Teams(
                team = teamName,
                player_ids = player_id_list,
                name = names,
                year = teamYear[0:4] + "/" + teamYear[6:10]
        )

        # update changes to database
        db.merge(team)

        # if list of teams still exists and current year range exceeded 2024, update new team and continue gathering data
        if len(list_of_seasons) == 0:
            base_url = update_new_team()
            print(base_url)
            list_of_seasons = requests.get(f"https://api-web.nhle.com/v1/roster-season/{current_team[0]}").json()


    db.commit()
    return {"data": "committed!"}


    
# requests.post(f'{head}/send_some_info', data = {"key": r})


# skater db
# points, goals, assists, currently playing bool, curr team, age, years in nhl, past teams list, number, nation, position
 

def get_player_id(team: str, db: Session = Depends(get_db)):
    
    player = db.query(models.Teams).filter(models.Teams.team == team, models.Teams.year == '2024/25').first()
    try:
        return player.player_ids
    except AttributeError:
        return ""



@app.post("/player_data") 
async def player_data(db: Session = Depends(get_db)):
    list_of_player_ids = []
    
    for team in teams:
    # for loop  to go through players
        list_of_player_ids.append(get_player_id(team, db))
    # flatten list 
    list_of_player_ids =  [item for sublist in list_of_player_ids for item in sublist] 
    # remove duplicate player_ids, in the case where a player played on two teams in a season
    list_of_player_ids = list(set(list_of_player_ids))
    for player_id  in list_of_player_ids:    
        print(player_id)
        r = requests.get(f"https://api-web.nhle.com/v1/player/{player_id}/landing", allow_redirects=False)
        response = r.json()
        position = response["position"]        
        player_id = int(response["playerId"])
        isActive = response["isActive"]
        headshot = response["headshot"]
        if isActive:
            curr_team = response["currentTeamAbbrev"]
            standings = get_division(curr_team)
            division, conference = standings[0], standings[1]
        else:
            curr_team = None
        name = response["firstName"]["default"] + " " + response["lastName"]["default"]

        try:
            country = response["birthCountry"]
        except Exception:
            country = "NA"

        # in the case where a player has not chosen a number yet
        try:
            number = response["sweaterNumber"]
        except Exception:
            number = None
        #position = response["position"]
        height = convert(response["heightInInches"])
        dob = str(response["birthDate"])
        # splice birthdates and convert to age (years old)
        year, month, day = map(int, dob.split("-"))
        # year = int(dob[0:4])
        # month = int(dob[5:7])
        # day = int(dob[8:10])
        age = get_age(year, month, day)
        past_teams = get_past_teams(response["seasonTotals"])

        # goals = stats["goals"]
        # assists = stats["assists"]
        # gamesPlayed = stats["gamesPlayed"]

        # points = int(goals) + int(assists)
        try: 
            players = models.Players(
                player_id = player_id,
                headshot = headshot,
                name = name,
                team = curr_team,
                conference = conference,
                division = division,
                country = country,
                past_teams = past_teams,
                isActive = isActive,
                number = number,
                height = height,
                position = position,
                age = age
                )
        except Exception:
            # raise exception if unique constraint is violated
            # raise HTTPException(status_code=status.HTTP_409_CONFLICT)
            continue
        
        # if position == "G":
        #     get_goalie(player_id, response, db)
        # else:
        
        skater = get_skater(player_id, response)
        draftee = get_draft(player_id, response)

        db.merge(skater)
        db.merge(draftee)
        db.merge(players)
    # update and commit changes to database
    db.commit()
    return {"data": "recieved"}


# idea: all time wordle, with hints attached to each guess


# merge data puts player, skater, and draft data together
# will be the db used for queries of the wordle
@app.post("/merge_data")
async def merge_data(db: Session = Depends(get_db)):
    # query models together on where id's are equal
    data = (
    db.query(models.Players,  models.Skaters, models.Draft)
    .join(target=models.Draft, onclause=models.Players.player_id == models.Draft.player_id)
    .join(target=models.Skaters, onclause=models.Players.player_id == models.Skaters.skater_id)
    .all()
    )
    
    
    for player, skater, draft in data:
        player_data = models.CombinedPlayerData(   
            player_id = player.player_id,
            headshot = player.headshot,
            name = player.name,
            team = player.team,
            conference = player.conference,
            division = player.division,
            country = player.country,
            past_teams = player.past_teams,
            isActive = player.isActive,
            number = player.number,
            height = player.height,
            age = player.age,
            position = player.position,
            games_played = skater.games_played,
            goals = skater.goals,
            assists = skater.assists,
            points = skater.points,
            year = draft.year,
            drafted_by = draft.drafted_by,
            round = draft.round,
            pick = draft.pick,
            awards = skater.awards
        )
        db.merge(player_data)
    db.commit()
    return {"data": "committed"}

@app.get("/data")
async def return_player_data(db: Session = Depends(get_db)):
    data = (
        db.query(models.CombinedPlayerData).all()
    )
    return {"query": data}


@app.get("/random")
async def return_random_player(db: Session = Depends(get_db)):
    data = (
        db.query(models.CombinedPlayerData).filter(models.CombinedPlayerData.points > 200).order_by(func.random())
    ).first()

    return {"player": data}

@app.get("/all_names")
async def return_all_names(db: Session = Depends(get_db)):

    data = db.query(models.CombinedPlayerData.name).all()

    names_list = [name[0] for name in data]
    
    return {"names": names_list}

# "names": {}"player1", id], ["player2", id]