from maa.agent.agent_server import AgentServer
from maa.custom_action import CustomAction
from maa.context import Context

import base64
import difflib
import json
import os
import re
from pathlib import Path

from utils import logger

# Configuration
BASE_DIR = Path(__file__).parent / "image_convert"
BOX_JSON_PATH = 'box.json'
EQUIPMENT_JSON_PATH = BASE_DIR / 'resource' / 'equipment.json'
IMAGE_DIR = BASE_DIR / 'image'
CSS_FILE = BASE_DIR / 'style.css'
SCRIPT_FILE = BASE_DIR / 'script.js'
OUTPUT_FILE = 'box.html'

LANGUAGES = ('jp', 'en', 'kr', 'th', 'tw', 'cn', 'zh')

HEART_SVG = '<svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>'
STAR_SVG = '<svg viewBox="0 0 576 512"><path fill="currentColor" d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"/></svg>'
LOCK_SVG = '<svg viewBox="0 0 448 512"><path fill="currentColor" d="M400 224h-24v-72C376 68.2 307.8 0 224 0S72 68.2 72 152v72H48c-26.5 0-48 21.5-48 48v192c0 26.5 21.5 48 48 48h352c26.5 0 48-21.5 48-48V272c0-26.5-21.5-48-48-48zm-104 0H152v-72c0-39.7 32.3-72 72-72s72 32.3 72 72v72z"/></svg>'

TYPE_COLORS = {
    "Explosion": "#9B2221",
    "LightArmor": "#9B2221",
    "Pierce": "#A97031",
    "HeavyArmor": "#A97031",
    "Mystic": "#376D98",
    "Unarmed": "#376D98",
    "Sonic": "#8A389F",
    "ElasticArmor": "#8A389F",
    "Front": "#D2232A",
    "Back": "#0078D7",
}

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_gear_released(gear_data, lang):
    if not gear_data or 'Released' not in gear_data:
        return False

    released = gear_data['Released']
    if not released:
        return False

    index = 1 # Default for others (en, kr, th, tw)
    if lang == 'jp':
        index = 0
    elif lang in ('zh', 'cn'):
        index = 2

    if index < len(released):
        return released[index]
    return False


def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error reading image {path}: {e}")
        return ""


def normalize_name(name):
    return name.replace('（', '(').replace('）', ')').strip()


