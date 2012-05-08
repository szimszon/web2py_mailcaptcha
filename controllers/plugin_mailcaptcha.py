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
	return dict( form = form,
							ok = ok,
							email = email )
