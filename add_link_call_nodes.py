#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Добавление link call нод для организации связей в Node-RED flow.
Создает link in/out структуры для веток switch нод.
"""

import json
import uuid

def generate_id():
    """Генерирует новый ID для ноды"""
    return ''.join([format(x, 'x') for x in uuid.uuid4().bytes[:8]])

def find_end_nodes(data, start_node_ids, nodes_dict):
    """Находит конечные ноды в цепочке (ноды без исходящих связей в этой группе)"""
    visited = set()
    end_nodes = []
    
    def traverse(node_id):
        if node_id in visited or node_id not in nodes_dict:
            return
        visited.add(node_id)
        
        node = nodes_dict[node_id]
        wires = node.get('wires', [])
        
        # Проверяем, есть ли исходящие связи к другим нодам в группе
        has_outgoing_in_group = False
        for wire_list in wires:
            for target_id in wire_list:
                if target_id in start_node_ids:
                    has_outgoing_in_group = True
                    traverse(target_id)
        
        # Если нет исходящих связей в группе, это конечная нода
        if not has_outgoing_in_group:
            end_nodes.append(node_id)
    
    for start_id in start_node_ids:
        traverse(start_id)
    
    return end_nodes if end_nodes else start_node_ids

def create_link_flow_for_branch(data, switch_node, branch_idx, target_node_ids):
    """Создает link in/out структуру для одной ветки switch"""
    tab_id = None
    for node in data:
        if node.get('type') == 'tab':
            tab_id = node.get('id')
            break
    
    if not tab_id or not target_node_ids:
        return None, None
    
    nodes_dict = {n.get('id'): n for n in data if 'x' in n and 'y' in n}
    
    # Создаем link in ноду
    link_in_id = generate_id()
    switch_name = switch_node.get('name', 'switch')
    link_in_name = f"{switch_name}_step_{branch_idx + 1}"
    
    # Позиционируем link in перед целевыми нодами
    first_target = nodes_dict.get(target_node_ids[0])
    link_in_x = (first_target.get('x', 0) - 200) if first_target else switch_node.get('x', 0) + 200
    link_in_y = first_target.get('y', 0) if first_target else switch_node.get('y', 0) + (branch_idx * 80)
    
    link_in_node = {
        "id": link_in_id,
        "type": "link in",
        "z": tab_id,
        "name": link_in_name,
        "links": [],
        "x": link_in_x,
        "y": link_in_y
    }
    
    # Находим конечные ноды в этой ветке
    end_node_ids = find_end_nodes(data, target_node_ids, nodes_dict)
    
    # Создаем link out ноду
    link_out_id = generate_id()
    
    # Позиционируем link out после конечных нод
    if end_node_ids:
        last_target = nodes_dict.get(end_node_ids[0])
        link_out_x = (last_target.get('x', 0) + 200) if last_target else link_in_x + 400
        link_out_y = last_target.get('y', 0) if last_target else link_in_y
    else:
        link_out_x = link_in_x + 400
        link_out_y = link_in_y
    
    link_out_node = {
        "id": link_out_id,
        "type": "link out",
        "z": tab_id,
        "name": "return",
        "mode": "return",
        "links": [link_in_id],
        "x": link_out_x,
        "y": link_out_y,
        "wires": []
    }
    
    # Подключаем link in к первой целевой ноде
    link_in_node['wires'] = [[target_node_ids[0]]]
    
    # Подключаем конечные ноды к link out
    for end_id in end_node_ids:
        end_node = nodes_dict.get(end_id)
        if end_node:
            if 'wires' not in end_node:
                end_node['wires'] = []
            if not end_node['wires']:
                end_node['wires'] = [[]]
            # Добавляем link out к существующим связям первой выходной линии
            if link_out_id not in end_node['wires'][0]:
                end_node['wires'][0].append(link_out_id)
    
    data.append(link_in_node)
    data.append(link_out_node)
    
    return link_in_id, link_out_id

def add_link_calls_for_switch(data, switch_node):
    """Добавляет link call структуру для switch ноды"""
    tab_id = None
    for node in data:
        if node.get('type') == 'tab':
            tab_id = node.get('id')
            break
    
    if not tab_id:
        return data
    
    switch_id = switch_node.get('id')
    switch_name = switch_node.get('name', '')
    wires = switch_node.get('wires', [])
    
    link_call_ids = []
    
    # Создаем link структуру для каждой ветки
    for branch_idx, target_ids in enumerate(wires):
        if not target_ids:
            continue
        
        link_in_id, link_out_id = create_link_flow_for_branch(
            data, switch_node, branch_idx, target_ids
        )
        
        if link_in_id:
            link_call_ids.append(link_in_id)
    
    # Создаем link call ноды для каждой ветки
    link_call_nodes = []
    for i, link_in_id in enumerate(link_call_ids):
        link_call_id = generate_id()
        
        link_call_node = {
            "id": link_call_id,
            "type": "link call",
            "z": tab_id,
            "name": f"Call {switch_name} step {i+1}",
            "links": [link_in_id],
            "x": switch_node.get('x', 0) + 150,
            "y": switch_node.get('y', 0) + (i * 60),
            "wires": []
        }
        
        link_call_nodes.append(link_call_node)
        data.append(link_call_node)
        link_call_ids[i] = link_call_id  # Сохраняем ID link call ноды
    
    # Обновляем switch ноду - заменяем прямые связи на link call
    new_wires = []
    for link_call_id in link_call_ids:
        new_wires.append([link_call_id])
    
    switch_node['wires'] = new_wires
    
    return data

def main():
    input_file = 'flows_controller_iteration_ver_2025-11-10_2151.json'
    
    print(f"Чтение файла {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Находим switch ноды
    switch_nodes = [n for n in data if n.get('type') == 'switch' and 'x' in n]
    
    print(f"Найдено {len(switch_nodes)} switch нод\n")
    
    for switch in switch_nodes:
        switch_name = switch.get('name', '')
        branch_count = len([w for w in switch.get('wires', []) if w])
        print(f"Обработка switch: {switch_name} ({branch_count} веток)")
        
        # Добавляем link call структуру
        data = add_link_calls_for_switch(data, switch)
        print(f"  ✓ Создана link call структура")
    
    # Сохраняем
    output_file = 'flows_controller_iteration_ver_2025-11-10_2151.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n✓ Результат сохранен в {output_file}")
    print("\nСтруктура link call создана:")
    print("  - Switch ноды теперь используют link call для вызова веток")
    print("  - Каждая ветка обернута в link in -> [ноды] -> link out")
    print("  - Проверьте работу flow в Node-RED редакторе")

if __name__ == '__main__':
    main()
