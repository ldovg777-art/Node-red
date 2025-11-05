#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления управления видимостью графиков через стандартные узлы Node-RED
"""

import json
import uuid
import sys
import os
from datetime import datetime

def gen_id():
    """Генерирует уникальный ID для узла Node-RED"""
    return ''.join([f'{i:x}' for i in uuid.uuid4().bytes])

def main():
    # Получаем имена файлов из аргументов командной строки или используем значения по умолчанию
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'flows_AO6224_AI6717_ver_311020251659.json'
    
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    else:
        # Генерируем имя файла с текущей датой и временем
        now = datetime.now()
        timestamp = now.strftime('%d%m%Y%H%M')
        output_filename = f'flows_AO6224_AI6717_ver_{timestamp}_FINAL.json'
    
    print(f'Загрузка {filename}...')
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f'Загружено узлов: {len(data)}')
    
    # Найдем все графики
    charts = []
    for item in data:
        if item.get('type') == 'ui_chart':
            charts.append({
                'item': item,
                'id': item.get('id'),
                'name': item.get('name', 'График'),
                'group': item.get('group', ''),
                'order': item.get('order', 0),
                'z': item.get('z', ''),
                'x': item.get('x', 0),
                'y': item.get('y', 0)
            })
    
    print(f'Найдено графиков: {len(charts)}')
    
    # 1. Добавляем ui_template с CSS (стандартный узел node-red-dashboard)
    # Находим ui_base для размещения CSS template
    ui_base_idx = None
    for i, item in enumerate(data):
        if item.get('type') == 'ui_base':
            ui_base_idx = i
            break
    
    # Определяем z (вкладку) для CSS template
    css_tab_z = ""
    if charts:
        css_tab_z = charts[0]['z']
    else:
        # Если графиков нет, ищем первую вкладку
        for item in data:
            if item.get('type') == 'ui_tab':
                css_tab_z = item.get('id', '')
                break
    
    css_template_id = gen_id()
    css_template = {
        "id": css_template_id,
        "type": "ui_template",
        "z": css_tab_z,
        "group": "",
        "name": "CSS для скрытия графиков",
        "order": 1,
        "width": "0",
        "height": "0",
        "format": "<style>.chart-hidden { display: none !important; }</style>",
        "storeOutMessages": True,
        "fwdInMessages": True,
        "template": "<style>.chart-hidden { display: none !important; }</style>",
        "x": 100,
        "y": 100,
        "wires": [[]]
    }
    
    if ui_base_idx is not None:
        data.insert(ui_base_idx + 1, css_template)
        print('✓ CSS template добавлен')
    else:
        # Если ui_base не найден, добавляем в начало
        data.insert(0, css_template)
        print('✓ CSS template добавлен (ui_base не найден)')
    
    # 2. Для каждого графика добавляем стандартные узлы
    new_nodes = []
    chart_states = {}
    
    if not charts:
        print('⚠ Графики не найдены, пропускаем создание узлов управления')
    else:
        for idx, chart_info in enumerate(charts):
            chart_id = chart_info['id']
            chart_name = chart_info['name'] or f'График {idx+1}'
            group_id = chart_info['group']
            z_tab = chart_info['z']
            chart_order = chart_info['order']
            x_pos = chart_info['x']
            y_pos = chart_info['y']
            
            button_id = gen_id()
            function_id = gen_id()
            control_id = gen_id()
            state_var = f'chart_visible_{chart_id[:8]}'
            chart_states[chart_id] = state_var
            
            # Модифицируем график - добавляем className для скрытия по умолчанию
            chart_info['item']['className'] = "chart-hidden"
            
            # UI Button (стандартный узел node-red-dashboard)
            button_order = max(0, chart_order - 0.5)
            button = {
                "id": button_id,
                "type": "ui_button",
                "z": z_tab,
                "name": f"Показать/Скрыть: {chart_name}",
                "group": group_id,
                "order": button_order,
                "width": "3",
                "height": "1",
                "label": "Показать график",
                "tooltip": "",
                "color": "",
                "bgColor": "",
                "className": "",
                "icon": "",
                "payload": chart_id,
                "payloadType": "str",
                "topic": "toggle_chart",
                "x": x_pos - 200,
                "y": y_pos,
                "wires": [[function_id]]
            }
            
            # Function (стандартный узел core) - логика переключения
            function_code = f"""const g = global.get.bind(global);
const s = global.set.bind(global);

const chartId = msg.payload;
const stateVar = '{state_var}';
const buttonId = '{button_id}';

