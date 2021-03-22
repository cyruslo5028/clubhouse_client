"""
client.py

Modify from https://github.com/stypr/clubhouse-py

Recreated by: Cyrus Lo
"""
import os
import sys
import threading
import configparser
import keyboard
import agorartc
from SwSpotify import spotify,SpotifyNotRunning, SpotifyPaused #For spotify function
from time import gmtime, strftime # Timestamp
from rich.table import Table
from rich.console import Console
from clubhouse.clubhouse import Clubhouse

class client:
    def __init__(self):
        #Set Up Voice
        rtc = self.setup_rtc()
        

        
    # Set Up Voice    
    def setup_rtc(self):
        try:
            rtc = agorartc.createRtcEngineBridge()
            eventHandler = agorartc.RtcEngineEventHandlerBase()
            rtc.initEventHandler(eventHandler)
            rtc.initialize(Clubhouse.AGORA_KEY, None, agorartc.AREA_CODE_GLOB & 0xFFFFFFFE) #exclude Chinese server
            # Enhance Voice Quality
            if rtc.setAudioProfile(
                agorartc.AUDIO_PROFILE_MUSIC_HIGH_QUALITY_STEREO,
                agorartc.AUDIO_SCENARIO_GAME_STREAMING
            ) < 0:
            #if setAudioProfile return -1 -> Error
            print("Error While setting up the audio profile")
            return rtc
        except:
            rtc = None
            return rtc
            
    # Main Loop
    def check_auth(self):
        user_config = read_config()
        user_id = user_config.get('user_id')
        # User is authenticated
        if user_id != None:
            client = Clubhouse(user_id = user_id, user_token = user_config.get(user_token), user_device=user_config.get(user_device))
            _check = client.check_waitlist_status()
            if _check['is_waitlisted']:
                print("You are still on waitlist.")
                return
            _check = client.me()
            _check['user_profile'].get("username"):
            
        # Not authenticated
        else:

    # Write to config (Delete setting.ini if failed to login)
    def write_config(self,user_id, user_token, user_device, filename='setting.ini'):
        config = configparser.ConfigParser()
        config["Account"] = {
            "user_device": user_device,
            "user_id": user_id,
            "user_token": user_token,
        }
        with open(filename, 'w') as config_file:
            config.write(config_file)
        return True

    # Read from the config file
    # If Account exist, return the dict, else return empty dict
    def read_config(self, filename = 'setting.ini'):
        config = configparser.ConfigParser()
        config.read(filename)
        if "Account" in config:
            return dict(config['Account'])
        return dict()

    # Print the list of current user
    def print_channel_list (self,client,max_limit):
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("")
        table.add_column("channel_name", style="cyan", justify="right")
        table.add_column("topic")
        table.add_column("speaker_count")
        table.add_column("total_count")
        channels = client.get_channels()['channels']
        i = 0
        for channel in channels:
            i += 1
            if i > max_limit:
                break
            _option = ""
            _option += "\xEE\x85\x84" if channel['is_social_mode'] or channel['is_private'] else ""
            table.add_row(
                str(_option),
                str(channel['channel']),
                str(channel['topic']),
                str(int(channel['num_speakers'])),
                str(int(channel['num_all'])),
            )
        console.print(table)

    # For threading
    def set_interval(self,interval):
        def decorator(func):
            def wrap(*args, **kwargs):
                stopped = threading.Event()
                def loop():
                    while not stopped.wait(interval):
                        ret = func(*args, **kwargs)
                        if not ret:
                            break
                thread = threading.Thread(target=loop)
                thread.daemon = True
                thread.start()
                return stopped
            return wrap
        return decorator


if __name__ == "__main__":
    try:
        client = client()

    except Exception:
        # Remove dump files on exit.
        file_list = os.listdir(".")
        for _file in file_list:
            if _file.endswith(".dmp"):
                os.remove(_file)