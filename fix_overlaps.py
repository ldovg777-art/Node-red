#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление перекрытий нод в Node-RED flow
"""

import json
from collections import defaultdict

# Константы для размещения нод
NODE_WIDTH = 150
NODE_HEIGHT = 40
HORIZONTAL_SPACING = 200
VERTICAL_SPACING = 60
START_X = 100
START_Y = 100

def detect_overlaps(data):
    """Обнаруживает перекрывающиеся ноды"""
    nodes_with_pos = [n for n in data if 'x' in n and 'y' in n]
    overlaps = []
    
    for i, n1 in enumerate(nodes_with_pos):
        for j, n2 in enumerate(nodes_with_pos[i+1:], i+1):
            x1, y1 = n1.get('x', 0), n1.get('y', 0)
            x2, y2 = n2.get('x', 0), n2.get('y', 0)
            
            # Проверяем перекрытие (с учетом размеров нод)
            if abs(x1 - x2) < NODE_WIDTH and abs(y1 - y2) < NODE_HEIGHT:
                overlaps.append((n1, n2, abs(x1 - x2), abs(y1 - y2)))
    
    return overlaps

def reorganize_grid_layout(data):
    """Реорганизует ноды в grid layout без перекрытий"""
    tab_id = None
    for node in data:
        if node.get('type') == 'tab':
            tab_id = node.get('id')
            break
    
    nodes_with_pos = [n for n in data if 'x' in n and 'y' in n]
    
    # Группируем по типам для логической организации
    groups = {
        'entry': [],           # inject, http in
        'ui_buttons': [],      # ui_button
        'initialization': [],  # функции инициализации
        'file_ops': [],        # file in, file, json
        'control': [],         # switch, split
        'processing': [],     # function
        'ui_forms': [],        # ui_form
        'ui_display': [],      # ui_text, ui_chart, ui_template, ui_base
        'error': []           # catch
    }
    
    # Находим функцию инициализации
    init_node_ids = set()
    for node in nodes_with_pos:
        if node.get('type') == 'function' and 'Инициализация' in node.get('name', ''):
            init_node_ids.add(node.get('id'))
    
    # Группируем ноды
    for node in nodes_with_pos:
        node_id = node.get('id')
        ntype = node.get('type', '')
        name = node.get('name', '')
        
        if ntype == 'inject':
            groups['entry'].append(node)
        elif ntype == 'http in':
            groups['entry'].append(node)
        elif ntype == 'ui_button':
            groups['ui_buttons'].append(node)
        elif node_id in init_node_ids or 'Инициализация' in name:
            groups['initialization'].append(node)
        elif ntype in ['file in', 'file', 'json']:
            groups['file_ops'].append(node)
        elif ntype in ['switch', 'split']:
            groups['control'].append(node)
        elif ntype == 'ui_form':
            groups['ui_forms'].append(node)
        elif ntype.startswith('ui_'):
            groups['ui_display'].append(node)
        elif ntype == 'catch':
            groups['error'].append(node)
        elif ntype == 'function':
            groups['processing'].append(node)
        else:
            groups['processing'].append(node)
    
    # Размещаем группы в колонках
    current_x = START_X
    current_y = START_Y
    
    group_order = [
        'entry', 'ui_buttons', 'initialization', 'file_ops',
        'control', 'processing',
        'ui_forms', 'ui_display', 'error'
    ]
    
    for group_name in group_order:
        group_nodes = groups[group_name]
        if not group_nodes:
            continue
        
        # Сортируем по исходной Y позиции для сохранения порядка
        group_nodes.sort(key=lambda n: n.get('y', 0))
        
        # Размещаем в колонке
        y_pos = current_y
        for node in group_nodes:
            node['x'] = current_x
            node['y'] = y_pos
            y_pos += VERTICAL_SPACING
        
        # Переходим к следующей колонке
        current_x += HORIZONTAL_SPACING
        
        # Если колонка слишком длинная, начинаем новую строку
        if y_pos > START_Y + 1200:
            current_x = START_X
            current_y = y_pos + 100
    
    return data

def main():
    input_file = 'flows_controller_iteration_ver_2025-11-10_2151.json'
    
    print(f"Чтение файла {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Проверяем перекрытия до реорганизации
    overlaps_before = detect_overlaps(data)
    print(f"Перекрытий до реорганизации: {len(overlaps_before)}")
    
    # Реорганизуем
    print("Реорганизация нод...")
    data = reorganize_grid_layout(data)
    
    # Проверяем перекрытия после реорганизации
    overlaps_after = detect_overlaps(data)
    print(f"Перекрытий после реорганизации: {len(overlaps_after)}")
    
    if overlaps_after:
        print("\nПредупреждение: остались перекрытия:")
        for n1, n2, dx, dy in overlaps_after[:5]:
            print(f"  {n1.get('name', n1.get('id'))} ({n1.get('type')}) и "
                  f"{n2.get('name', n2.get('id'))} ({n2.get('type')})")
    
    # Сохраняем
    output_file = 'flows_controller_iteration_ver_2025-11-10_2151.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n✓ Результат сохранен в {output_file}")

if __name__ == '__main__':
    main()
