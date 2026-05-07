from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import random
import uuid
import os
from PIL import Image, ImageDraw, ImageFont
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'simple-key'

# Простой класс для чтения Excel
class ExcelReader:
    def __init__(self):
        self.file_path = 'data/dungeon_data.xlsx'
        if os.path.exists(self.file_path):
            try:
                self.df = pd.read_excel(self.file_path, sheet_name=0)
                print(f"✅ Загружено {len(self.df)} записей из Excel")
                print(f"📊 Колонки: {list(self.df.columns)}")
            except Exception as e:
                print(f"❌ Ошибка чтения Excel: {e}")
                self.df = pd.DataFrame()
        else:
            print(f"❌ Excel файл не найден: {self.file_path}")
            self.df = pd.DataFrame()
    
    def get_random_room(self, room_type=None, size=None):
        if len(self.df) == 0:
            return {
                'description': f'Обычная комната',
                'type': room_type or 'common',
                'size': size or 'medium'
            }
        
        filtered = self.df
        type_col = None
        for col in self.df.columns:
            if 'type' in col.lower() or 'room' in col.lower():
                type_col = col
                break
        
        if type_col and room_type:
            filtered = filtered[filtered[type_col].astype(str).str.lower() == room_type.lower()]
        
        if len(filtered) == 0:
            filtered = self.df
        
        room = filtered.sample(1).iloc[0].to_dict()
        
        desc_col = None
        for col in self.df.columns:
            if 'desc' in col.lower():
                desc_col = col
                break
        
        return {
            'description': room.get(desc_col, room.get('description', f'Таинственная комната')),
            'type': room_type or 'common',
            'size': size or 'medium'
        }

# Генератор подземелий с поддержкой связей
class DungeonGenerator:
    def __init__(self, excel_reader):
        self.excel = excel_reader
        self.rooms = []
        self.connections = []
    
    def generate(self, size='medium', dungeon_type='standard'):
        if size == 'small':
            num_rooms = random.randint(5, 7)
            connection_density = 0.3
        elif size == 'medium':
            num_rooms = random.randint(8, 12)
            connection_density = 0.4
        else:
            num_rooms = random.randint(15, 20)
            connection_density = 0.5
        
        self.rooms = []
        
        for i in range(1, num_rooms + 1):
            if i == 1:
                room_type = 'entrance'
            elif i == num_rooms:
                room_type = 'boss'
            else:
                types = ['battle', 'trap', 'treasure', 'puzzle', 'rest']
                weights = [0.35, 0.15, 0.15, 0.15, 0.20]
                room_type = random.choices(types, weights=weights)[0]
            
            if i < num_rooms / 3:
                size_room = random.choices(['small', 'medium', 'large'], weights=[0.6, 0.3, 0.1])[0]
            elif i < 2 * num_rooms / 3:
                size_room = random.choices(['small', 'medium', 'large'], weights=[0.3, 0.5, 0.2])[0]
            else:
                size_room = random.choices(['small', 'medium', 'large'], weights=[0.1, 0.4, 0.5])[0]
            
            room_data = self.excel.get_random_room(room_type, size_room)
            
            if room_type == 'boss':
                num_exits = 0
            elif i == num_rooms:
                num_exits = 0
            else:
                num_exits = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            
            room = {
                'id': i,
                'type': room_type,
                'size': size_room,
                'description': room_data.get('description', f'Комната #{i}'),
                'difficulty': random.randint(1, 10),
                'num_exits': num_exits,
                'exits': [],
                'area': (i - 1) // 3 + 1
            }
            
            self.rooms.append(room)
        
        self.generate_connections(connection_density)
        
        return self.rooms, self.connections
    
    def generate_connections(self, density):
        self.connections = []
        num_rooms = len(self.rooms)
        
        # Основной путь
        for i in range(num_rooms - 1):
            self.add_connection(i + 1, i + 2, 'normal')
        
        # Дополнительные связи
        max_extra_connections = max(2, int(num_rooms * density))
        
        for _ in range(max_extra_connections):
            possible_from = [r for r in self.rooms if r['id'] < num_rooms]
            if not possible_from:
                break
            
            from_room = random.choice(possible_from)
            
            possible_targets = [r for r in self.rooms if r['id'] != from_room['id'] 
                               and r['id'] != from_room['id'] + 1
                               and not self.connection_exists(from_room['id'], r['id'])]
            
            if possible_targets:
                to_room = random.choice(possible_targets)
                conn_type = random.choice(['normal', 'secret', 'oneway', 'magic'])
                self.add_connection(from_room['id'], to_room['id'], conn_type)
                from_room['num_exits'] += 1
                from_room['exits'].append(to_room['id'])
    
    def connection_exists(self, from_id, to_id):
        for c in self.connections:
            if c['from'] == from_id and c['to'] == to_id:
                return True
        return False
    
    def add_connection(self, from_id, to_id, conn_type):
        descriptions = {
            'normal': ['Каменный коридор', 'Узкий проход', 'Широкая галерея', 'Лестница вниз'],
            'secret': ['Секретный проход за шкафом', 'Потайная дверь', 'Замаскированный люк', 'Тайный тоннель'],
            'oneway': ['Обрыв', 'Скользкая горка', 'Водоворот', 'Падающая платформа'],
            'magic': ['Мерцающий портал', 'Круг телепортации', 'Зеркальный переход', 'Призывной круг']
        }
        desc_list = descriptions.get(conn_type, descriptions['normal'])
        description = random.choice(desc_list)
        
        self.connections.append({
            'from': from_id,
            'to': to_id,
            'type': conn_type,
            'label': description
        })

