"""
cli.py

Sample CLI Clubhouse Client

RTC: For voice communication
"""

import os
import sys
import threading
import configparser
import keyboard
from SwSpotify import spotify,SpotifyNotRunning, SpotifyPaused #For spotify function
from time import gmtime, strftime # Timestamp
from rich.table import Table
from rich.console import Console
from clubhouse.clubhouse import Clubhouse

# Set some global variables
try:
    import agorartc
    RTC = agorartc.createRtcEngineBridge()
    eventHandler = agorartc.RtcEngineEventHandlerBase()
    RTC.initEventHandler(eventHandler)
    # 0xFFFFFFFE will exclude Chinese servers from Agora's servers.
    RTC.initialize(Clubhouse.AGORA_KEY, None, agorartc.AREA_CODE_GLOB & 0xFFFFFFFE)
    # Enhance voice quality
    if RTC.setAudioProfile(
            agorartc.AUDIO_PROFILE_MUSIC_HIGH_QUALITY_STEREO,
            agorartc.AUDIO_SCENARIO_GAME_STREAMING
        ) < 0:
        print("[-] Failed to set the high quality audio profile")
except ImportError:
    RTC = None

def set_interval(interval):
    """ (int) -> decorator

    set_interval decorator
    """
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

def write_config(user_id, user_token, user_device, filename='setting.ini'):
    """ (str, str, str, str) -> bool

    Write Config. return True on successful file write
    """
    config = configparser.ConfigParser()
    config["Account"] = {
        "user_device": user_device,
        "user_id": user_id,
        "user_token": user_token,
    }
    with open(filename, 'w') as config_file:
        config.write(config_file)
    return True

def read_config(filename='setting.ini'):
    """ (str) -> dict of str

    Read Config
    """
    config = configparser.ConfigParser()
    config.read(filename)
    if "Account" in config:
        return dict(config['Account'])
    return dict()

def process_onboarding(client):
    """ (Clubhouse) -> NoneType

    This is to process the initial setup for the first time user.
    """
    print("=" * 30)
    print("Welcome to Clubhouse!\n")
    print("The registration is not yet complete.")
    print("Finish the process by entering your legal name and your username.")
    print("WARNING: THIS FEATURE IS PURELY EXPERIMENTAL.")
    print("         YOU CAN GET BANNED FOR REGISTERING FROM THE CLI ACCOUNT.")
    print("=" * 30)

    while True:
        user_realname = input("[.] Enter your legal name (John Smith): ")
        user_username = input("[.] Enter your username (elonmusk1234): ")

        user_realname_split = user_realname.split(" ")

        if len(user_realname_split) != 2:
            print("[-] Please enter your legal name properly.")
            continue

        if not (user_realname_split[0].isalpha() and
                user_realname_split[1].isalpha()):
            print("[-] Your legal name is supposed to be written in alphabets only.")
            continue

        if len(user_username) > 16:
            print("[-] Your username exceeds above 16 characters.")
            continue

        if not user_username.isalnum():
            print("[-] Your username is supposed to be in alphanumerics only.")
            continue

        client.update_name(user_realname)
        result = client.update_username(user_username)
        if not result['success']:
            print(f"[-] You failed to update your username. ({result})")
            continue

        result = client.check_waitlist_status()
        if not result['success']:
            print("[-] Your registration failed.")
            print(f"    It's better to sign up from a real device. ({result})")
            continue

        print("[-] Registration Complete!")
        print("    Try registering by real device if this process pops again.")
        break

def print_channel_list(client, max_limit=20):
    """ (Clubhouse) -> NoneType

    Print list of channels
    """
    # Get channels and print out
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

