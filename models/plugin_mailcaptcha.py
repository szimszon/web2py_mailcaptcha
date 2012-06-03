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

import uuid
auth.signature.created_by.label = T( auth.signature.created_by.label )
auth.signature.created_on.label = T( auth.signature.created_on.label )
auth.signature.modified_by.label = T( auth.signature.modified_by.label )
auth.signature.modified_on.label = T( auth.signature.modified_on.label )
db.define_table( 'plugin_mailcaptcha_queue',
							Field( 'uuid', 'string',
									label = T( 'UUID' ),
									requires = IS_NOT_EMPTY(),
									writable = False,
									default = lambda: str( uuid.uuid4() ),
									),
							Field( 'email', 'string',
									label = T( 'E-mail' ),
									requires = IS_NOT_EMPTY(),
									),
							Field( 'client_address', 'string',
									label = T( 'Client address' ),
									),
							Field( 'client_name', 'string',
									label = T( 'Client name' ),
									),
							Field( 'helo_name', 'string',
									label = T( 'Helo name' ),
									),
							Field( 'recipient', 'string',
									label = T( 'Recipient' ),
									),
							auth.signature
 )
db.plugin_mailcaptcha_queue.created_on.readable = True
db.define_table( 'plugin_mailcaptcha_whitelist',
							Field( 'email', 'string',
									label = T( 'E-mail / Domain' ),
									requires = IS_NOT_EMPTY(),
									),
							auth.signature
 )
db.plugin_mailcaptcha_whitelist.created_by.readable = True
db.plugin_mailcaptcha_whitelist.created_on.readable = True
db.plugin_mailcaptcha_whitelist.modified_by.readable = True
db.plugin_mailcaptcha_whitelist.modified_on.readable = True
db.define_table( 'plugin_mailcaptcha_blacklist',
							Field( 'email', 'string',
									label = T( 'E-mail / Domain' ),
									requires = IS_NOT_EMPTY(),
									),
							auth.signature
 )
db.plugin_mailcaptcha_blacklist.created_by.readable = True
db.plugin_mailcaptcha_blacklist.created_on.readable = True
db.plugin_mailcaptcha_blacklist.modified_by.readable = True
db.plugin_mailcaptcha_blacklist.modified_on.readable = True
db.define_table( 'plugin_mailcaptcha_apply_on',
							Field( 'email', 'string',
									label = T( 'E-mail' ),
									requires = IS_NOT_EMPTY(),
									),
							auth.signature
 )
db.plugin_mailcaptcha_apply_on.created_by.readable = True
db.plugin_mailcaptcha_apply_on.created_on.readable = True
db.plugin_mailcaptcha_apply_on.modified_by.readable = True
db.plugin_mailcaptcha_apply_on.modified_on.readable = True
db.define_table( 'plugin_mailcaptcha_honeypot',
							Field( 'email', 'string',
									label = T( 'E-mail' ),
									requires = IS_NOT_EMPTY(),
									comment = T( 'If this e-mail address receives mail than the sender goes to the blacklist.' )
									),
							auth.signature
 )