def work():
    box_data = load_json(BOX_JSON_PATH)
    equipment_data = load_json(EQUIPMENT_JSON_PATH)

    # Create mappings
    # Name -> Student Data
    language_maps = {}
    language_maps_norm = {}

    for lang in LANGUAGES:
        file_path = BASE_DIR / 'resource' / f'students.{lang}.json'
        if file_path.exists():
            try:
                lang_data = load_json(file_path)
                current_map = {}
                current_map_norm = {}
                for _, sdata in lang_data.items():
                    if 'Name' in sdata:
                        current_map[sdata['Name']] = sdata
                        current_map_norm[normalize_name(sdata['Name'])] = sdata
                language_maps[lang] = current_map
                language_maps_norm[lang] = current_map_norm
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

    # Determine the best language
    # We select the language that has the most matches (exact or fuzzy) with the box.json names.
    # This ensures that we use the data (including Gear status) from the language that matches the user's input best.
    best_lang = None
    max_match_count = -1

    logger.info("确定当前客户端语言...")

    for lang, s_map_norm in language_maps_norm.items():
        match_count = 0
        for name, data in box_data.items():
            norm_name = normalize_name(name)
            matched_sdata = None
            if norm_name in s_map_norm:
                matched_sdata = s_map_norm[norm_name]
            else:
                # Fuzzy match check
                matches = difflib.get_close_matches(norm_name, s_map_norm.keys(), n=1, cutoff=0.6)
                if matches:
                    matched_sdata = s_map_norm[matches[0]]

            if matched_sdata:
                match_count += 1

        logger.info(f"语言 '{lang}': {match_count} 个匹配")

        if match_count > max_match_count:
            max_match_count = match_count
            best_lang = lang

    logger.info(f"使用语言: '{best_lang}'，匹配数: {max_match_count}")
    student_name_map = language_maps[best_lang]
    student_name_map_norm = language_maps_norm[best_lang]

    # (Category, Tier) -> Equipment Icon
    equipment_map = {}
    for _, edata in equipment_data.items():
        if 'Category' in edata and 'Tier' in edata and 'Icon' in edata and not edata['Icon'].endswith('_piece'):
            key = (edata['Category'], edata['Tier'])
            equipment_map[key] = edata['Icon']

    # Prepare to collect body content and icons
    body_content = ""
    equipment_icons_cache = {} # icon_name -> base64_str
    ui_icons_cache = {} # icon_name -> base64_str

    student_id_map = {v['Id']: v for v in student_name_map.values()}

    for name, data in box_data.items():
        display_name = name
        norm_name = normalize_name(name)
        if norm_name not in student_name_map_norm:
            found_data = None
            found_lang = None

            # 1. Exact match in other languages
            for lang, s_map_norm in language_maps_norm.items():
                if norm_name in s_map_norm:
                    found_data = s_map_norm[norm_name]
                    found_lang = lang
                    break

            # 2. Fuzzy match in all languages
            if not found_data:
                for lang, s_map_norm in language_maps_norm.items():
                    matches = difflib.get_close_matches(norm_name, s_map_norm.keys(), n=1, cutoff=0.6)
                    if matches:
                        found_data = s_map_norm[matches[0]]
                        found_lang = lang
                        break

            if found_data:
                sid = found_data['Id']
                if sid in student_id_map:
                    s_static_data = student_id_map[sid]
                    display_name = s_static_data['Name']
                    logger.info(f"Student '{name}' found via {found_lang} ID {sid}, using local name '{display_name}'")
                else:
                    s_static_data = found_data
                    display_name = found_data['Name']
                    logger.info(f"Student '{name}' found via {found_lang} ID {sid} (local data missing)")
            else:
                logger.warn(f"Student {name} not found in any resource/students.*.json")
                continue
        else:
            s_static_data = student_name_map_norm[norm_name]

        student_id = s_static_data['Id']
        position = s_static_data.get('Position', '')
        tactic_role = s_static_data.get('TacticRole', '')
        bullet_type = s_static_data.get('BulletType', '')
        armor_type = s_static_data.get('ArmorType', '')

        # Ensure icons are in cache
        for ui_icon in [f"Role_{tactic_role}", "Type_Attack", "Type_Defense"]:
            if ui_icon not in ui_icons_cache:
                icon_path = IMAGE_DIR / "ui" / f"{ui_icon}.png"
                if icon_path.exists():
                    with open(icon_path, "rb") as img_f:
                        ui_icons_cache[ui_icon] = base64.b64encode(img_f.read()).decode('utf-8')
                else:
                    logger.warn(f"UI icon not found: {icon_path}")
                    ui_icons_cache[ui_icon] = ""

        safe_role = f"Role_{tactic_role}".replace(' ', '_').replace('.', '_')
        safe_attack = "Type_Attack".replace(' ', '_').replace('.', '_')
        safe_defense = "Type_Defense".replace(' ', '_').replace('.', '_')

        squares_html = f"""
        <div class="info-squares">
            <div class="info-square" style="background-color: {TYPE_COLORS.get(position, '#F5A623')};">
                <div class="square-icon ui-icon-{safe_role}"></div>
            </div>
            <div class="info-square" style="background-color: {TYPE_COLORS.get(bullet_type, '#000000')};">
                <div class="square-icon ui-icon-{safe_attack}"></div>
            </div>
            <div class="info-square" style="background-color: {TYPE_COLORS.get(armor_type, '#000000')};">
                <div class="square-icon ui-icon-{safe_defense}"></div>
            </div>
        </div>
        """
        # Student Icon
        icon_path = IMAGE_DIR / "student" / f"{student_id}.webp"
        with open(icon_path, "rb") as img_f:
            icon_base64 = base64.b64encode(img_f.read()).decode('utf-8')

        # Stars
        if data['tier'] <= 4:
            stars_html = ""
            for _ in range(data['tier']):
                stars_html += f'<span class="yellow-star-icon">{STAR_SVG}</span>'
        else:
            weapon_tier = data.get('weapon', {}).get('tier', 0)
            weapon_level = data.get('weapon', {}).get('level', 0)
            stars_html = f"""
            <div class="icon-wrapper">
                <span class="icon-shape blue-star-shape">{STAR_SVG}</span>
                <span class="icon-text">{weapon_tier}</span>
            </div>
            <span class="level-info">Lv.{weapon_level}</span>
            """

        # Skills
        skills = data['skill']
        skill_order = ['ex', 'ns', 'ps', 'ss']
        skill_labels = ['EX', 'NS', 'PS', 'SS'] # Or all EX as per image? Let's use correct labels.

        skills_html = ""
        for i, key in enumerate(skill_order):
            val = skills.get(key, 1)
            label = skill_labels[i]
            skills_html += f"""
            <div class="skill-box">
                <div class="skill-label">{label}</div>
                <div class="skill-value">{val}</div>
            </div>
            """

        # Equipment
        equip_html = ""
        equip_slots = s_static_data.get('Equipment', [])

        # Standard 3 slots
        for i in range(3):
            slot_idx = str(i + 1)
            if slot_idx in data['equipment']:
                eq_data = data['equipment'][slot_idx]
                eq_tier = eq_data['tier']
                eq_level = eq_data['level']

                # Determine if locked (Tier 0)
                is_locked = (eq_tier == 0)
                display_tier = 1 if is_locked else eq_tier

                if i < len(equip_slots):
                    category = equip_slots[i]
                    # Find icon
                    icon_name = equipment_map.get((category, display_tier), "")

                    # Fallback to Tier 4 if specific tier not found (since we only have T4 icons in example)
                    if not icon_name:
                        icon_name = equipment_map.get((category, 4), "")

                    if icon_name:
                        if icon_name not in equipment_icons_cache:
                            eq_icon_path_obj = IMAGE_DIR / 'equipment' / f'{icon_name}.webp'
                            if eq_icon_path_obj.exists():
                                with open(eq_icon_path_obj, "rb") as img_f:
                                    equipment_icons_cache[icon_name] = base64.b64encode(img_f.read()).decode('utf-8')
                            else:
                                equipment_icons_cache[icon_name] = ""

                        safe_icon_name = icon_name.replace(' ', '_').replace('.', '_')

                        lock_html = ""
                        equip_text_html = f'<div class="equip-text">T{eq_tier}&nbsp;&nbsp;Lv.{eq_level}</div>'
                        icon_extra_class = ""

                        if is_locked:
                            lock_html = f'<div class="locked-overlay"><div class="lock-icon">{LOCK_SVG}</div></div>'
                            equip_text_html = ""
                            icon_extra_class = " no-text"

                        equip_html += f"""
                        <div class="equip-box">
                            {lock_html}
                            <div class="equip-icon eq-icon-{safe_icon_name}{icon_extra_class}"></div>
                            {equip_text_html}
                        </div>
                        """
                    else:
                        equip_html += """<div class="equip-box empty-slot">?</div>"""
                else:
                     equip_html += """<div class="equip-box empty-slot">/</div>"""
            else:
                equip_html += """<div class="equip-box empty-slot">/</div>"""

        # Gear (Unique Item)
        gear_data = data['equipment'].get('gear', {})
        gear_tier = gear_data.get('tier', 0)

        # Check if the student has Gear in the SELECTED language data.
        # If the language data says no Gear, we show empty slot (/) even if box.json has gear info.
        # This ensures the display corresponds to the selected language/server status.
        has_gear = check_gear_released(s_static_data.get('Gear'), best_lang)

        if has_gear:
            gear_icon_path_obj = IMAGE_DIR / 'gear' / f'{student_id}.webp'
            with open(gear_icon_path_obj, "rb") as img_f:
                gear_icon_base64 = base64.b64encode(img_f.read()).decode('utf-8')

            if gear_tier > 0:
                equip_html += f"""
                <div class="equip-box">
                    <img src="data:image/webp;base64,{gear_icon_base64}" class="equip-icon">
                    <div class="equip-text">T{gear_tier}</div>
                </div>
                """
            else:
                # Tier 0 but has gear -> Locked
                equip_html += f"""
                <div class="equip-box">
                    <div class="locked-overlay"><div class="lock-icon">{LOCK_SVG}</div></div>
                    <img src="data:image/webp;base64,{gear_icon_base64}" class="equip-icon no-text">
                </div>
                """
        else:
            equip_html += """<div class="equip-box empty-slot">/</div>"""

        body_content += f"""
    <div class="card">
        <div class="student-info">
            <img src="data:image/webp;base64,{icon_base64}" class="student-icon">
            <div class="student-name">{display_name}</div>
        </div>
        <div class="stats">
            {squares_html}
            <div class="level-bond">
                <div class="icon-wrapper">
                    <span class="icon-shape bond-heart-shape">{HEART_SVG}</span>
                    <span class="icon-text">{data['relationship']}</span>
                </div>
                <span class="level-info">Lv.{data['level']}</span>
            </div>
            <div class="stars">{stars_html}</div>
        </div>
        <div class="skills">
            {skills_html}
        </div>
        <div class="equipments">
            {equip_html}
        </div>
    </div>
        """

    # Generate CSS for equipment icons
    generated_css = ""
    for icon_name, b64_data in equipment_icons_cache.items():
        if b64_data:
            safe_icon_name = icon_name.replace(' ', '_').replace('.', '_')
            generated_css += f""".eq-icon-{safe_icon_name} {{ background-image: url('data:image/webp;base64,{b64_data}'); }}\n"""

    for icon_name, b64_data in ui_icons_cache.items():
        if b64_data:
            safe_icon_name = icon_name.replace(' ', '_').replace('.', '_')
            generated_css += f""".ui-icon-{safe_icon_name} {{ background-image: url('data:image/png;base64,{b64_data}'); }}\n"""

    with open(CSS_FILE, "r", encoding="utf-8") as f:
        style_css = f.read()
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        script_js = f.read()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <style>
        {style_css}
        {generated_css}
        </style>
        <script src="https://s4.zstatic.net/ajax/libs/html-to-image/1.11.13/html-to-image.min.js" async></script>
        <title>Box</title>
    </head>
    <body>
    <div id="main">
        {body_content}
    </div>
    <button class="export-btn" onclick="exportImage()" disabled>📤 导出图片</button>
    <script>
    {script_js}
    </script>
    </body>
    </html>
    """
    compressed_html = re.sub(r'\s{2,}', ' ', re.sub(r'>\s+<', '><', html_content))
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(compressed_html)

    os.startfile(OUTPUT_FILE)

if __name__ == "__main__":
    work()


@AgentServer.custom_action("export_to_html")
class ExportToHTML(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:
        work()
        logger.info("已导出至 box.html")
        return True