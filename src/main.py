from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import get_db
from . import models
from .utils import update_current_team, update_new_team, get_base_url, get_json_url, convert, get_age, get_past_teams, get_division, get_skater, get_draft, process_filter
from .utils import teams, current_team
from .utils import HTTPException, status
import requests
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

head = "http://127.0.0.1:8000"
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "hello world!"}

@app.post("/teams")
async def team_data(db: Session = Depends(get_db)):
    update_current_team()
    list_of_seasons = requests.get(f"https://api-web.nhle.com/v1/roster-season/{current_team[0]}").json()
    base_url = get_base_url(current_team[0])

    while len(teams) > 0 and len(list_of_seasons) > 0:
        link = get_json_url(base_url, list_of_seasons[0])
        list_of_seasons.pop(0)
        print(link)

        try:
            r = requests.get(link, stream=True)
            response = r.json()
        except requests.exceptions.JSONDecodeError:
            raise HTTPException(status_code=r.status_code, detail ="failed to fetch data!")

        teamName = link.split('/')[-2]
        teamYear = str(link.split('/')[-1])

        player_id_list = []
        names = []
        for player in response["forwards"]:
            player_id_list.append(player["id"])
            names.append(player["firstName"]["default"] + " " + player["lastName"]["default"])

        for player in response["defensemen"]:
            player_id_list.append(player["id"])
            names.append(player["firstName"]["default"] + " " + player["lastName"]["default"])

        team = models.Teams(
            team = teamName,
            player_ids = player_id_list,
            name = names,
            year = teamYear[0:4] + "/" + teamYear[6:10]
        )

        db.merge(team)

        if len(list_of_seasons) == 0:
            base_url = update_new_team()
            print(base_url)
            list_of_seasons = requests.get(f"https://api-web.nhle.com/v1/roster-season/{current_team[0]}").json()

    db.commit()
    return {"data": "committed!"}

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
        list_of_player_ids.append(get_player_id(team, db))

    list_of_player_ids =  [item for sublist in list_of_player_ids for item in sublist]
    list_of_player_ids = list(set(list_of_player_ids))

    for player_id  in list_of_player_ids:
        print("Player ID: ", player_id)
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

        try:
            number = response["sweaterNumber"]
        except Exception:
            number = None

        height = convert(response["heightInInches"])
        dob = str(response["birthDate"])
        year, month, day = map(int, dob.split("-"))
        age = get_age(year, month, day)
        past_teams = get_past_teams(response["seasonTotals"])

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
            continue

        skater = get_skater(player_id, response)
        draftee = get_draft(player_id, response)

        db.merge(skater)
        db.merge(draftee)
        db.merge(players)

    db.commit()
    return {"data": "recieved"}

@app.post("/merge_data")
async def merge_data(db: Session = Depends(get_db)):
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

@app.get("/filter_players")
async def return_filtered_players(goals, assists, age, db: Session = Depends(get_db)):
    data = db.query(models.CombinedPlayerData).filter(models.CombinedPlayerData.goals > goals[0]).filter(
        models.CombinedPlayerData.goals < goals[1]).filter(models.CombinedPlayerData.assists > assists[0]).filter(
            models.CombinedPlayerData.assists < assists[1]).filter(models.CombinedPlayerData.age > age[0]).filter(
                models.CombinedPlayerData.age < age[1]).all()
    for name in data:
        print(name.name + " goals: " + str(name.goals) + " assists: " + str(name.assists) + " age: " + str(name.age))
    return {"length": len(data)}

class ReturnedPlayer(BaseModel):
    goals: int
    assists: int
    age: int
    mystery_goals: int
    mystery_assists: int
    mystery_age: int


# endpoint, filters remaining players that can be chosen based on the player's guesses
@app.post("/filter")
async def filter_data(player: ReturnedPlayer, db: Session = Depends(get_db)):
    if player.goals == player.mystery_goals and player.assists == player.mystery_assists and player.age == player.mystery_age:
        result = await return_filtered_players([player.goals, player.goals], [player.assists, player.assists], [player.age, player.age], db)
    else:
        x = process_filter(player.goals, player.assists, player.age, player.mystery_goals, player.mystery_assists, player.mystery_age)
        result = await return_filtered_players(x["goals"], x["assists"], x["age"], db)
    return {"message": "data received", "data": player.model_dump(), "remaining_count": result["length"]}