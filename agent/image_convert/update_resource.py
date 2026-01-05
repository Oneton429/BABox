import pathlib
import requests
import os

URL_BASE = 'https://schaledb.brightsu.cn/' # Mirror of 'https://schaledb.com/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0' # 'BABoxExporter/1.0'
LANGUAGES = ('jp', 'en', 'kr', 'th', 'tw', 'cn', 'zh')

HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
}

def update_equipment():
    print('[*] Updating equipment data...')
    resp = requests.get(URL_BASE + 'data/jp/equipment.min.json', headers=HEADERS)
    if resp.status_code == 200:
        pathlib.Path('resource').mkdir(parents=True, exist_ok=True)
        with open('resource/equipment.json', 'wb') as f:
            f.write(resp.content)
    else:
        raise Exception(f'Failed to download equipment data: {resp.status_code}')

    for item in resp.json().values():
        if item.get('Category', 'Exp') == 'Exp' or item.get('Icon', '_piece').endswith('_piece'):
            continue
        if pathlib.Path('image/equipment').joinpath(f'{item.get("Icon")}.webp').exists():
            continue
        print(f'[*] Downloading image for equipment ID {item.get("Icon")}')
        image_resp = requests.get(f'{URL_BASE}images/equipment/full/{item.get("Icon")}.webp', headers=HEADERS)
        if image_resp.status_code == 200:
            pathlib.Path('image/equipment').mkdir(parents=True, exist_ok=True)
            with open(f'image/equipment/{item.get("Icon")}.webp', 'wb') as img_file:
                img_file.write(image_resp.content)
        else:
            print(f'[-] Failed to download image for equipment ID {item.get("Icon")}: {image_resp.status_code}')


def update_student():
    print('[*] Updating student data...')
    resp = requests.get(URL_BASE + 'data/jp/students.min.json', headers=HEADERS)
    if resp.status_code == 200:
        pathlib.Path('resource').mkdir(parents=True, exist_ok=True)
        with open('resource/students.jp.json', 'wb') as f:
            f.write(resp.content)
    else:
        raise Exception(f'Failed to download student data: {resp.status_code}')

    for item in resp.json().values():
        if not pathlib.Path('image/student').joinpath(f'{item.get("Id")}.webp').exists():
            print(f'[*] Downloading image for student ID {item.get("Id")}')
            image_resp = requests.get(f'{URL_BASE}images/student/icon/{item.get("Id")}.webp', headers=HEADERS)
            if image_resp.status_code == 200:
                pathlib.Path('image/student').mkdir(parents=True, exist_ok=True)
                with open(f'image/student/{item.get("Id")}.webp', 'wb') as img_file:
                    img_file.write(image_resp.content)
            else:
                print(f'[-] Failed to download image for student ID {item.get("Id")}: {image_resp.status_code}')

        if item.get('Gear', {}) and not pathlib.Path(f'image/gear/{item.get("Id")}.webp').exists():
            print(f'[*] Downloading gear image for student ID {item.get("Id")}')
            gear_resp = requests.get(f'{URL_BASE}images/gear/full/{item.get("Id")}.webp', headers=HEADERS)
            if gear_resp.status_code == 200:
                pathlib.Path('image/gear').mkdir(parents=True, exist_ok=True)
                with open(f'image/gear/{item.get("Id")}.webp', 'wb') as gear_file:
                    gear_file.write(gear_resp.content)
            else:
                print(f'[-] Failed to download gear image for student ID {item.get("Id")}: {gear_resp.status_code}')

        # if not pathlib.Path(f'image/ui/Role_{item.get("TacticRole")}.png').exists():
        #     pathlib.Path('image/ui').mkdir(parents=True, exist_ok=True)
        #     print(f'[*] Downloading role icon for {item.get("TacticRole")}')
        #     os.system(f'curl -o image/ui/Role_{item.get("TacticRole")}.png {URL_BASE}images/ui/Role_{item.get("TacticRole")}.png')

    for lang in LANGUAGES:
        if lang == 'jp':
            continue
        print(f'[*] Updating student data for language: {lang}...')
        lang_resp = requests.get(URL_BASE + f'data/{lang}/students.min.json', headers=HEADERS)
        if lang_resp.status_code == 200:
            with open(f'resource/students.{lang}.json', 'wb') as f:
                f.write(lang_resp.content)
        else:
            print(f'[-] Failed to download student data for language {lang}: {lang_resp.status_code}')


def update_icons():
    os.system(f'curl -o image/ui/Type_Defense.png {URL_BASE}images/ui/Type_Defense.png')
    os.system(f'curl -o image/ui/Type_Attack.png {URL_BASE}images/ui/Type_Attack.png')

def main():
    update_equipment()
    update_student()
    # update_icons()


if __name__ == '__main__':
    main()
