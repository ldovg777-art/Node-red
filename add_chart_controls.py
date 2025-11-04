#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для добавления управления видимостью графиков через CSS
"""

import json
import uuid
import sys
import os
from datetime import datetime

def gen_id():
    """Генерирует уникальный ID для узла Node-RED"""
    return ''.join([f'{i:x}' for i in uuid.uuid4().bytes])

def add_chart_controls(data):
    """Добавляет кнопки управления и логику для всех графиков"""
    
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
    
    # Проверка на наличие графиков
    if not charts:
        print('Предупреждение: графики не найдены. Выход без изменений.')
        return [], {}
    
    # Создаем CSS template узел (один на весь проект)
    css_template_id = gen_id()
    css_template = {
        "id": css_template_id,
        "type": "ui_template",
        "z": charts[0]['z'] if charts else "",
        "group": "",
        "name": "CSS для скрытия графиков",
        "order": 0,
        "width": "0",
        "height": "0",
        "format": "<style>\n.chart-hidden { display: none !important; }\n</style>",
        "storeOutMessages": True,
        "fwdInMessages": True,
        "template": "<style>\n.chart-hidden { display: none !important; }\n</style>",
        "x": 100,
        "y": 100,
        "wires": [[]]
    }
    
    new_nodes = []
    chart_state_vars = {}  # Для хранения состояний графиков
    
    # Для каждого графика создаем узлы управления
    for idx, chart_info in enumerate(charts):
        chart_id = chart_info['id']
        chart_name = chart_info['name'] or f'График {idx+1}'
        group_id = chart_info['group']
        z_tab = chart_info['z']
        chart_order = chart_info['order']
        x_pos = chart_info['x']
        y_pos = chart_info['y']
        
        # Генерируем ID для новых узлов
        button_id = gen_id()
        function_id = gen_id()
        control_id = gen_id()
        state_var_name = f'chart_visible_{chart_id[:8]}'
        chart_state_vars[chart_id] = state_var_name
        
        # 1. UI Button - кнопка переключения
        button_order = chart_order - 0.5 if chart_order > 0 else 0
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
        
        # 2. Function - логика переключения видимости
        function_code = f"""const g = global.get.bind(global);
const s = global.set.bind(global);

const chartId = msg.payload; // ID графика
const stateVar = '{state_var_name}';
const buttonId = '{button_id}';

// Получаем текущее состояние (по умолчанию false - скрыт)
let isVisible = g(stateVar);
if (isVisible === undefined || isVisible === null) {{
    isVisible = false; // По умолчанию скрыт
}}

// Переключаем состояние
isVisible = !isVisible;
s(stateVar, isVisible);

// Формируем сообщение для ui_control для изменения className
const controlMsg = {{
    id: chartId,
    ui_control: {{
        className: isVisible ? "" : "chart-hidden"
    }}
}};

// Обновляем текст кнопки через ui_control
const buttonMsg = {{
    id: buttonId,
    ui_control: {{
        label: isVisible ? "Скрыть график" : "Показать график"
    }}
}};

return [[controlMsg, buttonMsg]];"""
        
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
        
        # 3. UI Control - управление видимостью графика
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
        
        # 4. Модифицируем график - добавляем className для скрытия
        chart_info['item']['className'] = "chart-hidden"
        
        # Добавляем узлы в список новых узлов
        new_nodes.extend([button, function_node, control_node])
        
        print(f'  ✓ {chart_name}: добавлены кнопка, function, control')
    
    # Добавляем CSS template
    new_nodes.append(css_template)
    
    # Создаем инициализационный узел для скрытия всех графиков при старте
    init_function_id = gen_id()
    init_inject_id = gen_id()
    
    init_code = """const g = global.get.bind(global);
const s = global.set.bind(global);

// Список всех переменных состояний графиков
const chartStates = """ + json.dumps(list(chart_state_vars.values()), ensure_ascii=False) + """;

// Инициализируем все графики как скрытые
chartStates.forEach(stateVar => {
    s(stateVar, false);
});

// Отправляем команды скрытия для всех графиков через ui_control
const chartIds = """ + json.dumps(list(chart_state_vars.keys()), ensure_ascii=False) + """;

const controlMsgs = chartIds.map(chartId => ({
    id: chartId,
    ui_control: {
        className: "chart-hidden"
    }
}));

return [controlMsgs];"""
    
    init_function = {
        "id": init_function_id,
        "type": "function",
        "z": charts[0]['z'] if charts else "",
        "name": "Инициализация: скрыть все графики",
        "func": init_code,
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 200,
        "y": 200,
        "wires": [[]]
    }
    
    init_inject = {
        "id": init_inject_id,
        "type": "inject",
        "z": charts[0]['z'] if charts else "",
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
    
    new_nodes.extend([init_function, init_inject])
    
    # Добавляем один ui_control узел для инициализации (один узел может обработать массив сообщений)
    control_node_init_id = gen_id()
    control_node_init = {
        "id": control_node_init_id,
        "type": "ui_control",
        "z": charts[0]['z'] if charts else "",
        "name": "Контроль инициализации графиков",
        "events": "all",
        "x": 400,
        "y": 200,
        "wires": [[]]
    }
    new_nodes.append(control_node_init)
    
    # Подключаем init_function к ui_control узлу
    init_function['wires'] = [[control_node_init_id]]
    
    return new_nodes, chart_state_vars

# Основная функция
def main():
    # Получаем имя файла из аргументов командной строки или используем значение по умолчанию
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'flows_AO6224_AI6717_ver_311020251659.json'
    
    backup_filename = filename.replace('.json', '_backup.json')
    
    # Проверка существования файла
    if not os.path.exists(filename):
        print(f'Ошибка: файл {filename} не найден')
        sys.exit(1)
    
    print(f'Загрузка {filename}...')
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f'Ошибка: невалидный JSON в файле {filename}: {e}')
        sys.exit(1)
    except IOError as e:
        print(f'Ошибка при чтении файла {filename}: {e}')
        sys.exit(1)
    
    # Валидация структуры данных
    if not isinstance(data, list):
        print(f'Ошибка: ожидается список узлов, получен {type(data).__name__}')
        sys.exit(1)
    
    print(f'Загружено узлов: {len(data)}')
    
    # Создаем резервную копию
    print(f'Создание резервной копии: {backup_filename}...')
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f'Ошибка при создании резервной копии {backup_filename}: {e}')
        sys.exit(1)
    
    # Добавляем узлы управления
    print('\nДобавление узлов управления графиками...')
    new_nodes, chart_states = add_chart_controls(data)
    
    # Добавляем новые узлы в данные
    data.extend(new_nodes)
    
    print(f'\nДобавлено новых узлов: {len(new_nodes)}')
    print(f'Всего узлов в файле: {len(data)}')
    
    # Сохраняем модифицированный файл
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    else:
        # Генерируем имя файла с текущей датой и временем
        now = datetime.now()
        timestamp = now.strftime('%d%m%Y%H%M')
        output_filename = f'flows_AO6224_AI6717_ver_{timestamp}_with_chart_controls.json'
    
    print(f'\nСохранение в {output_filename}...')
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f'Ошибка при записи файла {output_filename}: {e}')
        sys.exit(1)
    
    print('\n✓ Готово!')
    print(f'\nФайлы:')
    print(f'  - Оригинал: {filename}')
    print(f'  - Резервная копия: {backup_filename}')
    print(f'  - С изменениями: {output_filename}')
    print(f'\nИспользование:')
    print(f'  python3 {os.path.basename(__file__)} [input_file.json] [output_file.json]')

if __name__ == '__main__':
    main()
