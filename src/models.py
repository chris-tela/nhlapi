from sqlalchemy import Column, Integer, String, Boolean, ARRAY, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()

"""
players class --> data of both skater/goalies
inner join skater/goalie class
"""

class Players(Base): 
    __tablename__ = "players"
    player_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    headshot = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    team = Column(String, nullable=True)
    conference = Column(String, nullable=True)
    division = Column(String, nullable=True)
    country = Column(String, nullable=False)
    past_teams = Column(ARRAY(String), nullable=True)  
    isActive = Column(Boolean, nullable=False)
    number = Column(SmallInteger, nullable=True)
    height = Column(String, nullable=True)
    age = Column(SmallInteger, nullable=True)
    position = Column(String, nullable=True)



class Skaters(Base):
    __tablename__ = "skaters"
    skater_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    games_played = Column(Integer, nullable=True)
    goals = Column(Integer, nullable=True)
    assists = Column(Integer, nullable=True)
    points = Column(Integer, nullable=True)
    awards = Column(JSONB, nullable=True)

# class Goalies(Base):
#     __tablename__ = "goalies"
#     goalie_id = Column(Integer,unique=True, nullable=False, primary_key=True)
#     games_played = Column(Integer, nullable=True)
#     goals_against_avg = Column(Float, nullable=True)
#     save_percentage = Column(Float, nullable=True)
#     wins = Column(Integer, nullable=False)
#     shutouts = Column(Integer, nullable=False)
   
class Teams(Base):
    __tablename__ = "alltime_teams"
    id = Column(Integer, primary_key=True, autoincrement=True)
    team = Column(String, nullable=True)
    player_ids = Column(ARRAY(String), nullable=True)
    name = Column(ARRAY(String), nullable=True)
    year = Column(String, nullable=True)

class Draft(Base):
    __tablename__ = "draft"
    player_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    drafted_by = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    round = Column(Integer, nullable=True)
    pick = Column(Integer, nullable=True)

class CombinedPlayerData(Base):
    __tablename__ = "merged"
    player_id = Column(Integer, unique=True, primary_key=True, nullable=False)
    headshot = Column(String, nullable=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    team = Column(String, nullable=True)
    conference = Column(String, nullable=True)
    division = Column(String, nullable=True)
    country = Column(String, nullable=False)
    past_teams = Column(ARRAY(String), nullable=True)  
    isActive = Column(Boolean, nullable=False)
    number = Column(SmallInteger, nullable=True)
    height = Column(String, nullable=True)
    age = Column(SmallInteger, nullable=True)
    position = Column(String, nullable=True)  
    games_played = Column(Integer, nullable=True)
    goals = Column(Integer, nullable=True)
    assists = Column(Integer, nullable=True)
    points = Column(Integer, nullable=True)  
    year = Column(Integer, nullable=True)
    drafted_by = Column(String, nullable=True)
    round = Column(Integer, nullable=True)
    pick = Column(Integer, nullable=True)
    awards = Column(JSONB, nullable=True)
