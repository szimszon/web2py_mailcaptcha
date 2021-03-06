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
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_whitelist,
																	orderby = db.plugin_mailcaptcha_whitelist.email ) )

@auth.requires_login()
def blacklist():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_blacklist,
																	orderby = db.plugin_mailcaptcha_blacklist.email ) )

@auth.requires_login()
def apply_on():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_apply_on,
																	orderby = db.plugin_mailcaptcha_apply_on.email ) )

@auth.requires_login()
def settings():
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_settings ) )

@auth.requires_login()
def queue():
	links = [dict( header = '',
						body = lambda r:DIV( 
															A( T( 'Put to the whitelist' ),
																callback = URL( 'to_whitelist',
																							vars = dict( email = r.email ),
																							user_signature = True ),
																delete = "tr",
																_class = "btn"
															 ),
															BR(),
															A( T( 'Put to the blacklist' ),
																callback = URL( 'to_blacklist',
																							vars = dict( email = r.email ),
																							user_signature = True ),
																delete = "tr",
																_class = "btn"
															 )
															)
							)]
	return dict( grid = SQLFORM.grid( db.plugin_mailcaptcha_queue,
																	orderby = ~db.plugin_mailcaptcha_queue.id,
																	links = links ) )

@auth.requires_login()
def scheduler_task():
	return dict( grid = SQLFORM.grid( db.scheduler_task,
																	orderby = ~db.scheduler_task.id ) )

@auth.requires_login()
def scheduler_run():
	return dict( grid = SQLFORM.grid( db.scheduler_run,
																	orderby = ~db.scheduler_run.id ) )

@auth.requires_signature()
def to_whitelist():
	if not request.vars.email:
		raise HTTP( 'Invalid request' )
	if db( db.plugin_mailcaptcha_whitelist.email == request.vars.email ).count() == 0:
		db.plugin_mailcaptcha_whitelist.insert( email = request.vars.email )
		#
		# Send mail to the sender that the e-mail address is approved by the admin
		# ######################################################################### 
		# if there is x.509 cert we set up to sign the mail
		if plugin_mailcaptcha_config.x509_sign_keyfile and \
			plugin_mailcaptcha_config.x509_sign_certfile and \
			plugin_mailcaptcha_config.x509_sign_passphrase:
			mail.settings.cipher_type = 'x509'
			mail.settings.sign = True
			mail.settings.sign_passphrase = plugin_mailcaptcha_config.x509_sign_passphrase
			mail.settings.encrypt = False
			mail.settings.x509_sign_keyfile = plugin_mailcaptcha_config.x509_sign_keyfile
			mail.settings.x509_sign_certfile = plugin_mailcaptcha_config.x509_sign_certfile

		mail.settings.sender = plugin_mailcaptcha_config.mail_sender
		mail.settings.login = plugin_mailcaptcha_config.mail_login if len( plugin_mailcaptcha_config.mail_login ) > 0 else None
		mail.settings.server = plugin_mailcaptcha_config.mail_server
		msg_vars = {'from': request.vars.email}
		msg = plugin_mailcaptcha_config.mail_admin_approval_txt % msg_vars
		mail.send( to = [request.vars.email],
								subject = plugin_mailcaptcha_config.mail_admin_approval_subject,
								message = msg )
	if db( db.plugin_mailcaptcha_whitelist.email == request.vars.email ).count() > 0:
		db( db.plugin_mailcaptcha_queue.email == request.vars.email ).delete()

	return dict()

@auth.requires_signature()
def to_blacklist():
	if not request.vars.email:
		raise HTTP( 'Invalid request' )
	if db( db.plugin_mailcaptcha_blacklist.email == request.vars.email ).count() == 0:
		db.plugin_mailcaptcha_blacklist.insert( email = request.vars.email )
	if db( db.plugin_mailcaptcha_blacklist.email == request.vars.email ).count() > 0:
		db( db.plugin_mailcaptcha_queue.email == request.vars.email ).delete()
	return dict()