db.plugin_mailcaptcha_honeypot.created_by.readable = True
db.plugin_mailcaptcha_honeypot.created_on.readable = True
db.plugin_mailcaptcha_honeypot.modified_by.readable = True
db.plugin_mailcaptcha_honeypot.modified_on.readable = True
db.define_table( 'plugin_mailcaptcha_settings',
							Field( 'webserver_url', 'string',
									label = T( 'Webserver url' ),
									requires = IS_NOT_EMPTY(),
									default = 'https://',
									comment = T( 'Like: "https://mailcaptcha.domain.com/", don\'t put application name at the end' )
									),
							Field( 'greetings', 'text',
									label = T( 'Web page message' ),
									comment = XML( T( 'It\'s a markmin!<br/>%(sender)s - sender email address' ) ),
									),
							Field( 'successful', 'text',
									label = T( 'Web page successful message' ),
									comment = XML( T( 'It\'s a markmin!<br/>%(sender)s - sender email address' ) ),
									),
							Field( 'mail_server', 'string',
									label = T( 'Mail server' ),
									requires = IS_NOT_EMPTY(),
									default = 'localhost:25'
									),
							Field( 'mail_sender', 'string',
									label = T( 'Mail sender' ),
									requires = IS_EMAIL(),
									),
							Field( 'mail_login', 'string',
									label = T( 'Mail login' ),
									),
							Field( 'mail_subject', 'string',
									label = T( 'Mail subject' ),
									),
							Field( 'mail_txt', 'text',
									label = T( 'Mail text' ),
									requires = IS_NOT_EMPTY(),
									comment = T( '%(url)s - URL, %(from)s - from email address' ),
									),
							Field( 'mail_admin_approval_subject', 'string',
									label = T( 'Admin approval subject' ),
									),
							Field( 'mail_admin_approval_txt', 'text',
									label = T( 'Admin approval text' ),
									requires = IS_NOT_EMPTY(),
									comment = T( '%(from)s - from email address' ),
									),
							Field( 'mail_notify_recipient', 'string',
									label = T( 'Mail notify recipient' ),
									comment = T( 'Comma separated list. If it\'s empty no notify will be sent.' )
									),
							Field( 'mail_notify_subject', 'string',
									label = T( 'Mail notify subject' ),
									),
							Field( 'mail_notify_txt', 'text',
									label = T( 'Mail notify text' ),
									comment = T( '%(from)s - from email address, %(client_address)s - client address, %(client_name)s - client name, %(helo_name)s - helo name, %(recipient)s - recipient, %(created_on)s - created on, %(url)s - admin url' ),
									),
							Field( 'x509_sign_keyfile', 'string',
									label = T( 'X.509 sign keyfile' ),
									),
							Field( 'x509_sign_certfile', 'string',
									label = T( 'X.509 certificate file' ),
									),
							Field( 'x509_sign_passphrase', 'string',
									label = T( 'X.509 passphrase' ),
									),
							Field( 'defer_if_permit', 'string',
									label = T( 'defer_if_permit reply text' ),
									requires = IS_NOT_EMPTY(),
									default = 'You should answer a captcha first'
									),
							Field( 'reject', 'string',
									label = T( 'reject reply text' ),
									requires = IS_NOT_EMPTY(),
									default = 'You are in our blacklist'
									),
							Field( 'recaptcha_private_key', 'string',
									label = T( 'Recaptcha private key' ),
									requires = IS_NOT_EMPTY(),
									),
							Field( 'recaptcha_public_key', 'string',
									label = T( 'Recaptcha public key' ),
									requires = IS_NOT_EMPTY(),
									),
							Field( 'recaptcha_options', 'string',
									label = T( 'Recaptcha options' ),
									),
							Field( 'listen_host', 'string',
									label = T( 'Listening hostname' ),
									default = 'localhost',
									),
							Field( 'listen_port', 'integer',
									label = T( 'Listening port' ),
									default = 9999
									),
							Field( 'queue_timeout', 'integer',
									label = T( 'Queue entry timeout' ),
									default = 1440,
									requires = IS_NOT_EMPTY(),
									comment = T( 'Time the e-mail entry is valid in the queue in minutes' ) ),
							auth.signature
 )
db.plugin_mailcaptcha_settings.created_by.readable = True
db.plugin_mailcaptcha_settings.created_on.readable = True
db.plugin_mailcaptcha_settings.modified_by.readable = True
db.plugin_mailcaptcha_settings.modified_on.readable = True
plugin_mailcaptcha_config = db( db.plugin_mailcaptcha_settings.id > 0 ).select( orderby = db.plugin_mailcaptcha_settings.id ).first()

if auth.user:
	response.menu += [
								( T( 'Mailcaptcha' ), False, False,
									[
										( T( 'Whitelist' ), True, URL( 'plugin_mailcaptcha', 'whitelist' ), [] ),
										( T( 'Blacklist' ), True, URL( 'plugin_mailcaptcha', 'blacklist' ), [] ),
										( T( 'Apply on' ), True, URL( 'plugin_mailcaptcha', 'apply_on' ), [] ),
										( T( 'Honeypot' ), True, URL( 'plugin_mailcaptcha', 'honeypot' ), [] ),
										( T( 'Settings' ), True, URL( 'plugin_mailcaptcha', 'settings' ), [] ),
										( T( 'Queue' ), True, URL( 'plugin_mailcaptcha', 'queue' ), [] ),
										( T( 'Task' ), True, URL( 'plugin_mailcaptcha', 'scheduler_task' ), [] ),
										( T( 'Run' ), True, URL( 'plugin_mailcaptcha', 'scheduler_run' ), [] ),
									] )
								]
