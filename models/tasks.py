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
def plugin_mailcaptcha_del_old_queue_entries():
	import datetime
	from_time = datetime.datetime.now() - datetime.timedelta( seconds = ( plugin_mailcaptcha_config.queue_timeout ) * 60 )
	rows = db( db.plugin_mailcaptcha_queue.created_on < from_time )
	deleted = rows.count()
	rows.delete()
	db.commit()
	return dict( rows = deleted )

def plugin_mailcaptcha_sendmail( id ):
	import logging
	logger = logging.getLogger( "web2py.app.mailcaptcha" )
	logger.setLevel( logging.DEBUG )

	mail_queue = db( db.plugin_mailcaptcha_queue.id == id )
	if mail_queue.count() == 0:
		return dict( error = 'No record' )
	mail_queue_row = mail_queue.select( limitby = ( 0, 1 ) ).first()

	# if there is x.509 cert we set up to sign the mail
	if plugin_mailcaptcha_config.x509_sign_keyfile and \
		plugin_mailcaptcha_config.x509_sign_certfile and \
		plugin_mailcaptcha_config.x509_sign_passphrase:
		logger.debug( 'Do mail signing' )
		mail.settings.cipher_type = 'x509'
		mail.settings.sign = True
		mail.settings.sign_passphrase = plugin_mailcaptcha_config.x509_sign_passphrase
		mail.settings.encrypt = False
		mail.settings.x509_sign_keyfile = x509_sign_keyfile
		mail.settings.x509_sign_certfile = x509_sign_certfile

	mail.settings.sender = plugin_mailcaptcha_config.mail_sender
	mail.settings.login = plugin_mailcaptcha_config.mail_login if len( plugin_mailcaptcha_config.mail_login ) > 0 else None
	mail.settings.server = plugin_mailcaptcha_config.mail_server

	# Send notify e-mail if there is an address for that
	if plugin_mailcaptcha_config.mail_notify_recipient:
		msg_vars = {'from': mail_queue_row.email,
								'client_address': mail_queue_row.client_address,
								'client_name':mail_queue_row.client_name,
								'helo_name':mail_queue_row.helo_name,
								'recipient':mail_queue_row.recipient,
								'created_on':mail_queue_row.created_on,
								'url': '%s%s' % ( plugin_mailcaptcha_config.webserver_url,
															URL( 'plugin_mailcaptcha', 'queue'
																																						)
															)
									}
		msg = plugin_mailcaptcha_config.mail_notify_txt % msg_vars
		logger.debug( 'login: [%s]' % mail.settings.login )
		logger.debug( 'msg: [%s]' % msg )
		logger.debug( 'subject: [%s]' % plugin_mailcaptcha_config.mail_notify_subject )
		logger.debug( 'to: [%s]' % plugin_mailcaptcha_config.mail_notify_recipient )
		mail.send( to = plugin_mailcaptcha_config.mail_notify_recipient.split( ',' ),
								subject = plugin_mailcaptcha_config.mail_notify_subject,
								message = msg )

	# send the captcha url to the sender
	msg_vars = {'from': mail_queue_row.email,
							'url': '%s%s' % ( plugin_mailcaptcha_config.webserver_url,
															URL( 'plugin_mailcaptcha', 'index', vars = dict( 
																														i = mail_queue_row.uuid
																														)
																																						)
															)
								}
	msg = plugin_mailcaptcha_config.mail_txt % msg_vars
	logger.debug( 'login: [%s]' % mail.settings.login )
	logger.debug( 'msg: [%s]' % msg )
	logger.debug( 'subject: [%s]' % plugin_mailcaptcha_config.mail_subject )
	logger.debug( 'to: [%s]' % mail_queue_row.email )
	if not mail.send( to = [mail_queue_row.email],
							subject = plugin_mailcaptcha_config.mail_subject,
							message = msg ):
		return dict( error = mail.error )

	return dict()

from gluon.scheduler import Scheduler
Scheduler( db, dict( plugin_mailcaptcha_sendmail = plugin_mailcaptcha_sendmail,
										plugin_mailcaptcha_del_old_queue_entries = plugin_mailcaptcha_del_old_queue_entries ) )
