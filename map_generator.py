from PIL import Image, ImageDraw, ImageFont
import math
import os
import random
import string

class MapGenerator:
    def __init__(self, output_dir='static/maps'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Путь к папке со шрифтами
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.fonts_dir = os.path.join(base_dir, 'fonts')
        
        # Типы комнат для легенды (с символами)
        self.room_types = {
            'entrance': {'name': 'Вход', 'symbol': '1'},
            'boss': {'name': 'Босс', 'symbol': '2'},
            'battle': {'name': 'Битва', 'symbol': '3'},
            'treasure': {'name': 'Сокровище', 'symbol': '4'},
            'trap': {'name': 'Ловушка', 'symbol': '5'},
            'puzzle': {'name': 'Головоломка', 'symbol': '6'},
            'rest': {'name': 'Отдых', 'symbol': '7'},
            'gateway': {'name': 'Портал', 'symbol': '8'},
            'shop': {'name': 'Торговец', 'symbol': '9'}
        }
    
    def get_font(self, size):
        """Загружает шрифт из папки fonts или использует стандартный"""
        font_paths = [
            os.path.join(self.fonts_dir, 'arial.ttf'),
            os.path.join(self.fonts_dir, 'Roboto-Regular.ttf'),
            os.path.join(self.fonts_dir, 'DejaVuSans.ttf')
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        # Если шрифт не найден, используем стандартный
        print(f"⚠️ Шрифт не найден, использую стандартный. Размер: {size}")
        return ImageFont.load_default()
    
    def draw_room(self, draw, x, y, size, room, font, font_small):
        """Рисует квадратную комнату только с номером"""
        
        # Квадратная комната с чёрной обводкой
        bbox = [x - size, y - size, x + size, y + size]
        draw.rectangle(bbox, fill='white', outline='black', width=2)
        
        # Только номер комнаты (крупно)
        draw.text((x - 12, y - 8), str(room['id']), fill='black', font=font)
    
    def draw_tunnel(self, draw, from_room, to_room, connection, font_small, letter=None):
        """Рисует туннель из двух параллельных линий с буквой"""
        x1, y1 = from_room['x'], from_room['y']
        x2, y2 = to_room['x'], to_room['y']
        
        conn_type = connection.get('type', 'normal')
        
        room_size = 45
        offset = room_size + 5
        
        # Определяем направление
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return
        
        # Нормализуем направление
        dx = dx / distance
        dy = dy / distance
        
        # Точки начала и конца туннеля (от границ комнат)
        start_x = x1 + dx * offset
        start_y = y1 + dy * offset
        end_x = x2 - dx * offset
        end_y = y2 - dy * offset
        
        # Перпендикуляр для параллельных линий
        perp_x = -dy * 4
        perp_y = dx * 4
        
        # Две параллельные линии
        line1_start = (start_x + perp_x, start_y + perp_y)
        line1_end = (end_x + perp_x, end_y + perp_y)
        line2_start = (start_x - perp_x, start_y - perp_y)
        line2_end = (end_x - perp_x, end_y - perp_y)
        
        # Выбираем стиль линий в зависимости от типа связи
        if conn_type == 'secret':
            # Секретный туннель - пунктирные линии
            self.draw_dashed_line(draw, line1_start, line1_end, 'black', 2)
            self.draw_dashed_line(draw, line2_start, line2_end, 'black', 2)
        elif conn_type == 'oneway':
            # Односторонний туннель - сплошные линии со стрелкой
            draw.line([line1_start, line1_end], fill='black', width=2)
            draw.line([line2_start, line2_end], fill='black', width=2)
            self.draw_arrow_head(draw, end_x, end_y, dx, dy)
        elif conn_type == 'magic':
            # Магический туннель - волнистые линии
            self.draw_wavy_line(draw, line1_start, line1_end, 'black', 2)
            self.draw_wavy_line(draw, line2_start, line2_end, 'black', 2)
        else:
            # Обычный туннель - сплошные линии
            draw.line([line1_start, line1_end], fill='black', width=2)
            draw.line([line2_start, line2_end], fill='black', width=2)
        
        # Добавляем букву посередине туннеля
        if letter:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 - 10
            
            # Белый фон для буквы
            bbox = draw.textbbox((mid_x, mid_y), letter, font=font_small)
            padding = 4
            draw.rectangle([bbox[0]-padding, bbox[1]-padding, 
                          bbox[2]+padding, bbox[3]+padding], 
                          fill='white', outline='black', width=1)
            draw.text((mid_x, mid_y), letter, fill='black', font=font_small)
    
    def draw_dashed_line(self, draw, start, end, color, width):
        """Рисует пунктирную линию"""
        x1, y1 = start
        x2, y2 = end
        length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
        dash_length = 12
        gap_length = 6
        total = dash_length + gap_length
        dashes = int(length / total)
        
        for i in range(dashes):
            t1 = i * total / length
            t2 = (i * total + dash_length) / length
            if t2 > 1:
                t2 = 1
            x1d = x1 + (x2 - x1) * t1
            y1d = y1 + (y2 - y1) * t1
            x2d = x1 + (x2 - x1) * t2
            y2d = y1 + (y2 - y1) * t2
            draw.line([(x1d, y1d), (x2d, y2d)], fill=color, width=width)
    
    def draw_wavy_line(self, draw, start, end, color, width):
        """Рисует волнистую линию"""
        x1, y1 = start
        x2, y2 = end
        points = []
        steps = 40
        for i in range(steps + 1):
            t = i / steps
            tx = x1 + (x2 - x1) * t
            ty = y1 + (y2 - y1) * t + 6 * math.sin(t * math.pi * 3)
            points.append((tx, ty))
        draw.line(points, fill=color, width=width)
    
    def draw_arrow_head(self, draw, x, y, dx, dy):
        """Рисует стрелку на конце туннеля"""
        arrow_size = 10
        angle = math.atan2(dy, dx)
        
        # Смещаем назад от края комнаты
        back_x = x - dx * 8
        back_y = y - dy * 8
        
        arrow_points = [
            (back_x, back_y),
            (back_x - arrow_size * 0.7 * math.cos(angle - math.pi/6), 
             back_y - arrow_size * 0.7 * math.sin(angle - math.pi/6)),
            (back_x - arrow_size * 0.7 * math.cos(angle + math.pi/6), 
             back_y - arrow_size * 0.7 * math.sin(angle + math.pi/6))
        ]
        draw.polygon(arrow_points, fill='black')
    
    def generate(self, rooms, connections, map_filename='dungeon_map.png'):
        """Генерация чёрно-белой карты с легендами"""
        num_rooms = len(rooms)
        print(f"🗺️ Генерация ч/б карты: {num_rooms} комнат, {len(connections)} туннелей")
        
        # Распределяем комнаты по уровням (вертикально)
        levels = {0: [], 1: [], 2: [], 3: [], 4: []}
        
        entrance = None
        boss = None
        other_rooms = []
        
        for room in rooms:
            if room['type'] == 'entrance':
                entrance = room
            elif room['type'] == 'boss':
                boss = room
            else:
                other_rooms.append(room)
        
        if entrance:
            entrance['level'] = 0
            levels[0].append(entrance)
        
        for idx, room in enumerate(other_rooms):
            level = (idx % 3) + 1
            room['level'] = level
            levels[level].append(room)
        
        if boss:
            boss['level'] = 4
            levels[4].append(boss)
        
        for level in levels:
            levels[level].sort(key=lambda r: r['id'])
        
        # Размеры карты с учётом легенд
        room_size = 45
        spacing_x = 140
        spacing_y = 130
        
        max_rooms_per_level = max(len(levels[level]) for level in range(5))
        map_width = max(700, max_rooms_per_level * spacing_x + 200)
        map_height = 5 * spacing_y + 180
        
        # Ширина легенд
        legend_width = 200
        
        # Общая ширина карты + легенды
        total_width = map_width + legend_width * 2 + 40
        
        # Создаём белый фон
        img = Image.new('RGB', (int(total_width), int(map_height)), 'white')
        draw = ImageDraw.Draw(img)
        
        # Загружаем шрифты из папки fonts
        font = self.get_font(16)
        font_small = self.get_font(12)
        font_legend = self.get_font(11)
        
        # Смещение для карты (чтобы легенды были по бокам)
        map_offset_x = legend_width + 20
        
        # Расставляем комнаты по уровням
        for level in range(5):
            level_rooms = levels[level]
            num = len(level_rooms)
            if num > 0:
                start_x = map_offset_x + (map_width - (num - 1) * spacing_x) / 2
                for idx, room in enumerate(level_rooms):
                    room['x'] = int(start_x + idx * spacing_x)
                    room['y'] = int(level * spacing_y + spacing_y)
        
        # Генерируем буквы для туннелей (A, B, C, ...)
        tunnel_letters = {}
        letter_index = 0
        
        # Рисуем туннели (связи) с буквами
        print(f"🚇 Рисую {len(connections)} туннелей...")
        for conn in connections:
            from_room = next((r for r in rooms if r['id'] == conn['from']), None)
            to_room = next((r for r in rooms if r['id'] == conn['to']), None)
            if from_room and to_room:
                # Присваиваем букву для каждого уникального туннеля
                conn_key = f"{conn['from']}-{conn['to']}"
                if conn_key not in tunnel_letters:
                    tunnel_letters[conn_key] = string.ascii_uppercase[letter_index % 26]
                    letter_index += 1
                letter = tunnel_letters[conn_key]
                conn['letter'] = letter
                self.draw_tunnel(draw, from_room, to_room, conn, font_legend, letter)
        
        # Рисуем комнаты
        for room in rooms:
            self.draw_room(draw, room['x'], room['y'], room_size, room, font, font_small)
        
        # Рисуем вертикальные туннели между уровнями
        for level in range(4):
            for i in range(min(len(levels[level]), len(levels[level+1]))):
                from_room = levels[level][i]
                to_room = levels[level+1][i]
                if not any(c['from'] == from_room['id'] and c['to'] == to_room['id'] for c in connections):
                    x1 = from_room['x']
                    y1 = from_room['y'] + room_size + 5
                    x2 = to_room['x']
                    y2 = to_room['y'] - room_size - 5
                    draw.line([(x1 - 4, y1), (x2 - 4, y2)], fill='black', width=2)
                    draw.line([(x1 + 4, y1), (x2 + 4, y2)], fill='black', width=2)
                    draw.polygon([(x2, y2), (x2 - 6, y2 - 10), (x2 + 6, y2 - 10)], fill='black')
        
        # Рисуем рамку вокруг карты
        draw.rectangle([map_offset_x - 10, 10, map_offset_x + map_width + 10, map_height - 10], 
                       outline='black', width=2)
        
        # Заголовок карты
        title_x = map_offset_x + map_width // 2 - 80
        draw.text((title_x, 20), "СХЕМА ПОДЗЕМЕЛЬЯ", fill='black', font=font)
        
        # ============= ЛЕВАЯ ЛЕГЕНДА (ТИПЫ КОМНАТ С ЦИФРАМИ) =============
        legend_left_x = 15
        legend_left_y = 70
        
        draw.rectangle([legend_left_x, legend_left_y, 
                        legend_left_x + legend_width - 10, legend_left_y + 280], 
                       fill='white', outline='black', width=1)
        draw.text((legend_left_x + 10, legend_left_y + 10), "ТИПЫ КОМНАТ", 
                  fill='black', font=font_small)
        
        # Список типов комнат с цифрами
        y_offset = 35
        for room_type, info in self.room_types.items():
            # Квадратик с цифрой
            draw.rectangle([legend_left_x + 10, legend_left_y + y_offset, 
                          legend_left_x + 30, legend_left_y + y_offset + 18], 
                          fill='white', outline='black', width=1)
            # Цифра в квадратике
            draw.text((legend_left_x + 20, legend_left_y + y_offset + 2), 
                     info['symbol'], fill='black', font=font_small)
            # Название типа
            draw.text((legend_left_x + 45, legend_left_y + y_offset + 3), 
                     info['name'], fill='black', font=font_legend)
            y_offset += 24
        
        # ============= ПРАВАЯ ЛЕГЕНДА (ТИПЫ ПРОХОДОВ С ОПИСАНИЯМИ) =============
        legend_right_x = map_offset_x + map_width + 20
        
        draw.rectangle([legend_right_x, legend_left_y, 
                        legend_right_x + legend_width - 10, legend_left_y + 280], 
                       fill='white', outline='black', width=1)
        draw.text((legend_right_x + 10, legend_left_y + 10), "ТИПЫ ПРОХОДОВ", 
                  fill='black', font=font_small)
        
        # Типы проходов с полными описаниями
        passage_types = [
            {'symbol': '═══', 'name': 'Обычный проход', 'desc': 'Стандартный коридор между комнатами'},
            {'symbol': '- - -', 'name': 'Секретный проход', 'desc': 'Скрытый путь, требует поиска'},
            {'symbol': '═══→', 'name': 'Односторонний', 'desc': 'Проход только в одном направлении'},
            {'symbol': '≈≈≈', 'name': 'Магический портал', 'desc': 'Телепортация между комнатами'}
        ]
        
        y_offset = 35
        for passage in passage_types:
            # Символ прохода
            draw.text((legend_right_x + 10, legend_left_y + y_offset), 
                     passage['symbol'], fill='black', font=font)
            # Название
            draw.text((legend_right_x + 60, legend_left_y + y_offset + 2), 
                     passage['name'], fill='black', font=font_small)
            # Описание
            draw.text((legend_right_x + 10, legend_left_y + y_offset + 18), 
                     passage['desc'], fill='gray', font=font_legend)
            y_offset += 42
        
        # Информация о буквах туннелей
        draw.text((legend_right_x + 10, legend_left_y + y_offset + 10), 
                 "БУКВЫ ПЕРЕХОДОВ", fill='black', font=font_small)
        draw.text((legend_right_x + 10, legend_left_y + y_offset + 28), 
                 "A, B, C... - названия", fill='black', font=font_legend)
        draw.text((legend_right_x + 10, legend_left_y + y_offset + 43), 
                 "конкретных туннелей", fill='black', font=font_legend)
        draw.text((legend_right_x + 10, legend_left_y + y_offset + 58), 
                 "на схеме подземелья", fill='black', font=font_legend)
        
        # ============= ТАБЛИЦА СООТВЕТСТВИЯ БУКВ =============
        if tunnel_letters:
            table_x = legend_right_x
            table_y = legend_left_y + 310
            
            table_height = 30 + len(tunnel_letters) * 20
            if table_height > 250:
                table_height = 250
            
            draw.rectangle([table_x, table_y, 
                            table_x + legend_width - 10, 
                            table_y + table_height], 
                           fill='white', outline='black', width=1)
            draw.text((table_x + 10, table_y + 8), "ПЕРЕХОДЫ:", fill='black', font=font_small)
            
            y_offset = 28
            for conn, letter in list(tunnel_letters.items())[:12]:
                parts = conn.split('-')
                draw.text((table_x + 10, table_y + y_offset), 
                         f"{letter}:  {parts[0]} → {parts[1]}", 
                         fill='black', font=font_legend)
                y_offset += 20
            
            if len(tunnel_letters) > 12:
                draw.text((table_x + 10, table_y + y_offset), 
                         f"... и ещё {len(tunnel_letters) - 12} переходов", 
                         fill='gray', font=font_legend)
        
        # Сохраняем карту
        map_path = os.path.join(self.output_dir, map_filename)
        img.save(map_path)
        print(f"✅ Ч/б карта сохранена: {map_path}")
        
        return map_path