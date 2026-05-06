import random

class DungeonGenerator:
    def __init__(self, excel_reader):
        self.excel = excel_reader
        self.rooms = []
        self.connections = []
    
    def generate(self, size='medium', dungeon_type='standard'):
        """Генерация подземелья с множественными связями"""
        
        # Определяем количество комнат
        if size == 'small':
            num_rooms = random.randint(6, 9)
            connection_density = 0.3  # плотность связей
        elif size == 'medium':
            num_rooms = random.randint(10, 16)
            connection_density = 0.4
        else:
            num_rooms = random.randint(18, 25)
            connection_density = 0.5
        
        self.rooms = []
        
        # Создаём комнаты
        for i in range(1, num_rooms + 1):
            # Определяем тип комнаты
            if i == 1:
                room_type = 'entrance'
            elif i == num_rooms:
                room_type = 'boss'
            else:
                # Вероятности разных типов
                types = ['battle', 'trap', 'treasure', 'puzzle', 'rest', 'gateway']
                if i < num_rooms * 0.3:
                    # Начальные комнаты - больше битв
                    weights = [0.4, 0.2, 0.1, 0.1, 0.1, 0.1]
                elif i < num_rooms * 0.7:
                    # Средние комнаты - больше сокровищ и головоломок
                    weights = [0.25, 0.15, 0.2, 0.2, 0.1, 0.1]
                else:
                    # Финальные комнаты - больше ловушек и шлюзов
                    weights = [0.2, 0.25, 0.15, 0.1, 0.1, 0.2]
                
                room_type = random.choices(types, weights=weights)[0]
            
            # Размер комнаты
            if i < num_rooms / 3:
                size_room = random.choices(['small', 'medium', 'large'], weights=[0.6, 0.3, 0.1])[0]
            elif i < 2 * num_rooms / 3:
                size_room = random.choices(['small', 'medium', 'large'], weights=[0.3, 0.5, 0.2])[0]
            else:
                size_room = random.choices(['small', 'medium', 'large'], weights=[0.1, 0.4, 0.5])[0]
            
            # Описание из Excel
            room_data = self.excel.get_random_room(room_type, size_room)
            
            # Определяем, сколько выходов из комнаты
            if room_type == 'gateway':
                num_exits = random.randint(2, 4)  # Шлюз имеет несколько выходов
            elif room_type == 'boss':
                num_exits = 0  # У босса нет выходов
            elif i == num_rooms:
                num_exits = 0  # Последняя комната не имеет выходов
            else:
                num_exits = random.choices([1, 2, 3], weights=[0.6, 0.3, 0.1])[0]
            
            # Создаём комнату
            room = {
                'id': i,
                'type': room_type,
                'size': size_room,
                'description': room_data.get('description', f'Комната #{i}'),
                'difficulty': random.randint(1, 10),
                'num_exits': num_exits,
                'exits': [],  # Список ID комнат, куда можно перейти
                'is_visited': False
            }
            
            self.rooms.append(room)
        
        # Генерируем связи между комнатами
        self.generate_connections(connection_density)
        
        return self.rooms, self.connections
    
    def generate_connections(self, density):
        """Генерация множественных связей между комнатами"""
        self.connections = []
        num_rooms = len(self.rooms)
        
        # Связываем комнаты в последовательность (основной путь)
        for i in range(num_rooms - 1):
            self.add_connection(i + 1, i + 2, 'normal')
        
        # Добавляем дополнительные связи на основе плотности
        max_extra_connections = int(num_rooms * density)
        extra_connections = 0
        
        while extra_connections < max_extra_connections:
            # Выбираем случайную комнату (не последнюю)
            possible_from = [r for r in self.rooms if r['id'] < num_rooms]
            if not possible_from:
                break
                
            from_room = random.choice(possible_from)
            
            # Выбираем комнату для связи (не текущую и не следующую по порядку)
            possible_targets = [r for r in self.rooms if r['id'] != from_room['id'] 
                               and r['id'] != from_room['id'] + 1
                               and not self.connection_exists(from_room['id'], r['id'])]
            
            if possible_targets:
                to_room = random.choice(possible_targets)
                
                # Определяем тип связи
                if from_room['type'] == 'gateway':
                    conn_type = random.choice(['normal', 'oneway', 'secret', 'magic'])
                elif from_room['type'] == 'trap':
                    conn_type = random.choice(['oneway', 'secret'])
                else:
                    conn_type = random.choice(['normal', 'magic'] if random.random() < 0.2 else ['normal'])
                
                # Добавляем связь
                self.add_connection(from_room['id'], to_room['id'], conn_type)
                extra_connections += 1
                
                # Обновляем количество выходов в комнате
                from_room['num_exits'] += 1
                from_room['exits'].append(to_room['id'])
        
        # Добавляем секретные проходы
        num_secret = max(1, num_rooms // 10)
        for _ in range(num_secret):
            possible_from = [r for r in self.rooms if r['id'] < num_rooms - 1]
            if not possible_from:
                break
            from_room = random.choice(possible_from)
            # Секретный проход может вести дальше по сюжету
            skip = random.randint(2, min(5, num_rooms - from_room['id']))
            to_id = from_room['id'] + skip
            
            if to_id <= num_rooms and not self.connection_exists(from_room['id'], to_id):
                self.add_connection(from_room['id'], to_id, 'secret')
                from_room['num_exits'] += 1
                from_room['exits'].append(to_id)
        
        # Добавляем магические порталы (редко)
        num_magic = max(1, num_rooms // 15)
        added_magic = 0
        for _ in range(num_magic):
            possible_from = [r for r in self.rooms if r['id'] < num_rooms - 1]
            if not possible_from:
                break
            from_room = random.choice(possible_from)
            
            # Магический портал может вести в любую комнату (вперёд или назад)
            possible_targets = [r for r in self.rooms if r['id'] != from_room['id'] 
                               and abs(r['id'] - from_room['id']) > 2
                               and not self.connection_exists(from_room['id'], r['id'])]
            
            if possible_targets and added_magic < num_magic:
                to_room = random.choice(possible_targets)
                self.add_connection(from_room['id'], to_room['id'], 'magic')
                from_room['num_exits'] += 1
                from_room['exits'].append(to_room['id'])
                added_magic += 1
    
    def connection_exists(self, from_id, to_id):
        """Проверяет, существует ли уже связь"""
        return any(c['from'] == from_id and c['to'] == to_id for c in self.connections)
    
    def add_connection(self, from_id, to_id, conn_type):
        """Добавляет новую связь с описанием"""
        descriptions = {
            'normal': [
                'Каменный коридор',
                'Узкий проход',
                'Широкая галерея',
                'Лестница вниз',
                'Каменный мост',
                'Туннель с факелами'
            ],
            'secret': [
                'Секретный проход за книжным шкафом',
                'Потайная дверь в стене',
                'Замаскированный люк в полу',
                'Тайный тоннель',
                'Скрытая лестница за гобеленом',
                'Проход через камин'
            ],
            'oneway': [
                'Обрыв с которого нельзя вернуться',
                'Скользкая горка вниз',
                'Водоворот, затягивающий внутрь',
                'Падающая платформа',
                'Односторонний портал',
                'Ловушка-телепорт'
            ],
            'magic': [
                '✨ Мерцающий портал фиолетового цвета',
                '🔮 Древний круг телепортации',
                '🪞 Зеркальный переход между мирами',
                '⭐ Призывной круг из звёздной пыли',
                '🌀 Вихревой портал с сиянием',
                '🔥 Портал из живого пламени'
            ]
        }
        
        desc_list = descriptions.get(conn_type, descriptions['normal'])
        description = random.choice(desc_list)
        
        self.connections.append({
            'from': from_id,
            'to': to_id,
            'type': conn_type,
            'label': description
        })