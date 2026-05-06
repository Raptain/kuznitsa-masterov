import pandas as pd
import random
import os

class ExcelReader:
    def __init__(self, file_path='data/dungeon_data.xlsx'):
        self.file_path = file_path
        self.load_all_data()
    
    def load_all_data(self):
        """Загрузка всех листов Excel"""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        
        self.rooms_df = pd.read_excel(self.file_path, sheet_name='rooms')
        self.connections_df = pd.read_excel(self.file_path, sheet_name='room_connections')
        self.monsters_df = pd.read_excel(self.file_path, sheet_name='monsters')
        self.treasure_df = pd.read_excel(self.file_path, sheet_name='treasure')
        
        print(f"✅ Загружено: {len(self.rooms_df)} комнат, {len(self.monsters_df)} монстров")
    
    def get_random_room(self, room_type=None, size=None):
        """Получить случайную комнату"""
        filtered = self.rooms_df
        if room_type:
            filtered = filtered[filtered['room_type'] == room_type]
        if size:
            filtered = filtered[filtered['size'] == size]
        
        if len(filtered) == 0:
            return self.rooms_df.iloc[0].to_dict()
        
        return filtered.sample(1).iloc[0].to_dict()
    
    def get_random_monster(self, max_cr=5):
        """Получить случайного монстра"""
        filtered = self.monsters_df[self.monsters_df['cr'] <= max_cr]
        if len(filtered) == 0:
            return self.monsters_df.iloc[0].to_dict()
        return filtered.sample(1).iloc[0].to_dict()
    
    def get_random_treasure(self, max_value=1000):
        """Получить случайное сокровище"""
        filtered = self.treasure_df[self.treasure_df['value_gp'] <= max_value]
        if len(filtered) == 0:
            return None
        return filtered.sample(1).iloc[0].to_dict()