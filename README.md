MailCaptcha
===========

For e-mail address protection with recaptcha for postfix.

If somebody send an e-mail to a protected address the MailCaptcha
defer it with 4xx temporary failure and send an e-mail to the
sender with the URL where the sender can solve the captcha and get
their e-mail address to the whitelist. After that the mail system
is accepting the e-mail address.

There is a
* whitelist (you can put e-mail address or only domain in it without @)
* blacklist (you can put e-mail address or only domain in it without @)
* honeypot e-mail list (you can put e-mail address or only domain in it without @)
* notification to the mail system administrator
* sent mail can be signed with x.509 certificate

Requirements
============

* web2py 1.99.7 (http://web2py.com)
* postfix (http://postfix.com)

What does this?
===============

1. somebody send you an email from somebody@domain.com
2. postfix ask MailCaptcha what to do
 1. if the recipient address is not in the protected list do nothing special
 2. else if the sender is in the blacklist reject the message with 5xx code
 3. else if the recipient address is a honeypot address but the sender in the blacklist and reject the message with 5xx code
 4. else if the sender is in the whitelist do nothing special
 5. else if the sender is in the waiting queue the message get a temporary rejection with 4xx code
 6. else if the sender is not in queue then
  - put the sender address in the waiting queue
  - send a mail to the sender address with the web url where the sender can solve the captcha and so the sender address is going to the whitelist
  - optionally send a mail to mail system admin to notify about a new sender address in the waiting queue so admin can enable the sender address by hand
3. the sender have to go to the web url and solve the captcha
4. sender address is going to the whitelist
5. the next time the sender's mail system (the system that hold the sender's mail) try to deliver the e-mail after temporary failure can deliver the message without problem

 

Credit
======

The main idea is from:
 http://www.kfki.hu/cnc/projekt/postfilter/indexeng.html
 http://www.kfki.hu/cnc/projekt/postfilter/docs/README.txt

 József Kadlecsik

 together with the members of "CSI-KO Csillebérci Komputer" Company.