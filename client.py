"""
client.py

Modify from https://github.com/stypr/clubhouse-py

Modify by: Cyrus Lo

This client won't support registering a new account
Please use a Apple device to register.
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
        self.rtc = self.setup_rtc()
        self.client = self.check_auth()

        
    def setup_rtc(self):
        '''
        Set Up Rtc:
        return the RTC on success
        return None on Fail
        '''
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
                print("> ! Error while setting up the audio profile !")
            return rtc
        except:
            rtc = None
            return rtc

    def user_authentication(self):
        '''
        Auth the user
        Prompt to ask for phone number and SMS
        write all the info to the config
        '''
        client = Clubhouse()
        # get phone number for register
        while True:
            phone_num = input("Please enter your phone number. (+12345678900/+85212345678) :")
            result = client.start_phone_number_auth(phone_num)
            if result['success'] == False:
                print("Invalid phone number. Please try again.")
                continue
            else:
                break
        # get sms verification code
        while True:
            sms_code = input("Please enter the SMS verification code :")
            result = client.complete_phone_number_auth(phone_num,sms_code)
            if result['success'] == False:
                print("Wrong SMS Code. Please try again.")
                continue
            else:
                break
        
        # On success
        user_id = result['user_profile']['user_id']
        user_token = result['auth_token']
        user_device = client.HEADERS.get("CH-DeviceId")
        self.write_config(user_id, user_token, user_device)

        print("Successfully wrote to the config file.")

    def check_auth(self):
        '''
        Check if the user is authenticated
        return a clubhouse client
        return None on error
        '''
        user_config = self.read_config()
        user_id = user_config.get('user_id')
        user_token = user_config.get('user_token')
        user_device = user_config.get('user_device')
        # User is authenticated
        if user_id != None:
            client = Clubhouse(
                user_id=user_id,
                user_token=user_token,
                user_device=user_device
            )
            _check = client.check_waitlist_status()
            #User are on the waitlist
            if _check['is_waitlisted']:
                print("> You are still on waitlist.")
                return None
            _check = client.me()
            if not _check['user_profile'].get("username"):
                print("> You havent signed up yet.")
                return None
            return client
        # Not authenticated
        else:
            print("Check auth")
            self.user_authentication()
            client = self.check_auth()
            return client

    def write_config(self,user_id, user_token, user_device, filename='setting.ini'):
        '''
        Write 
        user_id -> str 
        user_token -> str
        user_device ->str 
        to setting.ini
        '''
        config = configparser.ConfigParser()
        config["Account"] = {
            "user_device": user_device,
            "user_id": user_id,
            "user_token": user_token,
        }
        with open(filename, 'w') as config_file:
            config.write(config_file)
        return True

    def read_config(self, filename = 'setting.ini'):
        '''
        Read from setting.ini
        If Account exist, return the dict, else return empty dictionary
        '''
        config = configparser.ConfigParser()
        config.read(filename)
        if "Account" in config:
            return dict(config['Account'])
        return dict()

    def print_channel_list (self,client,max_limit):
        '''
        Print Channel List
        client -> clubhouse()
        max_limit -> int (number of room to print)
        '''
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

    def set_interval(self,interval):
        '''
        This function for threading
        interval -> int (seconds)
        '''
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

    def _request_speaker_permission(self,channel_name, user_id):
        '''
        request for the speaker permission
        '''
        pass

    '''
    Main Client Loop
    '''
    def run(self):


if __name__ == "__main__":
    try:
        client = client()
        client.run()
    except Exception:
        # Remove dump files on exit.
        file_list = os.listdir(".")
        for _file in file_list:
            if _file.endswith(".dmp"):
                os.remove(_file)