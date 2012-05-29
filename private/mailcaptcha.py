#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Exec as:
#
# python ./web2py.py -R applications/mailcaptcha/private/mailcaptcha.py -S mailcaptcha -M
# #####################################################################################
import datetime

import logging
logger = logging.getLogger( "web2py.app.mailcaptcha" )
logger.setLevel( logging.DEBUG )

import SocketServer

RET_DUNNO = "action=dunno\n\n"
RET_DEFER_IF_PERMIT = 'action=defer_if_permit %s\n\n' % plugin_mailcaptcha_config.defer_if_permit
RET_REJECT = 'action=reject %s\n\n' % plugin_mailcaptcha_config.reject

class MyTCPHandler( SocketServer.StreamRequestHandler ):
		"""
		The RequestHandler class for our server.

		It is instantiated once per connection to the server, and must
		override the handle() method to implement communication to the
		client.
		"""

		def handle( self ):
				# self.request is the TCP socket connected to the client
				self.data = dict()
				while True:
					sor = self.rfile.readline().strip()
					if sor == '' and len( self.data ) > 0:
						break
					( key, value ) = sor.split( '=', 1 )
					key = key.strip()
					value = value.strip()
					self.data[key] = value
				logger.debug( 'data: %s' % str( self.data ) )
				# we can't handle mail without recipient or sender
				# #################################################
				if not self.data.has_key( 'recipient' ) or not self.data.has_key( 'sender' ):
					logger.warning( 'No or invalid recipient or sender' )
					self.wfile.write( RET_DUNNO )
					return True

				# see if recipient is in apply_on list
				# #####################################
				try:
					domain = str( self.data['recipient'] ).lower().split( '@', 1 )[1]
				except:
					logger.warning( 'Invalid recipient: [%s]' % str( self.data['recipient'] ) )
					self.wfile.write( RET_DUNNO )
					return True
				if db( db.plugin_mailcaptcha_apply_on.email.lower() == str( self.data['recipient'] ).lower() ).count() == 0 and \
					db( db.plugin_mailcaptcha_apply_on.email.lower() == domain ).count() == 0:
					logger.debug( "Don't need to be processed" )
					self.wfile.write( RET_DUNNO )
					return True

				# we need to handle the sender
				# #############################
				# check blacklist
				try:
					domain = str( self.data['sender'] ).lower().split( '@', 1 )[1]
				except:
					logger.warning( 'Invalid sender: [%s]' % str( self.data['sender'] ) )
					self.wfile.write( RET_DUNNO )
					return True
				if db( db.plugin_mailcaptcha_blacklist.email.lower() == str( self.data['sender'] ).lower() ).count() > 0 or \
					db( db.plugin_mailcaptcha_blacklist.email.lower() == domain ).count() > 0:
					logger.info( '[%s] in backlist' % str( self.data['sender'] ) )
					self.wfile.write( RET_REJECT )
					return True

				# check whitelist
				if db( db.plugin_mailcaptcha_whitelist.email.lower() == str( self.data['sender'] ).lower() ).count() > 0 or \
					db( db.plugin_mailcaptcha_whitelist.email.lower() == domain ).count() > 0:
					logger.info( '[%s] in whitelist' % str( self.data['sender'] ) )
					self.wfile.write( RET_DUNNO )
					return True

				# check queue
				if db( db.plugin_mailcaptcha_queue.email.lower() == str( self.data['sender'] ).lower() ).count() > 0:
					logger.info( '[%s] in queue' % str( self.data['sender'] ) )
					self.wfile.write( RET_DEFER_IF_PERMIT )
					return True

				# setup a queue if email not already in
				client_address = self.data['client_address'] if self.data.has_key( 'client_address' ) else None
				client_name = self.data['client_name'] if self.data.has_key( 'client_name' ) else None
				helo_name = self.data['helo_name'] if self.data.has_key( 'helo_name' ) else None
				recipient = self.data['recipient'] if self.data.has_key( 'recipient' ) else None
				db.plugin_mailcaptcha_queue.created_on.default = datetime.datetime.now()
				id = db.plugin_mailcaptcha_queue.insert( email = str( self.data['sender'] ).lower(),
																								client_address = client_address,
																								client_name = client_name,
																								helo_name = helo_name,
																								recipient = recipient )
				# setup a scheduler task to send an email about the captcha
				db.scheduler_task.insert( 
																task_name = self.data['sender'],
																function_name = 'plugin_mailcaptcha_sendmail',
																args = '[%s]' % id,
																start_time = datetime.datetime.now(),
																next_run_time = datetime.datetime.now(),
																stop_time = datetime.datetime.now() + datetime.timedelta( days = 1 )
																)
				db.commit()
				logger.info( '[%s] set up in queue' % str( self.data['sender'] ) )
				self.wfile.write( RET_DEFER_IF_PERMIT )
				return True

				# just send back the same data, but upper-cased
				#self.request.sendall(self.data.upper())

if __name__ == "__main__":
		listen_host = plugin_mailcaptcha_config.listen_host
		listen_port = plugin_mailcaptcha_config.listen_port
		# Create the server, binding to localhost on port 9999
		server = SocketServer.TCPServer( ( listen_host, listen_port ), MyTCPHandler )

		# Activate the server; this will keep running until you
		# interrupt the program with Ctrl-C
		try:
			server.serve_forever()
		except KeyboardInterrupt, e:
			pass
