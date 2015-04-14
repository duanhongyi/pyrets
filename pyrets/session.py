# -*- coding: utf-8 -*-

import requests
import xmltodict

import socket
import hashlib
import time
import urllib.parse
from urllib.parse import urlparse, urljoin

from .exceptions import raise_rets_exception, NotLoginException


class RetsSession(object):

    def __init__(self, login_url, user, passwd, user_agent=None,
                 user_agent_passwd=None, rets_version="RETS/1.7"):
        self.user = user
        self.passwd = passwd
        self.user_agent = user_agent
        self.user_agent_passwd = user_agent_passwd
        self.rets_version = rets_version
        self.login_url = login_url
        self.session_id = ''
        # cache session
        self._session = None

    @property
    def base_url(self):
        url_parts = urlparse(self.login_url)
        resURL = url_parts.scheme + "://" + url_parts.netloc
        return resURL

    @property
    def rets_ua_authorization(self):
        a1hashed = hashlib.md5(bytes(
            self.user_agent + ':' + self.user_agent_passwd,
            'utf-8')).hexdigest()
        digestHash = hashlib.md5(bytes(
            a1hashed + ':' + self.session_id + ':' +
            self.session_id + ':' + self.rets_version,
            'utf-8')).hexdigest()
        return 'Digest ' + digestHash

    @property
    def session(self):
        if not self._session:
            raise NotLoginException("You need to call login")
        if self.user_agent_passwd:
            self._session.headers[
                'RETS-UA-Authorization'] = self.rets_ua_authorization
        return self._session

    def login(self):
        self.session_id = ''
        _session = requests.session()
        headers = {'User-Agent': self.user_agent,
                   'RETS-Version': self.rets_version,
                   'Accept': "*/*"}
        if self.user_agent_passwd:
            headers['RETS-UA-Authorization'] = self.rets_ua_authorization

        auth = requests.auth.HTTPDigestAuth(self.user, self.passwd)

        _session.headers = headers
        _session.auth = auth

        login_result = _session.get(self.login_url)
        login_result.raise_for_status()

        self.server_info = self._parse_login_response(login_result)

        if self.user_agent_passwd:
            self.session_id = login_result.cookies['RETS-Session-ID']
        self._session = _session
        return True

    def logout(self):
        if not self._session:
            return
        self.session_id = ''
        logout_url = urljoin(self.base_url, self.server_info['Logout'])
        response = self._session.get(logout_url)
        response.raise_for_status()
        return self._parse_common_response(response)

    def get_object(self, obj_type, resource, obj_id):
        getobject_url = urljoin(self.base_url, self.server_info['GetObject'])
        response = self.session.get(
            getobject_url + "?Type=%s&Resource=%s&ID=%s" % (
                obj_type, resource, obj_id))
        if 'text/xml' in response.headers['content-type']:
            return self._parse_common_response(response)
        return response.content

    def get_metadata(self):
        get_meta_url = urljoin(self.base_url, self.server_info['GetMetadata'])
        response = self.session.get(
            get_meta_url + '?Type=METADATA-SYSTEM&ID=*&Format=STANDARD-XML')
        return self._parse_common_response(response)

    def search(self, resource, search_class,
               query, limit=30, offset=0, select=""):
        params = {'SearchType': resource,
                  'Class': search_class,
                  'Query': query,
                  'QueryType': 'DMQL2',
                  'Count': 1,
                  'Format': 'COMPACT-DECODED',
                  'Limit': limit,
                  'Offset': offset,
                  'Select': select,
                  'StandardNames': '0'}
        search_url = urljoin(self.base_url, self.server_info['Search'])
        response = self.session.post(search_url, params)
        return self._parse_common_response(response)

    def _parse_login_response(self, response):
        response_dict = self._parse_common_response(response)
        rets_info = response_dict["RETS"]['RETS-RESPONSE'].split('\n')
        rets_info_dict = {}
        for info_item in rets_info:
            if info_item.strip():
                key_value_pair = info_item.split('=')
                rets_info_dict[
                    key_value_pair[0].strip()] = key_value_pair[1].strip()
        return rets_info_dict

    def _parse_common_response(self, response):
        response.raise_for_status()
        response_dict = xmltodict.parse(response.text)
        reply_code = response_dict["RETS"]["@ReplyCode"]
        reply_text = response_dict["RETS"]["@ReplyText"]
        raise_rets_exception(reply_code, reply_text)
        return response_dict