# Инициализация
excel_reader = ExcelReader()
dungeon_gen = DungeonGenerator(excel_reader)

# Импортируем MapGenerator из отдельного файла
from map_generator import MapGenerator
map_gen = MapGenerator()
generated_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        size = request.form.get('size', 'medium')
        dungeon_type = request.form.get('dungeon_type', 'standard')
        
        print(f"🔄 Генерация подземелья размером: {size}")
        
        rooms, connections = dungeon_gen.generate(size, dungeon_type)
        
        print(f"📊 Создано: {len(rooms)} комнат, {len(connections)} связей")
        
        map_filename = f'map_{uuid.uuid4().hex}.png'
        map_path = map_gen.generate(rooms, connections, map_filename)
        
        session_id = uuid.uuid4().hex
        generated_data[session_id] = {'rooms': rooms, 'connections': connections, 'map_path': map_path}
        
        rooms_for_json = []
        for room in rooms:
            rooms_for_json.append({
                'id': room['id'],
                'type': room['type'],
                'size': room['size'],
                'description': room['description'],
                'difficulty': room['difficulty'],
                'num_exits': room['num_exits'],
                'area': room['area']
            })
        
        connections_for_json = []
        for conn in connections:
            connections_for_json.append({
                'from': conn['from'],
                'to': conn['to'],
                'type': conn['type'],
                'label': conn.get('label', '')
            })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'map_url': '/' + map_path.replace('\\', '/'),
            'rooms': rooms_for_json,
            'connections': connections_for_json
        })
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<session_id>')
def download(session_id):
    data = generated_data.get(session_id)
    if not data:
        return "Файл не найден", 404
    
    try:
        from doc_generator import DocGenerator
        doc_gen = DocGenerator()
        doc_path = doc_gen.generate_doc(
            data['rooms'], 
            data['connections'], 
            data['map_path'], 
            f'report_{session_id}.docx'
        )
        return send_file(doc_path, as_attachment=True, download_name='dungeon_report.docx')
    except Exception as e:
        print(f"❌ Ошибка создания отчёта: {e}")
        import traceback
        traceback.print_exc()
        return f"Ошибка создания отчёта: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)