def chat_main(client):
    """ (Clubhouse) -> NoneType

    Main function for chat
    """
    max_limit = 80
    prev_song = None
    channel_speaker_permission = False
    _wait_func = None
    _ping_func = None

    def _request_speaker_permission(client, channel_name, user_id):
        """ (str) -> bool

        Raise hands for permissions
        """
        if not channel_speaker_permission:
            client.audience_reply(channel_name, True, False)
            _wait_func = _wait_speaker_permission(client, channel_name, user_id)
            print("[/] You've raised your hand. Wait for the moderator to give you the permission.")

    @set_interval(30)
    def _ping_keep_alive(client, channel_name):
        """ (str) -> bool

        Continue to ping alive every 30 seconds.
        """
        try:
            client.active_ping(channel_name)
        except:
            time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print("["+time+"]"+" Error in _ping_keep_alive occur.")
        return True

    @set_interval(10)
    def _wait_speaker_permission(client, channel_name, user_id):
        """ (str) -> bool

        Function that runs when you've requested for a voice permission.
        """
        # Get some random users from the channel.
        _channel_info = client.get_channel(channel_name)
        if _channel_info['success']:
            for _user in _channel_info['users']:
                if _user['user_id'] != user_id:
                    user_id = _user['user_id']
                    break
            # Check if the moderator allowed your request.
            res_inv = client.accept_speaker_invite(channel_name, user_id)
            if res_inv['success']:
                print("[-] Now you have a speaker permission.")
                print("    Please re-join this channel to activate a permission.")
                return False
        return True

    @set_interval(1)
    def _update_song_bio(client, m_bio, prev_song):
        try:
            song,artist = spotify.current()
        except:
            client.update_bio(m_bio)
        else:
            if(song != prev_song):
                m_songname = "♫𝗡𝗼𝘄 𝗣𝗹𝗮𝘆𝗶𝗻𝗴: "+song+"\n♫𝗔𝗿𝘁𝗶𝘀𝘁: "+artist+"\n如果個Now playing無update可以refresh多幾次\n\n"
                new_bio = m_songname + m_bio
                try:
                    client.update_bio(new_bio)
                    prev_song = song
                except:
                    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    print("["+time+"]"+" Error updating bio.")
                    print("Song Name: "+song+"\nArtist: "+artist)

        return True

    while True:
        # Choose which channel to enter.
        # Join the talk on success.
        m_bio = ""
        user_me = client.me()
        user_id = client.HEADERS.get("CH-UserID")
        print_channel_list(client, max_limit)
        lobby_command = input("[.] Create Room(c)/ Join Room(j)/ Quit(quit)? : ")
        yes_no = ['y','n']
        if (lobby_command == 'j'):
            channel_name = input("[.] Enter channel_name: ")
            channel_info = client.join_channel(channel_name)
            if not channel_info['success']:
                # Check if this channel_name was taken from the link
                channel_info = client.join_channel(channel_name, "link", "e30=")
                if not channel_info['success']:
                    print(f"[-] Error while joining the channel ({channel_info['error_message']})")
                    continue
        elif (lobby_command == 'c'):
            channel_topic = input("[.] Enter the topic of the channel: ")
            channel_info = None
            privacy_setting = input("[.] Private?(y/n): ")
            while privacy_setting not in yes_no:
                privacy_setting = input("[.] Error! Private?(y/n): ")
            social_setting = input ("[.] Social?(y/n): ")
            while social_setting not in yes_no:
                social_setting = input("[.] Error! Social?(y/n): ")
            if(privacy_setting == 'y'):
                channel_info = client.create_channel(topic = channel_topic, is_private = True)
            elif(social_setting == 'y'):
                channel_info = client.create_channel(topic = channel_topic,is_social_mode=True)
            else:    
                channel_info = client.create_channel(topic = channel_topic)
            if not channel_info['success']:
                print("[.] Error creating the channel.")
                continue
            channel_name = channel_info['channel']
            channel_info = client.join_channel(channel_name)
            if not channel_info['success']:
                # Check if this channel_name was taken from the link
                channel_info = client.join_channel(channel_name, "link", "e30=")
                if not channel_info['success']:
                    print(f"[-] Error while joining the channel ({channel_info['error_message']})")
                    continue
        elif (lobby_command == 'quit'):
            break
        else:
            continue
        # Set up thread to update bio with song and artist
        spoti = input("Are you using spotify? (y/n)")
        if(spoti == 'y'):
            _spoti_func = _update_song_bio(client,m_bio,prev_song)
        # List currently available users (TOP 20 only.)
        # Also, check for the current user's speaker permission.
        channel_speaker_permission = False
        console = Console()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("user_id", style="cyan", justify="right")
        table.add_column("username")
        table.add_column("name")
        table.add_column("is_speaker")
        table.add_column("is_moderator")
        users = channel_info['users']
        i = 0
        for user in users:
            i += 1
            if i > max_limit:
                break
            table.add_row(
                str(user['user_id']),
                str(user['name']),
                str(user['username']),
                str(user['is_speaker']),
                str(user['is_moderator']),
            )
            # Check if the user is the speaker
            if user['user_id'] == int(user_id):
                channel_speaker_permission = bool(user['is_speaker'])
        console.print(table)
        print("Setting RTC...")
        # Check for the voice level.
        if RTC:
            token = channel_info['token']
            RTC.joinChannel(token, channel_name, "", int(user_id))
        else:
            print("[!] Agora SDK is not installed.")
            print("    You may not speak or listen to the conversation.")

        print("Setting ping...")
        # Activate pinging
        client.active_ping(channel_name)
        _ping_func = _ping_keep_alive(client, channel_name)
        _wait_func = None

        # Add raise_hands key bindings for speaker permission
        # Sorry for the bad quality
        if (lobby_command == 'j'):
            print("checking specking permission")
            if not channel_speaker_permission:

                if sys.platform == "darwin": # OSX
                    _hotkey = "9"
                elif sys.platform == "win32": # Windows
                    _hotkey = "ctrl+shift+h"

                print(f"[*] Press [{_hotkey}] to raise your hands for the speaker permission.")
                keyboard.add_hotkey(
                    _hotkey,
                    _request_speaker_permission,
                    args=(client, channel_name, user_id)
                )
        #Loop in the room
        while True:
            #Prompt Input from user
            command_input = input("Type \"help\" to check the command list\n>  ")

            #Print Current user in the room
            if(command_input == 'r'):
                channel_info = client.get_channel(channel_name)
                channel_speaker_permission = False
                console = Console()
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("user_id", style="cyan", justify="right")
                table.add_column("username")
                table.add_column("name")
                table.add_column("is_speaker")
                table.add_column("is_moderator")
                users = channel_info['users']
                i = 0
                for user in users:
                    i += 1
                    if i > max_limit:
                        break
                    table.add_row(
                        str(user['user_id']),
                        str(user['name']),
                        str(user['username']),
                        str(user['is_speaker']),
                        str(user['is_moderator']),
                    )
                    # Check if the user is the speaker
                    if user['user_id'] == int(user_id):
                        channel_speaker_permission = bool(user['is_speaker'])
                console.print(table)

            #Print Command List
            elif (command_input == "help"):
                print("r: refresh room user list")
                print("quit: quit the app")
                print("invite: invite user in the audience to speak")
                print("uninvite: move speaker to the audience")
                print("set mod: set moderator")
                print("user info: print details user info in the room")
                print("lobby: print current lobby list")

            #Invite Person to speak
            elif (command_input == 'invite'):
                id_invite = input("Enter the user_id to invite: ")
                users = channel_info['users']
                success = False
                for user in users:
                    if user['user_id'] == int(id_invite):
                        client.invite_speaker(channel_name,int(id_invite))
                        print("Invited.")
                        success = True
                if not success:
                    print("ID not found")

            #Move speak to audience
            elif (command_input == 'uninvite'):
                id_invite = input("Enter the user_id to invite: ")
                users = channel_info['users']
                success = False
                for user in users:
                    if user['user_id'] == int(id_invite):
                        client.uninvite_speaker(channel_name,int(id_invite))
                        print("Moved to audience.")
                        success = True
                if not success:
                    print("ID not found")

            #Print lobby list
            elif (command_input == 'lobby'):
                print_channel_list(client, max_limit)

            #Set Moderator
            elif (command_input == "set mod"):
                id_invite = input("Enter the user_id to set as moderator: ")
                users = channel_info['users']
                success = False
                for user in users:
                    if user['user_id'] == int(id_invite):
                        client.make_moderator(channel_name,int(id_invite))
                        print("Set.")
                        success = True
                if not success:
                    print("ID not found")

            #Print User Info
            elif (command_input == "user info"):
                users = channel_info['users']
                for user in users:
                    print(user)

            #Quit the App
            elif (command_input == 'quit'):
                break
            else:
                print("Bad input!")
        keyboard.unhook_all()

        # Safely leave the channel upon quitting the channel.
        if _ping_func:
            _ping_func.set()
        if _wait_func:
            _wait_func.set()
        if _spoti_func:
            _spoti_func.set()
            client.update_bio(m_bio)
        if RTC:
            RTC.leaveChannel()
        client.leave_channel(channel_name)

