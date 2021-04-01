from datetime import datetime, timedelta

from hashlib import sha256

from netaddr import IPAddress

from flask import g, request # dumb dumb stupid varname

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import (and_, or_, BigInteger, create_engine, Column, Date, DateTime,
	Enum, Float, ForeignKey, func, Integer, SmallInteger, String, Text)

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.session import make_transient

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from yogsite.config import cfg
from yogsite.const import *
from yogsite.extensions import flask_db_ext
from yogsite.util import byondname_to_ckey

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

	connections		= relationship('Connection',	primaryjoin = 'Player.ckey == Connection.ckey')

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
	
	def get_round_count(self):
		# We have to only query the round_id so the distinct thing will work because haha sqlalchemy
		return game_db.query(Connection.round_id).filter(Connection.ckey == self.ckey).distinct(Connection.round_id).count()

	def get_bans(self):
		return query_grouped_bans().filter(Ban.ckey == self.ckey).all()
	
	def get_notes(self):
		return game_db.query(Note).filter(Note.targetckey == self.ckey)
	
	def get_visible_notes(self):
		return self.get_notes().filter(Note.deleted == 0, or_(Note.expire_timestamp == None, Note.expire_timestamp > datetime.utcnow()))
	
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
	__tablename__ = 'erro_messages'

	id					= Column('id',					Integer(), primary_key=True)
	type				= Column('type',				String(32))
	targetckey			= Column('targetckey',			String(32), ForeignKey('erro_player.ckey'))
	adminckey			= Column('adminckey',			String(32))
	text				= Column('text',				String(16777215))
	timestamp			= Column('timestamp',			DateTime())
	server				= Column('server',				String(32))
	server_ip			= Column('server_ip',			Integer())
	server_port			= Column('server_port',			Integer())
	round_id			= Column('round_id',			Integer())
	secret				= Column('secret',				SmallInteger())
	expire_timestamp	= Column('expire_timestamp',	DateTime())
	lasteditor			= Column('lasteditor',			String(32))
	edits				= Column('edits',				Text())
	deleted				= Column('deleted',				SmallInteger())

	@classmethod
	def add_from_form(cls, form, ckey):
		note = cls(
			type = form.type.data,
			targetckey = ckey,
			adminckey = g.current_user.ckey,
			text = form.text.data,
			timestamp = datetime.utcnow(),
			server = "webmin",
			server_ip = 0,
			server_port = 0,
			round_id = 0,
			deleted = 0
		)

		game_db.add(note)
		game_db.commit()

	@classmethod
	def from_id(cls, id):
		try:
			return game_db.query(cls).filter(cls.id == id).one()
		except NoResultFound:
			return None

	def set_deleted(self, deleted):
		"""
		Mark a note as deleted, or not
		"""
		self.deleted = int(deleted) # int so we can pass bools
		game_db.commit()

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
	a_ip				= Column('a_ip',				Integer())
	a_computerid		= Column('a_computerid',		Integer())
	who					= Column('who',					String(2048))
	adminwho			= Column('adminwho',			String(2048))
	edits				= Column('edits',				Text())
	unbanned_datetime	= Column('unbanned_datetime',	DateTime())
	unbanned_ckey		= Column('unbanned_ckey',		String(32))
	unbanned_ip			= Column('unbanned_ip',			Integer())
	unbanned_computerid	= Column('unbanned_computerid',	String(32))
	unbanned_round_id	= Column('unbanned_round_id',	Integer())

	@classmethod
	def add_from_form(cls, form):
		bantime = datetime.utcnow() # Want all of the jobban entries to have the same time

		for role in form.roles.data:
			entry = cls(
				ckey = byondname_to_ckey(form.ckey.data),
				a_ckey = g.current_user.ckey,
				bantime = bantime,
				expiration_time = form.expiration_time.data if form.expiration_time.data else None,
				role = role,
				ip = int(IPAddress(form.ip.data)) if form.ip.data else None,
				computerid = form.computerid.data if form.computerid.data else None,
				reason = form.reason.data,
				## Defaults ##
				server_ip = 0, server_port = 0, round_id = 0, applies_to_admins = 0, edits = None,
				unbanned_datetime = None, unbanned_ckey = None, unbanned_round_id = None, a_ip = int(IPAddress(request.remote_addr)),
				a_computerid = 0, who = "", adminwho = "", unbanned_ip = None, unbanned_computerid = None
			)
			game_db.add(entry)

		game_db.commit()

	@classmethod
	def from_id(cls, id):
		try:
			return game_db.query(cls).filter(cls.id == id).one()
		except NoResultFound:
			return None
	
	@classmethod
	def grouped_from_id(cls, id): # For getting job bans with the roles grouped as a seperate field, yep it's a headache
		try:
			single_from_id = cls.from_id(id)

			return game_db.query(
				*([c for c in cls.__table__.c]+[func.group_concat(Ban.role).label("roles")])
			).group_by(cls.bantime, cls.ckey).filter(cls.ckey==single_from_id.ckey, cls.bantime==single_from_id.bantime).one()

		except NoResultFound:
			return None

	def apply_edit_form(self, form):
		"""
		Take the data from the form and update this record with it, then commit the change to the db
		There is almost definitely a better way to do this

		This is a complete headache especially when it comes to editing job bans
		"""

		grouped_bans = Ban.query.filter(Ban.bantime==self.bantime, Ban.ckey==self.ckey).all()

		roles_to_add = form.roles.data.copy() # We will remove all the ones we already have next, so we don't re-add them

		for ban in grouped_bans:
			if ban.role not in form.roles.data: # If we removed that role then delete the ban associated to it
				game_db.delete(ban)
			else:
				roles_to_add.remove(ban.role)
		
		for role in roles_to_add:
			non_pk_columns = [k for k in self.__table__.columns.keys() if k not in self.__table__.primary_key]
			data = {c: getattr(self, c) for c in non_pk_columns}
			data["role"] = role
			print(data)
			clone = Ban(**data)

			game_db.add(clone)

		update_dict = {
			Ban.ckey: byondname_to_ckey(form.ckey.data),
			Ban.reason: form.reason.data,
			Ban.expiration_time: form.expiration_time.data if form.expiration_time.data else None,
			Ban.ip: int(IPAddress(form.ip.data)) if form.ip.data else None,
			Ban.computerid: form.computerid.data if form.computerid.data else None
		}

		new_bans = Ban.query.filter(Ban.bantime==self.bantime, Ban.ckey==self.ckey)

		new_bans.update(update_dict)
		game_db.commit()

		return new_bans.first() # Return the first ban so we have a new ID to redirect them to in case they delete the old one they were editing
		# (by removing the role associated with it from the job ban group)
	
	def revoke(self, admin_ckey):
		"""
		Revoke a ban by setting the unbanned datetime
		"""
		Ban.query.filter(Ban.bantime==self.bantime, Ban.ckey==self.ckey).update({
			Ban.unbanned_ckey: admin_ckey,
			Ban.unbanned_datetime: datetime.utcnow() # Set the time of unbanning to now so the server knows that if we are past now, they should be unbanned
		})

		game_db.commit()

	def reinstate(self):
		"""
		Reinstate a ban by clearing the unbanned datetime
		"""
		Ban.query.filter(Ban.bantime==self.bantime, Ban.ckey==self.ckey).update({
			Ban.unbanned_ckey: None,
			Ban.unbanned_datetime: None
		})

		game_db.commit()

