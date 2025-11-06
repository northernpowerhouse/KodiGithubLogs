# -*- coding: utf-8 -*-
"""
Minimal GitHub client using the Device Authorization Flow and the REST API.

This implementation uses only the Python standard library so it can run inside
Kodi's Python environment without extra dependencies.

A default GitHub OAuth App client_id is included for convenience. Advanced users
can optionally create their own OAuth App at https://github.com/settings/developers
and update the FALLBACK_CLIENT_ID constant or enter it in addon settings.
"""
from __future__ import annotations

import base64
import json
import time
import urllib.request
import urllib.parse
from typing import List, Optional, Dict, Any

GITHUB_DEVICE_URL = "https://github.com/login/device/code"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API = "https://api.github.com"

# Default GitHub OAuth App client_id for Kodi Log Uploader
# Users can optionally create their own at: https://github.com/settings/developers
FALLBACK_CLIENT_ID = "Ov23liJRn4sGR9ixKu3w"


class GitHubError(Exception):
    pass


class GitHubClient:
    def __init__(self, addon):
        self.addon = addon

    def _request(self, url: str, method: str = 'GET', data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        if headers is None:
            headers = {}
        req = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                ct = resp.headers.get('Content-Type', '')
                if 'application/json' in ct or url.endswith('.json') or (raw.strip().startswith(b'{') or raw.strip().startswith(b'[')):
                    return json.loads(raw.decode('utf-8', errors='ignore'))
                return raw
        except urllib.error.HTTPError as e:
            body = None
            try:
                body = e.read().decode('utf-8', errors='ignore')
            except Exception:
                body = ''
            raise GitHubError(f'HTTP {e.code} {e.reason}: {body}')

    def start_device_flow(self, client_id: str, scope: str = 'repo') -> Dict[str, Any]:
        data = urllib.parse.urlencode({'client_id': client_id, 'scope': scope}).encode('utf-8')
        headers = {'Accept': 'application/json'}
        return self._request(GITHUB_DEVICE_URL, method='POST', data=data, headers=headers)

    def poll_for_token(self, client_id: str, device_code: str, interval: int, expires_in: int) -> str:
        start = time.time()
        headers = {'Accept': 'application/json'}
        while True:
            if time.time() - start > expires_in:
                raise GitHubError('Device code expired')
            data = urllib.parse.urlencode({
                'client_id': client_id,
                'device_code': device_code,
                'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            }).encode('utf-8')
            resp = self._request(GITHUB_TOKEN_URL, method='POST', data=data, headers=headers)
            if isinstance(resp, dict):
                if 'access_token' in resp:
                    return resp['access_token']
                if 'error' in resp:
                    err = resp.get('error')
                    if err == 'authorization_pending':
                        time.sleep(interval)
                        continue
                    if err == 'slow_down':
                        interval += 5
                        time.sleep(interval)
                        continue
                    raise GitHubError('Authorization failed: ' + err)
            time.sleep(interval)

    def get_user(self, token: str) -> Dict[str, Any]:
        headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
        return self._request(GITHUB_API + '/user', headers=headers)

    def list_repos(self, token: str) -> List[Dict[str, Any]]:
        headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
        page = 1
        items: List[Dict[str, Any]] = []
        while True:
            url = f"{GITHUB_API}/user/repos?per_page=100&page={page}"
            resp = self._request(url, headers=headers)
            if not isinstance(resp, list):
                break
            items.extend(resp)
            if len(resp) < 100:
                break
            page += 1
        # Keep only repos where user has push access
        writable = [r for r in items if r.get('permissions', {}).get('push')]
        return writable

    def list_contents(self, token: str, owner: str, repo: str, path: str = '') -> List[Dict[str, Any]]:
        headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
        p = urllib.parse.quote(path or '')
        url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{p}"
        resp = self._request(url, headers=headers)
        if isinstance(resp, list):
            return resp
        # if file or other, return empty list
        return []

    def get_file_sha(self, token: str, owner: str, repo: str, path: str) -> Optional[str]:
        headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
        p = urllib.parse.quote(path)
        url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{p}"
        try:
            resp = self._request(url, headers=headers)
            if isinstance(resp, dict):
                return resp.get('sha')
        except GitHubError:
            return None
        return None

    def upload_file(self, token: str, owner: str, repo: str, path: str, content_bytes: bytes, message: str) -> Dict[str, Any]:
        headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
        b64 = base64.b64encode(content_bytes).decode('ascii')
        sha = self.get_file_sha(token, owner, repo, path)
        body = {'message': message, 'content': b64}
        if sha:
            body['sha'] = sha
        data = json.dumps(body).encode('utf-8')
        url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}"
        return self._request(url, method='PUT', data=data, headers=headers)

    def create_folder(self, token: str, owner: str, repo: str, folder_path: str) -> Dict[str, Any]:
        """Create a folder by creating a .gitkeep file inside it.
        
        GitHub doesn't support empty directories, so we create a placeholder file.
        """
        keep_path = f"{folder_path.strip('/')}/.gitkeep"
        message = f"Create folder {folder_path}"
        placeholder = b"# Placeholder file to create directory\n"
        return self.upload_file(token, owner, repo, keep_path, placeholder, message)