def user_authentication(client):
    """ (Clubhouse) -> NoneType

    Just for authenticating the user.
    """

    result = None
    while True:
        user_phone_number = input("[.] Please enter your phone number. (+818043217654) > ")
        result = client.start_phone_number_auth(user_phone_number)
        if not result['success']:
            print(f"[-] Error occured during authentication. ({result['error_message']})")
            continue
        break

    result = None
    while True:
        verification_code = input("[.] Please enter the SMS verification code (1234, 0000, ...) > ")
        result = client.complete_phone_number_auth(user_phone_number, verification_code)
        if not result['success']:
            print(f"[-] Error occured during authentication. ({result['error_message']})")
            continue
        break

    user_id = result['user_profile']['user_id']
    user_token = result['auth_token']
    user_device = client.HEADERS.get("CH-DeviceId")
    write_config(user_id, user_token, user_device)

    print("[.] Writing configuration file complete.")

    if result['is_waitlisted']:
        print("[!] You're still on the waitlist. Find your friends to get yourself in.")
        return

    # Authenticate user first and start doing something
    client = Clubhouse(
        user_id=user_id,
        user_token=user_token,
        user_device=user_device
    )
    if result['is_onboarding']:
        process_onboarding(client)

    return

def main():
    """
    Initialize required configurations, start with some basic stuff.
    """
    # Initialize configuration
    client = None
    user_config = read_config()
    user_id = user_config.get('user_id')
    user_token = user_config.get('user_token')
    user_device = user_config.get('user_device')

    # Check if user is authenticated
    if user_id and user_token and user_device:
        client = Clubhouse(
            user_id=user_id,
            user_token=user_token,
            user_device=user_device
        )

        # Check if user is still on the waitlist
        _check = client.check_waitlist_status()
        if _check['is_waitlisted']:
            print("[!] You're still on the waitlist. Find your friends to get yourself in.")
            return

        # Check if user has not signed up yet.
        _check = client.me()
        if not _check['user_profile'].get("username"):
            process_onboarding(client)

        chat_main(client)
    else:
        client = Clubhouse()
        user_authentication(client)
        main()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Remove dump files on exit.
        file_list = os.listdir(".")
        for _file in file_list:
            if _file.endswith(".dmp"):
                os.remove(_file)
