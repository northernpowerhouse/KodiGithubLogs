#!/usr/bin/env python3
"""
Main script for the KodiGithubLogs addon.

Provides a simple UI: authorize with GitHub (device flow), choose a repo/folder,
and upload selected logs.
"""
from __future__ import annotations

import datetime
import os
import sys
import xbmc
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')

from resources.lib.github_client import GitHubClient, GitHubError, FALLBACK_CLIENT_ID
from resources.lib import log_uploader


def _get_setting(key: str) -> str:
    return ADDON.getSetting(key) or ''


def _set_setting(key: str, value: str) -> None:
    ADDON.setSetting(key, value)


def input_text(prompt: str, default: str = '') -> str:
    kb = xbmc.Keyboard(default, prompt)
    kb.doModal()
    if kb.isConfirmed():
        return kb.getText()
    return default


def show_message(title: str, msg: str) -> None:
    xbmcgui.Dialog().ok(title, msg)


def authorize(client: str) -> str:
    gh = GitHubClient(ADDON)
    try:
        resp = gh.start_device_flow(client)
    except Exception as e:
        show_message('Device Flow Error', str(e))
        return ''
    user_code = resp.get('user_code')
    ver_uri = resp.get('verification_uri') or resp.get('verification_uri_complete')
    device_code = resp.get('device_code')
    interval = int(resp.get('interval', 5))
    expires = int(resp.get('expires_in', 900))

    # tell user to visit verification URL
    dlg = xbmcgui.Dialog()
    message = 'Go to: %s\n\nEnter code: %s' % (ver_uri, user_code)
    dlg.ok('Authorize GitHub', message)

    try:
        token = gh.poll_for_token(client, device_code, interval, expires)
    except Exception as e:
        show_message('Authorization failed', str(e))
        return ''

    # store token
    _set_setting('access_token', token)
    show_message('Authorized', 'GitHub authorization completed and token saved.')
    return token


def choose_repo(token: str):
    gh = GitHubClient(ADDON)
    try:
        repos = gh.list_repos(token)
    except Exception as e:
        show_message('Error listing repos', str(e))
        return None
    labels = [r.get('full_name') for r in repos]
    if not labels:
        show_message('No writable repos', 'No repositories with push access found for this user.')
        return None
    
    # Pre-select last used repo
    last_repo = ADDON.getSetting('last_repo')
    preselect = -1
    if last_repo:
        for i, label in enumerate(labels):
            if label == last_repo:
                preselect = i
                break
    
    sel = xbmcgui.Dialog().select('Choose repository', labels, preselect=preselect)
    if sel < 0:
        return None
    repo = repos[sel]
    
    # Save last used repo
    _set_setting('last_repo', repo.get('full_name'))
    _set_setting('selected_repo', repo.get('name'))
    _set_setting('selected_repo_owner', repo.get('owner', {}).get('login', ''))
    return repo


def choose_folder(token: str, owner: str, repo: str):
    gh = GitHubClient(ADDON)
    path = ''
    while True:
        try:
            contents = gh.list_contents(token, owner, repo, path)
        except Exception as e:
            show_message('Error', str(e))
            return None
        dirs = [c for c in contents if c.get('type') == 'dir']
        items = ['. (select this folder)', '+ (create new folder)'] + [d.get('name') + '/' for d in dirs] + (['.. (up)'] if path else [])
        sel = xbmcgui.Dialog().select('Choose folder in %s/%s' % (owner, repo), items)
        if sel < 0:
            return None
        choice = items[sel]
        if sel == 0:
            _set_setting('last_folder', path)
            _set_setting('selected_folder', path)
            return path
        # create new folder
        if sel == 1:
            folder_name = input_text('Enter new folder name')
            if folder_name:
                new_path = os.path.join(path, folder_name) if path else folder_name
                try:
                    gh.create_folder(token, owner, repo, new_path)
                    show_message('Folder created', 'Created folder: %s' % new_path)
                    path = new_path
                    continue
                except Exception as e:
                    show_message('Error creating folder', str(e))
            continue
        # up
        if choice.startswith('..'):
            path = os.path.dirname(path)
            continue
        # go into selected folder
        name = dirs[sel - 2].get('name')
        path = os.path.join(path, name) if path else name


def upload_now():
    token = _get_setting('access_token')
    if not token:
        show_message('Not authorized', 'Please authorize with GitHub first (use Authorize).')
        return
    owner = _get_setting('selected_repo_owner')
    repo = _get_setting('selected_repo')
    folder = _get_setting('selected_folder')
    if not owner or not repo:
        show_message('Repository not selected', 'Please select a repository first.')
        return
    level = _get_setting('log_level') or 'regular'
    include_old = ADDON.getSettingBool('include_old_logs')
    exclude_startup = ADDON.getSettingBool('exclude_startup_logs')
    payload = log_uploader.build_log_payload(level=level, include_old=include_old, exclude_startup=exclude_startup)
    now = datetime.datetime.utcnow().strftime('%Y%m%d%H%M')
    filename = 'kodilog%s.txt' % now
    path = filename if not folder else '%s/%s' % (folder.strip('/'), filename)
    gh = GitHubClient(ADDON)
    try:
        message = 'Upload Kodi log %s' % filename
        gh.upload_file(token, owner, repo, path, payload, message)
        show_message('Upload complete', 'Log uploaded to %s/%s' % (repo, path))
    except Exception as e:
        show_message('Upload failed', str(e))


def open_settings():
    ADDON.openSettings()


def main_menu():
    while True:
        items = ['Authorize GitHub', 'Select repository', 'Select folder (current: %s)' % (_get_setting('selected_folder') or '/'), 'Upload logs now', 'Settings', 'Exit']
        sel = xbmcgui.Dialog().select('Kodi Log Uploader', items)
        if sel == 0:
            client = _get_setting('client_id')
            if not client:
                client = FALLBACK_CLIENT_ID
                if not client:
                    client = input_text('Enter GitHub OAuth App client_id')
                    if not client:
                        continue
                _set_setting('client_id', client)
            authorize(client)
        elif sel == 1:
            token = _get_setting('access_token')
            if not token:
                show_message('Not authorized', 'Authorize first')
                continue
            choose_repo(token)
        elif sel == 2:
            token = _get_setting('access_token')
            if not token:
                show_message('Not authorized', 'Authorize first')
                continue
            owner = _get_setting('selected_repo_owner')
            repo = _get_setting('selected_repo')
            if not owner or not repo:
                show_message('Select repo first', 'Please choose a repository first')
                continue
            choose_folder(token, owner, repo)
        elif sel == 3:
            upload_now()
        elif sel == 4:
            open_settings()
        else:
            break


if __name__ == '__main__':
    try:
        main_menu()
    except Exception as e:
        xbmc.log('Kodi Log Uploader error: %s' % str(e), xbmc.LOGERROR)
