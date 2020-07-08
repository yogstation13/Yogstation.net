from sqlalchemy import BigInteger
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from yogsite.config import cfg

Base = declarative_base()

class Player(Base):
	__tablename__ = 'erro_player'

	ckey				= Column('ckey',				String(32), primary_key=True)
	byond_key			= Column('byond_key',			String(32))
	firstseen			= Column('firstseen',			DateTime())
	firstseen_round_id	= Column('firstseen_round_id',	Integer())
	lastseen			= Column('lastseen',			DateTime())
	lastseen_round_id	= Column('lastseen_round_id',	Integer())
	ip					= Column('ip',					Integer())
	computerid			= Column('computerid',			String(32))
	lastadminrank		= Column('lastadminrank',		String(32))
	accountjoindate		= Column('accountjoindate',		Date())
	flags				= Column('flags',				SmallInteger())
	discord_id			= Column('discord_id',			BigInteger())
	antag_tokens		= Column('antag_tokens',		Integer())
	credits				= Column('credits',				BigInteger())
	antag_weight		= Column('antag_weight',		Integer())
	job_whitelisted		= Column('job_whitelisted',		SmallInteger())


	notes				= relationship('Note',	primaryjoin = 'Player.ckey == Note.ckey')
	bans				= relationship('Ban',	primaryjoin = 'Player.ckey == Ban.ckey')

	_connections		= relationship('Connection',	primaryjoin = 'Player.ckey == Connection.ckey')

	@classmethod
	def from_ckey(cls, ckey):
		try:
			return game_db.query(cls).filter(cls.ckey == ckey).one()
		except NoResultFound:
			return None
	
	def get_connection_count(self):
		return game_db.query(Connection).filter(Connection.ckey == self.ckey).count()
	
	def get_death_count(self):
		return game_db.query(Death).filter(Death.byondkey == self.ckey).count()
	
	def get_bans(self):
		return game_db.query(Ban).filter(Ban.ckey == self.ckey).all()


class Note(Base):
	__tablename__ = 'erro_notes'

	id					= Column('id',					Integer(), primary_key=True)
	ckey				= Column('ckey',				String(32), ForeignKey('erro_player.ckey'))
	timestamp			= Column('timestamp',			DateTime())
	notetext			= Column('notetext',			String(16777215))
	adminckey			= Column('adminckey',			String(32))
	server				= Column('server',				String(32))
	secret				= Column('secret',				SmallInteger())
	last_editor			= Column('last_editor',			String(32))
	edits				= Column('edits',				Text())

class Ban(Base):
	__tablename__ = 'erro_ban'

	id					= Column('id',					Integer(), primary_key=True)
	bantime				= Column('bantime',				DateTime())
	server_ip			= Column('server_ip',			Integer())
	server_port			= Column('server_port',			SmallInteger())
	round_id			= Column('round_id',			Integer())
	role				= Column('role',				String(32))
	expiration_time		= Column('expiration_time',		DateTime())
	applies_to_admins	= Column('applies_to_admins',	SmallInteger())
	reason				= Column('reason',				String(2048))
	ckey				= Column('ckey',				String(32),	ForeignKey('erro_player.ckey'))
	ip					= Column('ip',					Integer())
	computerid			= Column('computerid',			String(32))
	a_ckey				= Column('a_ckey',				String(32))
	edits				= Column('edits',				Text())
	unbanned_datetime	= Column('unbanned_datetime',	DateTime())
	unbanned_ckey		= Column('unbanned_ckey',		String(32))
	unbanned_round_id	= Column('unbanned_round_id',	Integer())

class Connection(Base):
	__tablename__ = "erro_connection_log"

	id				= Column('id',			Integer(), primary_key=True)
	datetime		= Column('datetime',	DateTime())
	left			= Column('left',		DateTime())
	server_ip		= Column('server_ip',	Integer())
	server_port		= Column('server_port',	SmallInteger())
	round_id		= Column('round_id',	Integer())
	ckey			= Column('ckey',		String(32),	ForeignKey('erro_player.ckey'))
	ip				= Column('ip',			Integer())
	computerid		= Column('computerid',	String(45))

class Book(Base):
	__tablename__ = "erro_library"

	id					= Column('id',					Integer(), primary_key=True)
	author				= Column('author',				String(32))
	title				= Column('title',				String(45))
	content				= Column('content',				String(16777215))
	category			= Column('category',			Enum('Any', 'Fiction', 'Non-Fiction', 'Adult', 'Reference', 'Religion'))
	ckey				= Column('ckey',				String(32),	ForeignKey('erro_player.ckey'))
	datetime			= Column('datetime',			DateTime())
	deleted				= Column('deleted',				SmallInteger())
	round_id_created	= Column('round_id_created',	Integer())


class Round(Base):
	__tablename__ = 'erro_round'

	id					= Column('id',					Integer(), primary_key=True)
	initialize_datetime	= Column('initialize_datetime',	DateTime())
	start_datetime		= Column('start_datetime',		DateTime())
	shutdown_datetime	= Column('shutdown_datetime',	DateTime())
	end_datetime		= Column('end_datetime',		DateTime())
	server_ip			= Column('server_ip',			Integer())
	server_port			= Column('server_port',			SmallInteger())
	commit_hash			= Column('commit_hash',			String(40))
	game_mode			= Column('game_mode',			String(32))
	game_mode_result	= Column('game_mode_result',	String(64))
	end_state			= Column('end_state',			String(64))
	shuttle_name		= Column('shuttle_name',		String(64))
	map_name			= Column('map_name',			String(32))
	station_name		= Column('station_name',		String(80))



game_db_engine = create_engine("mysql://{username}:{password}@{host}:{port}/{db}".format(
	username	= cfg.db.game.user,
	password	= cfg.db.game.password,
	host		= cfg.db.game.host,
	port		= cfg.db.game.port,
	db			= cfg.db.game.dbname,
))

game_db_sessionmaker = sessionmaker(bind=game_db_engine)

game_db = game_db_sessionmaker()