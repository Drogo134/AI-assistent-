#!/usr/bin/env python3
try:
    from dbus import SessionBus, Interface
    bus = SessionBus()
    def _playerlist() -> list:
        return [service for service in bus.list_names() if service.startswith('org.mpris.MediaPlayer2.')]
except Exception:
    bus = None
    def _playerlist() -> list:
        return []

def playpause() -> int:
    players = _playerlist()
    worked = len(players)
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                player.PlayPause(dbus_interface='org.mpris.MediaPlayer2.Player')
        except:
            worked -= 1
    return worked

def next() -> int:
    players = _playerlist()
    worked = len(players)
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                player.Next(dbus_interface='org.mpris.MediaPlayer2.Player')
        except:
            worked -= 1
    return worked

def prev() -> int:
    players = _playerlist()
    worked = len(players)
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                player.Previous(dbus_interface='org.mpris.MediaPlayer2.Player')
        except:
            worked -= 1
    return worked

def stop() -> int:
    players = _playerlist()
    worked = len(players)
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                player.Stop(dbus_interface='org.mpris.MediaPlayer2.Player')
        except:
            worked -= 1
    return worked

def volumeup() -> int:
    players = _playerlist()
    worked = len(players)
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                properties = Interface(player, dbus_interface='org.freedesktop.DBus.Properties')
                volume = properties.Get('org.mpris.MediaPlayer2.Player', 'Volume')
                properties.Set('org.mpris.MediaPlayer2.Player', 'Volume', volume+0.2)
        except:
            worked -= 1
    return worked

def volumedown() -> int:
    players = _playerlist()
    worked = len(players)
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                properties = Interface(player, dbus_interface='org.freedesktop.DBus.Properties')
                volume = properties.Get('org.mpris.MediaPlayer2.Player', 'Volume')
                properties.Set('org.mpris.MediaPlayer2.Player', 'Volume', volume-0.2)
        except:
            worked -= 1
    return worked

def status() -> list:
    players = _playerlist()
    details = []
    for player in players:
        try:
            if bus:
                player = bus.get_object(player, '/org/mpris/MediaPlayer2')
                properties = Interface(player, dbus_interface='org.freedesktop.DBus.Properties')
                metadata = properties.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
                Title = metadata['xesam:title'] if 'xesam:title' in metadata else 'Unknown'
                Artist = metadata['xesam:artist'][0] if 'xesam:artist' in metadata else 'Unknown'
                PlayStatus = properties.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
                details.append({'status': str(PlayStatus), 'title': str(Title), 'artist': str(Artist)})
        except:
            pass
    return details


