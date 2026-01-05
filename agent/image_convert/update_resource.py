import pathlib
import requests

URL_BASE = 'https://schaledb.brightsu.cn/' # Mirror of 'https://schaledb.com/'
USER_AGENT = 'BABoxExporter/1.0'
LANGUAGES = ('jp', 'en', 'kr', 'th', 'tw', 'cn', 'zh')


def update_equipment():
    print('[*] Updating equipment data...')
    resp = requests.get(URL_BASE + 'data/jp/equipment.min.json', headers={'User-Agent': USER_AGENT})
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
        image_resp = requests.get(f'{URL_BASE}images/equipment/full/{item.get("Icon")}.webp', headers={'User-Agent': USER_AGENT})
        if image_resp.status_code == 200:
            pathlib.Path('image/equipment').mkdir(parents=True, exist_ok=True)
            with open(f'image/equipment/{item.get("Icon")}.webp', 'wb') as img_file:
                img_file.write(image_resp.content)
        else:
            print(f'[-] Failed to download image for equipment ID {item.get("Icon")}: {image_resp.status_code}')


def update_student():
    print('[*] Updating student data...')
    resp = requests.get(URL_BASE + 'data/jp/students.min.json', headers={'User-Agent': USER_AGENT})
    if resp.status_code == 200:
        pathlib.Path('resource').mkdir(parents=True, exist_ok=True)
        with open('resource/students.jp.json', 'wb') as f:
            f.write(resp.content)
    else:
        raise Exception(f'Failed to download student data: {resp.status_code}')

    for item in resp.json().values():
        if not pathlib.Path('image/student').joinpath(f'{item.get("Id")}.webp').exists():
            print(f'[*] Downloading image for student ID {item.get("Id")}')
            image_resp = requests.get(f'{URL_BASE}images/student/icon/{item.get("Id")}.webp', headers={'User-Agent': USER_AGENT})
            if image_resp.status_code == 200:
                pathlib.Path('image/student').mkdir(parents=True, exist_ok=True)
                with open(f'image/student/{item.get("Id")}.webp', 'wb') as img_file:
                    img_file.write(image_resp.content)
            else:
                print(f'[-] Failed to download image for student ID {item.get("Id")}: {image_resp.status_code}')

        if item.get('Gear', {}) and not pathlib.Path(f'image/gear/{item.get("Id")}.webp').exists():
            print(f'[*] Downloading gear image for student ID {item.get("Id")}')
            gear_resp = requests.get(f'{URL_BASE}images/gear/full/{item.get("Id")}.webp', headers={'User-Agent': USER_AGENT})
            if gear_resp.status_code == 200:
                pathlib.Path('image/gear').mkdir(parents=True, exist_ok=True)
                with open(f'image/gear/{item.get("Id")}.webp', 'wb') as gear_file:
                    gear_file.write(gear_resp.content)
            else:
                print(f'[-] Failed to download gear image for student ID {item.get("Id")}: {gear_resp.status_code}')

    for lang in LANGUAGES:
        if lang == 'jp':
            continue
        print(f'[*] Updating student data for language: {lang}...')
        lang_resp = requests.get(URL_BASE + f'data/{lang}/students.min.json', headers={'User-Agent': USER_AGENT})
        if lang_resp.status_code == 200:
            with open(f'resource/students.{lang}.json', 'wb') as f:
                f.write(lang_resp.content)
        else:
            print(f'[-] Failed to download student data for language {lang}: {lang_resp.status_code}')


def main():
    update_equipment()
    update_student()

if __name__ == '__main__':
    main()
