# -*- coding: utf-8 -*-
if 0:
	from gluon import *
	request, session, response, T, cache = current.request, current.session, current.response, current.t, current.cache
	from gluon.dal import DAL
	from gluon.tools import Auth, Service, Crud, Storage
	db = DAL()
	auth = Auth()
	service = Service()
	crud = Crud()
	settings = Storage()

def index():
	if not plugin_mailcaptcha_config:
		raise HTTP( 404, T( 'Config error' ) )
	if not request.vars.i:
		raise HTTP( 404, T( 'Request error' ) )
	rows = db( db.plugin_mailcaptcha_queue.uuid == request.vars.i )
	if rows.count() == 0:
		raise HTTP( 404, T( 'Request error' ) )
	row = rows.select( db.plugin_mailcaptcha_queue.email ).first()
	email = str( row.email )
	ok = False
	from gluon.tools import Recaptcha
	form = FORM( 
					Recaptcha( request,
										plugin_mailcaptcha_config.recaptcha_private_key,
										plugin_mailcaptcha_config.recaptcha_public_key,
										options = plugin_mailcaptcha_config.recaptcha_options ),
					INPUT( _type = 'submit' )
					)
	if form.process().accepted:
		ok = True
		db.plugin_mailcaptcha_whitelist.insert( email = row.email )
		db( db.plugin_mailcaptcha_queue.email == row.email ).delete()
	if plugin_mailcaptcha_config.greetings:
		txt = MARKMIN( plugin_mailcaptcha_config.greetings % dict( sender = email ) )
	else:
		txt = T( 'To be able to send us emails from \'%(email)s\' address please fill in the following form. Thank you!', dict( email = email ) )
	if plugin_mailcaptcha_config.successful:
		successful = MARKMIN( plugin_mailcaptcha_config.successful % dict( sender = email ) )
	else:
		successful = T( 'The \'%(email)s\' address is now allowed to send e-mails to us.', dict( email = email ) )
	return dict( form = form,
							ok = ok,
							email = email,
							txt = txt,
							successful = successful )

@auth.requires_login()
def whitelist():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_whitelist ) )

@auth.requires_login()
def blacklist():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_blacklist ) )

@auth.requires_login()
def apply_on():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_apply_on ) )

@auth.requires_login()
def settings():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_settings ) )

@auth.requires_login()
def queue():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_queue ) )

@auth.requires_login()
def scheduler_task():
	return dict( grid = SQLFORM.grid( db.scheduler_task ) )

@auth.requires_login()
def scheduler_run():
	return dict( grid = SQLFORM.grid( db.scheduler_run ) )