def query_grouped_bans(order_by=Ban.id.desc(), search_query=None):
	query=game_db.query(
		*([c for c in Ban.__table__.c]+[func.group_concat(Ban.role).label("roles")])
	) # All columns from ban + the grouped by role

	query=query.group_by(Ban.bantime, Ban.ckey)

	if order_by is not None:
		query = query.order_by(order_by)
	if search_query:
		query = query.filter(Ban.ckey.like(search_query))
	
	return query

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

	def duration(self):
		# If the user hasn't left, use now as the end time for the connection
		if not self.left: return timedelta(0)

		return self.left - self.datetime

class Death(flask_db_ext.Model):
	__tablename__ = "erro_death"

	id				= Column('id',			Integer(), primary_key=True)
	tod				= Column('tod',			DateTime())
	server_ip		= Column('server_ip',	Integer())
	server_port		= Column('server_port',	SmallInteger())
	round_id		= Column('round_id',	Integer())
	byondkey		= Column('byondkey',	String(32),	ForeignKey('erro_player.ckey'))
	suicide			= Column('suicide',		SmallInteger())

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
	
	def in_progress(self):
		if self.shutdown_datetime:
			return False
		
		return True

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

	# Override so flask_login knows what we identify with
	def get_id(self):
		return self.ckey

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

	@classmethod
	def add(cls, admin_ckey, reason, expiry_time):
		entry = cls(ckey=admin_ckey, reason=reason, expiry_time=expiry_time, time=datetime.utcnow())
		game_db.add(entry)
		game_db.commit()

class ActionLog(flask_db_ext.Model):
	__tablename__ = "web_logs"

	id			= Column('id',			Integer(), primary_key=True)
	adminid		= Column('adminid',		String(32))
	target		= Column('target',		String(32),	ForeignKey('erro_player.ckey'))
	description	= Column('description',	String(16777215))
	timestamp	= Column('timestamp',	DateTime())

	@classmethod
	def add(cls, admin_ckey, target_ckey, description):
		entry = cls(adminid=admin_ckey, target=target_ckey, description=description)
		game_db.add(entry)
		game_db.commit()

class Donation(flask_db_ext.Model):
	__tablename__ = 'erro_donors'

	id 					= Column('id',					Integer(), primary_key=True)
	ckey				= Column('ckey',				String(32))
	discord_id			= Column('discord_id',			String(32))
	transaction_id		= Column('transaction_id',		String(70))
	amount				= Column('amount',				Float())
	datetime			= Column('datetime',			DateTime())
	expiration_time		= Column('expiration_time',		DateTime())
	revoked				= Column('revoked',				SmallInteger())
	revoked_ckey		= Column('revoked_ckey',		String(32))
	revoked_time		= Column('revoked_time',		DateTime())
	payer_email			= Column('payer_email',			String(256))
	status				= Column('status',				String(32))
	notes				= Column('notes',				String(1024))
	valid				= Column('valid',				SmallInteger())