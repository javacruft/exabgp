# encoding: utf-8
"""
timer.py

Created by Thomas Mangin on 2012-07-21.
Copyright (c) 2009-2015 Exa Networks. All rights reserved.
"""

import time

from exabgp.logger import Logger
from exabgp.bgp.message import _NOP
from exabgp.bgp.message import KeepAlive
from exabgp.bgp.message import Notify

# ================================================================ ReceiveTimer
# Track the time for keepalive updates


class ReceiveTimer (object):
	def __init__ (self, session, holdtime, code, subcode, message=b''):
		self.logger = Logger()
		self.session = session

		self.holdtime = holdtime
		self.last_read = time.time()
		self.last_print = 0

		self.code = code
		self.subcode = subcode
		self.message = message

	def check_ka (self, message=_NOP,ignore=_NOP.TYPE):
		if message.TYPE != ignore:
			self.last_read = time.time()
		if self.holdtime:
			left = int(self.last_read  + self.holdtime - time.time())
			if self.last_print != left:
				self.logger.timers('Receive Timer %d second(s) left' % left,source=self.session())
				self.last_print = left
			if left <= 0:
				raise Notify(self.code,self.subcode,self.message)
		elif message.TYPE == KeepAlive.TYPE:
			raise Notify(2,6,'Negotiated holdtime was zero, it was invalid to send us a keepalive messages')


class SendTimer (object):
	def __init__ (self, session, holdtime):
		self.logger = Logger()
		self.session = session

		self.keepalive = holdtime.keepalive()
		self.last_sent = int(time.time())
		self.last_print = 0

	def need_ka (self):
		if not self.keepalive:
			return False

		now  = int(time.time())
		left = self.last_sent + self.keepalive - now

		if now != self.last_print:
			self.logger.timers('Send Timer %d second(s) left' % left,source=self.session())
			self.last_print = now

		if left <= 0:
			self.last_sent = now
			return True
		return False
