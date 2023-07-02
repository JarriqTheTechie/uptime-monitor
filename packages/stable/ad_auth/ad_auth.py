import datetime
import socket

import pywintypes
import win32api
import win32con
import win32security
import yaml
from flask import redirect, url_for, session, request

from application.models.Login import Login
from helpers import getByDot


def ad_auth(username, password, redirect_url):
    username = username.lower()
    domain = getByDot(yaml.load(open("config/config.yaml", "r"), Loader=yaml.FullLoader), "admin.ldap_domain")
    try:
        token = win32security.LogonUser(
            username,
            domain,
            password,
            win32security.LOGON32_LOGON_NETWORK,
            win32security.LOGON32_PROVIDER_DEFAULT)
        if bool(token):
            session['username'] = username
            impersonator = Impersonate(username, password, domain)

            # Get Username by impersonating user
            impersonator.logon()
            fullname = win32api.GetUserNameEx(3)
            impersonator.logoff()
            session['fullname'] = fullname
            # Get user IP Address
            try:
                ip = str(socket.gethostbyaddr(request.remote_addr)[0])
            except socket.herror:
                ip = 'Unresolved'
            Login.create({
                "username": username,
                "ip": ip,
                "last_login": datetime.datetime.now(),
            })
            return redirect(redirect_url)
    except pywintypes.error:
        return redirect(url_for('login'))



class Impersonate:
    def __init__(self, login, password, domain):
        self.domain = domain
        self.login = login
        self.password = password

    def logon(self):
        self.handle = win32security.LogonUser(self.login, self.domain,self.password,win32con.LOGON32_LOGON_INTERACTIVE,win32con.LOGON32_PROVIDER_DEFAULT)
        win32security.ImpersonateLoggedOnUser(self.handle)

    def logoff(self):
        win32security.RevertToSelf() # terminates impersonation
        self.handle.Close() # guarantees cleanup


