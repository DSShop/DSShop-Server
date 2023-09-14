try:
    import flask, os, rainbowtext, json, pymongo, random, string, time, requests, hashlib, subprocess, sys
    import urllib.request
    from flask import Flask, render_template, redirect, request
    from colorama import Fore
    from InquirerPy import prompt
    from InquirerPy.exceptions import InvalidArgument
    from InquirerPy.validator import PathValidator
except ImportError:
    print('DSShop Server - ERROR!\nThe DSShop Server encountered an error due to missing dependencies.')

    response = input('Start AutoRepair? [Y/N] ')

    if response.lower() == "y":
        import subprocess, sys
        print('\nInstalling requests package.')
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], stdout=subprocess.DEVNULL)
        print('Done! Downloading package list.')
        import requests, os
        r = requests.get('https://cdn.discordapp.com/attachments/1102656107442343936/1150386783205478411/requirements.txt')

        if r.status_code == 200:
            package_list = r.text.split('\n')
            for package in package_list:
                if package:
                    print('Installing: ' + package)
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL)
                    print('Done installing: ' + package)

            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')

            print('All required packages installed successfully. Please restart the server.')
        else:
            print('Failed to download package list.')

    exit()

def clear():

    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def key_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def logger(user, logtype, log, url):

    data = {}
    data["username"] = "DSShop Server | Logger"

    logtypes = {
        "neutral": "Neutral",
        "warning": "Warning",
        "error": "Error",
        "fatal": "Fatal Error",
        "test": "Testing"
    }

    data["embeds"] = []
    embed = {}
    embed["title"] = logtypes[logtype]
    embed["description"] = log
    embed["author"] = {}
    embed["author"]["name"] = user
    data["embeds"].append(embed)

    result = requests.post(url, json=data, headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return { 'response': 'ERROR!', 'code': 'error', 'status': 'failed', 'http_response': result.status_code }
    else:
        return { 'response': 'Payload delivered', 'code': 'payload_delivered', 'status': 'success', 'http_response': result.status_code }



config = json.load(open('config.json', 'r'))
MONGO_URL = os.environ.get('DSSHOP_SERVER_MONGO_URL')
clear()
print('[!] Connecting to the database...')

if MONGO_URL == None:
    print('DSShop Server - ERROR!\nThe DSShop Server encountered an error due to missing MongoDB database. Possible fixes:\nWindows: Add it to your PATH.\nLinux: Before running the server, run: export DSSHOP_SERVER_MONGO_URL=your_mongodb_database_url_here and run the server again.\nExiting.')
    exit()


con = pymongo.MongoClient(MONGO_URL)
db = con['dsshop']
authdb = db['serverauth']
tipsdb = db['tips']

clear()

if config['firsttime']:

    print('DSShop Server Setup - Colors setup\nDo you want to enable colors? Do this only if your terminal supports them.')
    response = input('[Y/N] ')

    if str(response).lower() == 'y':

        with open('config.json', 'r') as f:
            r = json.load(f)
        
        r['colors'] = True
        r['firsttime'] = False

        with open('config.json', 'w') as f:
            json.dump(r, f, indent=6)
        
        config = json.load(open('config.json', 'r'))

    else:
        if str(response).lower() == 'n':
            with open('config.json', 'r') as f:
                r = json.load(f)
        
            r['firsttime'] = False

            with open('config.json', 'w') as f:
                json.dump(r, f, indent=6)
            
    
    clear()

linked_user = None

if config['colors']:
    print(rainbowtext.text('DSShop Server Setup') + Fore.RESET + ' - Link Discord Account')
    r1 = input('Please link your Discord Account with the DSShop Bot.\nCode: ')

    linked_user = authdb.find_one({ 'code': int(r1) })
    
    if linked_user == None or linked_user == ' ':
        print(Fore.RED + '[!!] ' + Fore.RESET + 'Failed to authenticate. Are you sure the code is right?')
        exit()
        
    print(Fore.YELLOW + '[?] ' + Fore.RESET + 'Log in as ' + linked_user['user'] + '?')
    r = input('[Y/N] ')
    if str(r).lower() == 'y':
        authdb.delete_one({ 'code': int(r1) })
        clear()
        pass
    else:
        exit()
else:
    print('DSShop Server Setup' + Fore.RESET + ' - Link Discord Account')
    r1 = input('Please link your Discord Account with the DSShop Bot.\nCode: ')

    linked_user = authdb.find_one({ 'code': int(r1) })
    
    if linked_user == None or linked_user == ' ':
        print('[!!] ' + 'Failed to authenticate. Are you sure the code is right?')
        exit()
        
    print('[?] '+ 'Log in as ' + linked_user['user'] + '?')
    r = input('[Y/N] ')
    if str(r).lower() == 'y':
        authdb.delete_one({ 'code': int(r1) })
        clear()
        pass
    else:
        exit()

if config['webhook']['enabled']:
    logger(str(linked_user['user']), 'neutral', str(linked_user['user']) + ' Logged in.', config['webhook']['url'])

tips = []

for xyz in tipsdb.find():
    tips.append({ 'tip': xyz['tip'], 'createdby': xyz['creator'] })

if config['colors']:
    print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Panel' + ' | Linked account: ' + linked_user['user'] + '\n')
    tip = random.choice(tips)
    print('Random tip: ' + tip['tip'] + '\nTip by: ' + tip['createdby'] +'\n')
else:
    print('DSShop Server - Panel | Linked account: ' + linked_user['user'] + '\n')
    tip = random.choice(tips)
    print('Random tip: ' + tip['tip'] + '\nTip by: ' + tip['createdby'] +'\n')

def is_setup(result):
    return result[0] == "Setup Server"

questions = [
    {
        "message": "Select a option.",
        "type": "list",
        "choices": [("Start Server" if config['setup'] else "Setup Server"), "Keys", "Extras"],
    }
]

try:
    result = prompt(questions, vi_mode=True)
except InvalidArgument:
    print("No available choices")

if result[0] == "Setup Server":    
    clear()

    if config['colors']:
        print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Setup' + ' | Linked account: ' + linked_user['user'])
        print('\n' + Fore.YELLOW + '[?] ' + Fore.RESET + 'Do you want to see what will happen during the process?')
        r = input('[Y/N] ')
        if str(r).lower() == 'y':
            print(Fore.YELLOW + '[!]' + Fore.RESET + 'Here is what happens during the process:')
            print(f'''
            
- Create folder "roms": All the uploaded roms go there.
- Create folder "utils": All the utilities go there.
- Create file "roms.json": Like a database, all the roms will be there, with their download links and other stuff.
- Create default authentication key: You can see it in the config.json. You can create new keys under this panel. Keys > Create new key.
- Download server: Download the server, containing the endpoints and the backend.                 
- Logs: Setup logging via Discord.

            ''')
        
        print(Fore.YELLOW + '[?] '+ Fore.RESET + 'Start setup?')
        r = input('[Y/N] ')

        if str(r).lower() == 'y':
            os.mkdir('roms')
            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Created folder: roms.')
            os.mkdir('utils')
            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Created folder: utils.')
            file = open('roms.json', 'w')
            file.write('{}')
            file.close()
            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Created file: roms.json')
            
            with open('config.json', 'r') as f:
                r = json.load(f)
            
            r['keys']['admin'] = { 'name': 'admin', 'key': key_generator(24)}

            with open('config.json', 'w') as f:
                json.dump(r, f, indent=5)

            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Created key: admin.')

            urllib.request.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")

            clear()

        if str(r).lower() == 'n':
            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Aborted.')
            exit()

        print(Fore.YELLOW + '[?] ' + Fore.RESET + 'Do you want to set up Discord logging? (You can do this later)')
        r = input('[Y/N] ')
        
        if str(r).lower() == 'y':
            clear()

            while True:
                print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Setup Discord Logs' + ' | Linked account: ' + linked_user['user'])
                print(Fore.YELLOW + '[?] ' + Fore.RESET + 'Please provide a Discord Webhook URL.')
                url = input('Webhook URL: ')
                response = logger('The DSShop Server', 'test', 'If you see this message, the example payload has been sent from the DSShop Server Setup.', url)
                
                if response['http_response'] == 204:
                    break

                if response['http_response'] == 400:
                    print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Invalid webhook URL.\nRetrying in 5 seconds.')
                    time.sleep(5)
                    clear()
                
                if not response['http_response'] == (400 or 204):
                    print(Fore.RED + '[!!] ' + Fore.RESET + 'Unknown error.\nRetrying in 5 seconds.')
                    time.sleep(5)
                    clear()
            
            with open('config.json', 'r') as f:
                r = json.load(f)
            
            r['webhook']['enabled'] = True
            r['webhook']['url'] = url
            r['setup'] = True

            with open('config.json', 'w') as f:
                json.dump(r, f, indent=5)

            clear()
            print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Setup Discord Logs' + ' | Linked account: ' + linked_user['user'])
            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Done! Please restart the server.')
            exit()
        
        if str(r).lower() == 'n':
            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Aborted.')
            exit()

    if config['colors'] == False:
        print('DSShop Server ' +  '- Setup' + ' | Linked account: ' + linked_user['user'])
        print('\n' + '[?] ' + 'Do you want to see what will happen during the process?')
        r = input('[Y/N] ')
        if str(r).lower() == 'y':
            print('[!] Here is what happens during the process:')
            print(f'''
            
- Create folder "roms": All the uploaded roms go there.
- Create folder "utils": All the utilities go there.
- Create file "roms.json": Like a database, all the roms will be there, with their download links and other stuff.
- Create default authentication key: You can see it in the config.json. You can create new keys under this panel. Keys > Create new key.
- Download server: Download the server, containing the endpoints and the backend.
- Logs: Setup logging via Discord.

            ''')
        
        print('[?] ' + 'Start setup?')
        r = input('[Y/N] ')

        if str(r).lower() == 'y':
            os.mkdir('roms')
            print('[!] ' + 'Created folder: roms.')
            os.mkdir('utils')
            print('[!] ' + 'Created folder: utils.')
            file = open('roms.json', 'w')
            file.write('{}')
            file.close()
            print('[!] ' + 'Created file: roms.json')
            
            with open('config.json', 'r') as f:
                r = json.load(f)
            
            r['keys']['admin'] = { 'name': 'admin', 'key': key_generator(24)}

            with open('config.json', 'w') as f:
                json.dump(r, f, indent=5)

            print('[!] ' + 'Created key: admin.')
            clear()

        if str(r).lower() == 'n':
            print('[!] ' +  'Aborted.')
            exit()

        print('[?] ' + 'Do you want to set up Discord logging? (You can do this later)')
        r = input('[Y/N] ')
        
        if str(r).lower() == 'y':
            clear()

            while True:
                print('DSShop Server ' + '- Setup Discord Logs' + ' | Linked account: ' + linked_user['user'])
                print('[?] ' + 'Please provide a Discord Webhook URL.')
                url = input('Webhook URL: ')
                response = logger('The DSShop Server', 'test', 'If you see this message, the example payload has been sent from the DSShop Server Setup.', url)
                
                if response['http_response'] == 204:
                    break

                if response['http_response'] == 400:
                    print('[!] ' + 'Invalid webhook URL.\nRetrying in 5 seconds.')
                    time.sleep(5)
                    clear()
                
                if not response['http_response'] == (400 or 204):
                    print('[!!] ' + 'Unknown error.\nRetrying in 5 seconds.')
                    time.sleep(5)
                    clear()
            
            with open('config.json', 'r') as f:
                r = json.load(f)
            
            r['webhook']['enabled'] = True
            r['webhook']['url'] = url
            r['setup'] = True

            with open('config.json', 'w') as f:
                json.dump(r, f, indent=5)

            clear()
            print('DSShop Server ' + '- Setup Discord Logs' + ' | Linked account: ' + linked_user['user'])
            print('[!] ' + 'Done! Please restart the server.')
            exit()
        
        if str(r).lower() == 'n':
            print('[!] ' + 'Aborted.')
            exit()

#!!! TODO: Add the download server part.!!!!

if result[0] == "Keys":
    clear()
    
    if config['colors']:
        print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Keys management' + ' | Linked account: ' + linked_user['user'] +'\n')
        
        questions2 = [
            {
                "message": "Select a option.",
                "type": "list",
                "choices": ["Disable a key", "Create new key"],
            }
        ]

        try:
            result2 = prompt(questions2, vi_mode=True)
        except InvalidArgument:
            print("No available choices")

        if result2[0] == "Create new key":
            clear()
            print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Keys management' + ' | Linked account: ' + linked_user['user'] +'\n')

            config['keys'][str(linked_user['user'])] = { 'name': linked_user['user'], 'key': key_generator(24) }

            with open('config.json', 'w') as f:
                json.dump(config, f, indent=5)

            print(Fore.YELLOW + '[!] ' + Fore.RESET + 'Created new key for user ' + linked_user['user'] + ': ' + config['keys'][str(linked_user['user'])]['key'])

            print('\nPlease restart the panel.')

if result[0] == 'Start Server':
    clear()

    import server

    print(rainbowtext.text('DSShop Server ') + Fore.RESET + '- Start Server' + ' | Linked account: ' + linked_user['user'])

    print(Fore.YELLOW + '[?] ' + Fore.RESET + 'On what port should the server be listening?')
    
    r = input('[80] ')

    if r == ('' or ' ' or '80'):
        server.start(port=int(80))
    else:
        server.start(port=int(r))