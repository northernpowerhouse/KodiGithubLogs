# -*- coding: utf-8 -*-
"""
Helpers for reading Kodi logs with simple filters (level, startup trimming).
"""
from __future__ import annotations

import os
import re
import xbmc


def _translate(path: str) -> str:
    return xbmc.translatePath(path)


def read_logs(include_old: bool = True) -> str:
    """Read kodi.log and optionally kodi.old and return combined text."""
    log_paths = ["special://logpath/kodi.log"]
    if include_old:
        log_paths.append("special://logpath/kodi.old")
    parts = []
    for p in log_paths:
        try:
            fp = _translate(p)
            xbmc.log('KodiGithubLogs: Checking log path: %s -> %s' % (p, fp), xbmc.LOGINFO)
            if not os.path.exists(fp):
                xbmc.log('KodiGithubLogs: Log file does not exist: %s' % fp, xbmc.LOGWARNING)
                continue
            with open(fp, 'rb') as f:
                raw = f.read()
                xbmc.log('KodiGithubLogs: Read %d bytes from %s' % (len(raw), fp), xbmc.LOGINFO)
                try:
                    txt = raw.decode('utf-8')
                except Exception:
                    txt = raw.decode('latin-1', errors='ignore')
                parts.append(txt)
        except Exception as e:
            xbmc.log('KodiGithubLogs: Error reading log %s: %s' % (p, str(e)), xbmc.LOGERROR)
            continue
    result = "\n----\n".join(parts)
    xbmc.log('KodiGithubLogs: Total log text length: %d' % len(result), xbmc.LOGINFO)
    return result


def filter_by_level(text: str, level: str = 'regular') -> str:
    """Filter log text for regular/debug/trace.

    - regular: remove lines with DEBUG or TRACE
    - debug: include DEBUG, remove TRACE
    - trace: include all
    """
    if level == 'trace':
        return text
    out_lines = []
    for line in text.splitlines():
        if level == 'regular':
            if 'DEBUG' in line or 'TRACE' in line:
                continue
        elif level == 'debug':
            if 'TRACE' in line:
                continue
        out_lines.append(line)
    return '\n'.join(out_lines)


def trim_startup(text: str) -> str:
    """Remove initial startup lines up to first likely 'start' marker.
    
    Uses multiple heuristics to find where the main log content begins,
    skipping over initialization, skin loading, codec detection, etc.
    """
    # Multiple pattern groups, ordered by reliability
    patterns_groups = [
        # Main Kodi start messages
        [r'\bStarting Kodi\b', r'\bKodi.*\bstarted\b', r'\bWelcome to Kodi\b'],
        # Application initialization complete
        [r'\bapplication successfully started\b', r'\bStartup done\b', r'\binitialization complete\b'],
        # First user action or main window
        [r'\bactivate window\b', r'\bCEventServer.*started\b', r'\bJSON-RPC.*started\b'],
        # Fallback: first info/notice after lots of debug
        [r'\bNOTICE\b.*\bLoaded skin\b', r'\bNOTICE\b.*\bfrom\b'],
    ]
    
    lines = text.splitlines()
    best_match = None
    
    # Try each pattern group
    for patterns in patterns_groups:
        regex = re.compile('|'.join(patterns), re.IGNORECASE)
        for i, line in enumerate(lines):
            if regex.search(line):
                # Prefer earlier matches from more reliable patterns
                if best_match is None or i < best_match:
                    best_match = i
                break
        if best_match is not None:
            break
    
    if best_match is not None:
        # Keep a few lines before the match for context (max 5)
        start = max(0, best_match - 2)
        return '\n'.join(lines[start:])
    
    # Final fallback: if log is very long, skip first 20% as likely startup
    if len(lines) > 200:
        skip = int(len(lines) * 0.15)
        return '\n'.join(lines[skip:])
    
    # Return original if we can't determine startup
    return text


def build_log_payload(level: str = 'regular', include_old: bool = True, exclude_startup: bool = False) -> bytes:
    txt = read_logs(include_old=include_old)
    txt = filter_by_level(txt, level)
    if exclude_startup:
        txt = trim_startup(txt)
    return txt.encode('utf-8', errors='replace')
