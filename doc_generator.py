from docx import Document
from docx.shared import Inches
import os

class DocGenerator:
    def __init__(self, output_dir='static/docs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_doc(self, rooms, map_image_path, filename='dungeon_report.docx'):
        doc = Document()
        doc.add_heading('Отчёт о подземелье', 0)
        
        doc.add_heading('Карта подземелья', level=1)
        doc.add_picture(map_image_path, width=Inches(6))
        
        doc.add_heading('Описания комнат', level=1)
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = '№'
        hdr_cells[1].text = 'Тип'
        hdr_cells[2].text = 'Размер'
        hdr_cells[3].text = 'Описание'
        
        for room in rooms:
            row_cells = table.add_row().cells
            row_cells[0].text = str(room['id'])
            row_cells[1].text = room['type']
            row_cells[2].text = room['size']
            row_cells[3].text = room['description']
        
        filepath = os.path.join(self.output_dir, filename)
        doc.save(filepath)
        return filepath