// Получаем текущее состояние
let isVisible = g(stateVar);
if (isVisible === undefined || isVisible === null) {{
    isVisible = false;
}}

// Переключаем
isVisible = !isVisible;
s(stateVar, isVisible);

// Формируем сообщение для ui_control (стандартный формат Node-RED Dashboard)
// Это сообщение управляет видимостью графика
const controlMsg = {{
    id: chartId,
    ui_control: {{
        className: isVisible ? "" : "chart-hidden"
    }}
}};

// Обновление текста кнопки через ui_control
const buttonUpdateMsg = {{
    id: buttonId,
    ui_control: {{
        label: isVisible ? "Скрыть график" : "Показать график"
    }}
}};

return [[controlMsg, buttonUpdateMsg]];"""
            
            function_node = {
                "id": function_id,
                "type": "function",
                "z": z_tab,
                "name": f"Переключить: {chart_name}",
                "func": function_code,
                "outputs": 1,
                "noerr": 0,
                "initialize": "",
                "finalize": "",
                "libs": [],
                "x": x_pos - 50,
                "y": y_pos,
                "wires": [[control_id]]
            }
            
            # UI Control (стандартный узел node-red-dashboard)
            control_node = {
                "id": control_id,
                "type": "ui_control",
                "z": z_tab,
                "name": f"Контроль: {chart_name}",
                "events": "all",
                "x": x_pos + 150,
                "y": y_pos,
                "wires": [[]]
            }
            
            # Узел change больше не нужен - обновление кнопки происходит через ui_control
            
            new_nodes.extend([button, function_node, control_node])
            print(f'  ✓ {chart_name}: добавлены кнопка, function, control')
    
    # 3. Инициализация при старте (стандартные узлы)
    init_function_id = gen_id()
    init_inject_id = gen_id()
    init_control_id = gen_id()
    
    init_code = f"""const g = global.get.bind(global);
const s = global.set.bind(global);

// Инициализируем все графики как скрытые
const chartStates = {json.dumps(list(chart_states.values()), ensure_ascii=False)};
chartStates.forEach(stateVar => {{
    s(stateVar, false);
}});

// Отправляем команды скрытия для всех графиков
const chartIds = {json.dumps(list(chart_states.keys()), ensure_ascii=False)};
const controlMsgs = chartIds.map(chartId => ({{
    id: chartId,
    ui_control: {{
        className: "chart-hidden"
    }}
}}));

return [controlMsgs];"""
    
    # Находим первую вкладку для размещения узлов инициализации
    init_tab_z = ""
    if charts:
        init_tab_z = charts[0]['z']
    else:
        # Если графиков нет, ищем первую вкладку
        for item in data:
            if item.get('type') == 'ui_tab':
                init_tab_z = item.get('id', '')
                break
    
    init_function = {
        "id": init_function_id,
        "type": "function",
        "z": init_tab_z,
        "name": "Инициализация: скрыть все графики",
        "func": init_code,
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 200,
        "y": 200,
        "wires": [[init_control_id]]
    }
    
    init_inject = {
        "id": init_inject_id,
        "type": "inject",
        "z": init_tab_z,
        "name": "При старте: скрыть графики",
        "props": [{"p": "payload"}],
        "repeat": "",
        "crontab": "",
        "once": True,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 100,
        "y": 200,
        "wires": [[init_function_id]]
    }
    
    init_control = {
        "id": init_control_id,
        "type": "ui_control",
        "z": init_tab_z,
        "name": "Контроль инициализации графиков",
        "events": "all",
        "x": 400,
        "y": 200,
        "wires": [[]]
    }
    
    # Добавляем узлы инициализации только если есть графики
    if charts:
        new_nodes.extend([init_function, init_inject, init_control])
    data.extend(new_nodes)
    
    print(f'\nДобавлено новых узлов: {len(new_nodes)}')
    print(f'Всего узлов: {len(data)}')
    
    # Сохраняем
    print(f'\nСохранение в {output_filename}...')
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print('✓ Готово!')
    print(f'\nИспользованы только стандартные узлы Node-RED:')
    print('  - ui_button (node-red-dashboard)')
    print('  - ui_control (node-red-dashboard)')
    print('  - ui_template (node-red-dashboard)')
    print('  - function (core)')
    print('  - inject (core)')
    print(f'\nИспользование:')
    print(f'  python3 {os.path.basename(__file__)} [input_file.json] [output_file.json]')

if __name__ == '__main__':
    main()
