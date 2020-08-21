from datetime import datetime

from hashlib import sha256

from netaddr import IPAddress

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import and_
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
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker


from yogsite.config import cfg
from yogsite.const import *

from yogsite.extensions import flask_db_ext

game_db = flask_db_ext.session

class Player(flask_db_ext.Model):
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
	
	def get_role_time(self, role):
		try:
			time_for_role = game_db.query(RoleTime).filter(
				and_(RoleTime.ckey == self.ckey, RoleTime.job == role)
			).one()

			return time_for_role.minutes

		except NoResultFound:
			return 0
	
	def get_total_playtime(self):
		living_time = self.get_role_time("Living")
		ghost_time = self.get_role_time("Ghost")

		return living_time + ghost_time

	def get_favorite_job(self):
		try:
			most_played_role = game_db.query(RoleTime).filter(
				and_(
					RoleTime.ckey == self.ckey,
					RoleTime.job != "Living",		# probably not the best way to do this but.... UGHHH
					RoleTime.job != "Ghost"
				)
			).order_by(RoleTime.minutes.desc()).first()

			return most_played_role

		except NoResultFound:
			return None

class Note(flask_db_ext.Model):
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


class Ban(flask_db_ext.Model):
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

	@classmethod
	def from_id(cls, id):
		try:
			return game_db.query(cls).filter(cls.id == id).one()
		except NoResultFound:
			return None


	def apply_edit_form(self, form):
		"""
		Take the data from the form and update this record with it, then commit the change to the db
		There is almost definitely a better way to do this
		"""

		self.ckey = form.ckey.data
		self.reason = form.reason.data
		self.role = form.role.data

		if form.expiration_time.data:
			self.expiration_time = form.expiration_time.data # yes this is parsed by the form already
		else:
			self.expiration_time = None

		self.ip = int(IPAddress(form.ip.data))
		self.computerid = form.computerid.data

		game_db.commit()
	
	def revoke(self, admin_ckey):
		"""
		Revoke a ban by setting the unbanned datetime
		"""
		self.unbanned_ckey = admin_ckey
		self.unbanned_datetime = datetime.utcnow() # Set the time of unbanning to now so the server knows that if we are past now, they should be unbanned

		game_db.commit()

	def reinstate(self):
		"""
		Reinstate a ban by clearing the unbanned datetime
		"""
		self.unbanned_ckey = None
		self.unbanned_datetime = None

		game_db.commit()


class Connection(flask_db_ext.Model):
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


class Book(flask_db_ext.Model):
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

	@classmethod
	def from_id(cls, id):
		try:
			return game_db.query(cls).filter(cls.id == id).one()
		except NoResultFound:
			return None

	def apply_edit_form(self, form):
		"""
		Take the data from the form and update this record with it, then commit the change to the db
		There is almost definitely a better way to do this
		"""

		self.title = form.title.data
		self.author = form.author.data
		self.content = form.content.data
		self.category = form.category.data

		game_db.commit()

	def set_deleted(self, deleted):
		"""
		Mark a book as deleted, or not
		"""
		self.deleted = int(deleted) # int so we can pass bools
		game_db.commit()

class Round(flask_db_ext.Model):
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

	@classmethod
	def from_id(cls, id):
		try:
			return game_db.query(cls).filter(cls.id == id).one()
		except NoResultFound:
			return None

class RoleTime(flask_db_ext.Model):
	__tablename__ = 'erro_role_time'

	ckey		= Column('ckey',		String(32), primary_key=True)
	job			= Column('job',			String(128), primary_key=True)
	minutes	=	 Column('minutes',		Integer())


class Admin(flask_db_ext.Model):
	__tablename__ = 'erro_admin'

	ckey		= Column('ckey',		String(32), primary_key=True)
	rank		= Column('rank',		String(32))
	password	= Column('password',	String(64))

	perms		= relationship('AdminRank',	primaryjoin = 'Admin.rank == AdminRank.rank')

	@classmethod
	def from_ckey(cls, ckey):
		try:
			return game_db.query(cls).filter(cls.ckey == ckey).one()
		except NoResultFound:
			return None
	
	def check_password(self, passwd): # MAKE SURE THIS IS SECUREEEE
		hash = sha256()
		hash.update(passwd.encode())
		hex_hash = hash.hexdigest()

		return self.password == hex_hash


class AdminRank(flask_db_ext.Model):
	__tablename__ = 'erro_admin_ranks'

	rank			= Column('rank',			String(32), ForeignKey('erro_admin.rank'), primary_key=True)
	flags			= Column('flags',			Integer())
	exclude_flags	= Column('exclude_flags',	Integer())
	can_edit_flags	= Column('can_edit_flags',	Integer())


class LOA(flask_db_ext.Model):
	__tablename__ = 'erro_loa'

	id 			= Column('id',			Integer(), primary_key=True)
	ckey		= Column('ckey',		String(32))
	time		= Column('time',		DateTime())
	expiry_time	= Column('expiry_time',	DateTime())
	revoked		= Column('revoked',		SmallInteger())
	reason		= Column('reason',		String(2048))

	@classmethod
	def from_id(cls, id):
		try:
			return game_db.query(cls).filter(cls.id == id).one()
		except NoResultFound:
			return None

	def is_active(self):
		now = datetime.utcnow()

		return (now > self.time) and (now < self.expiry_time) and (not self.revoked)
	
	def set_revoked(self, revoked):
		"""
		Set the revoked status of an LOA
		"""
		self.revoked = int(revoked) # so we can pass bools
		game_db.commit()