# -*- coding: utf-8 -*-
import socket
import hashlib
import time
import urllib.parse
import requests
import xmltodict
from urllib.parse import urlparse, urljoin

from .exceptions import NoLoginException



class RetsSession(object):

    def __init__(self, user, passwd, user_agent, user_agent_passwd, rets_version, login_url):
        self.rets_ua_authorization = None
        self.user = user
        self.passwd = passwd
        self.user_agent = user_agent
        self.user_agent_passwd = user_agent_passwd
        self.rets_version = rets_version
        self.base_url = self._get_base_url(login_url)
        self.login_url = login_url
        self._session = None
        self.login_called = False

         
    def _get_base_url(self, url_str):
        url_parts = urlparse(url_str)
        resURL = url_parts.scheme + "://" + url_parts.netloc
        return resURL
        
    def _set_rets_ua_authorization(self):
        self._session.headers['RETS-UA-Authorization'] = self.rets_ua_authorization;

    def _calculate_rets_ua_authorization(self, sid, user_agent, user_agent_passwd, rets_version):
        product = user_agent
        a1hashed = hashlib.md5(bytes(product + ':' + user_agent_passwd, 'utf-8')).hexdigest()
        retsrequestid = ''
        retssessionid = sid
        digestHash = hashlib.md5(bytes(a1hashed + ':' + retsrequestid + ':' + retssessionid + ':' + rets_version, 'utf-8')).hexdigest()
        return 'Digest ' + digestHash

    def login(self):
        self._session = requests.session()
        
        headers = {'User-Agent':self.user_agent,
               'RETS-Version':self.rets_version,
               'Accept':"*/*"}
        
        if self.user_agent_passwd:
            headers['RETS-UA-Authorization'] = self._calculate_rets_ua_authorization(''
                                                                            , self.user_agent
                                                                            , self.user_agent_passwd
                                                                            , self.rets_version)
            
        auth = requests.auth.HTTPDigestAuth(self.user, self.passwd)
        
        self._session.headers = headers
        self._session.auth = auth

        login_result = self._session.get(self.login_url)
        login_result.raise_for_status()
        
        self.server_info = xmltodict.parse(ogin_result.text)
        
        if self.user_agent_passwd:
            self.rets_ua_authorization = self._calculate_rets_ua_authorization(login_result.cookies['RETS-Session-ID']
                                                                            , self.user_agent
                                                                            , self.user_agent_passwd
                                                                           , self.rets_version)
        self.login_called = True
        return true

    def logout(self):
        if not self.login_called:
            raise NoLoginException("You need to call login before logout")
        
        logout_url = urljoin(self.base_url, self.server_info['Logout'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        logout_response = self._session.get(logout_url)
        logout_response.raise_for_status()
        return xmltodict.parse(logout_response.text)

    def getobject(self, obj_type, resource , obj_id):
        if not self.login_called:
            raise NoLoginException("You need to call login before getobject")
        getobject_url = urljoin(self.base_url, self.server_info['GetObject'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        getobject_response = self._session.get(getobject_url + "?Type=%s&Resource=%s&ID=%s" % (obj_type, resource, obj_id))
        getobject_response.raise_for_status()
        return xmltodict.parse(getobject_response.content)

                
    def getmetadata(self):
        if not self.login_called:
            raise NoLoginException("You need to call login before getmetadata")
        
        get_meta_url = urljoin(self.base_url, self.server_info['GetMetadata'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        response = self._session.get(get_meta_url + '?Type=METADATA-SYSTEM&ID=*&Format=STANDARD-XML')
        response.raise_for_status()
        return xmltodict.parse(response.text)
    
    def search(self, resource, search_class, query, limit, select):
        if not self.login_called:
            raise NoLoginException("You need to call login before search")
        
        if limit:
            limit = 'NONE'
        params = {'SearchType': resource,
                  'Class': search_class,
                  'Query': query,
                  'QueryType': 'DMQL2',
                  'Count': '0',
                  'Format': 'COMPACT-DECODED',
                  'Limit': limit,
                  'Select': select,
                  'StandardNames': '0'}
        search_url = urljoin(self.base_url, self.server_info['Search'])
        if self.user_agent_passwd:
            self._set_rets_ua_authorization()
        search_response = self._session.post(search_url, params)
        search_response.raise_for_status()
        return xmltodict.parse(search_response.text)
