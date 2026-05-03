import fitz  # PyMuPDF
import base64
import io
import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    ai_score = fields.Float(string="AI Score", readonly=True)
    ai_summary = fields.Text(string="AI Summary", readonly=True)
    ai_questions = fields.Text(string="AI Suggested Questions", readonly=True)

    def clear_ai_analysis(self):
        """Method untuk membersihkan hasil analisis AI, bisa dipanggil saat CV diupdate"""
        self.write({
            'ai_score': 0,
            'ai_summary': '',
            'ai_questions': ''
        })

    def action_analyze_cv_with_ai(self):
        self.ensure_one()
        
        # Gunakan candidate_id jika di Odoo 17+
        target_id = self.candidate_id.id 
        target_model = 'hr.candidate' 

        attachment = self.env['ir.attachment'].sudo().search([
            ('res_model', '=', target_model),
            ('res_id', '=', target_id),
            ('mimetype', '=', 'application/pdf')
        ], limit=1, order='create_date desc')

        if not attachment:
            raise UserError(_("Mohon unggah CV dalam format PDF terlebih dahulu."))

        # Ekstraksi Teks
        pdf_data = base64.b64decode(attachment.datas)
        text_content = ""
        try:
            with fitz.open(stream=io.BytesIO(pdf_data), filetype="pdf") as doc:
                text_content = "".join([page.get_text() for page in doc])
        except Exception as e:
            raise UserError(_("Gagal membaca PDF: %s") % str(e))

        # Prompt dengan instruksi JSON yang ketat
        prompt = f"""
        Tugas: HR Expert.
        Analisis kecocokan CV terhadap posisi: {self.job_id.name}.
        Isi CV: {text_content}
        
        WAJIB kembalikan hanya dalam format JSON murni:
        {{"score": integer_0_sampai_100, "summary": "string_penjelasan_secara_detail_singkat_mengapa_score_tersebut_diberikan_berupa_kelebihan_dan_kekurangan", "questions": ["pertanyaan_1", "pertanyaan_2" dibikin point sebanyak banyak nya sesuai yang di keteahui dari dokumentasi yang di kasih"]}}
        tolong hasil summary dan questions bahasa {self.env.company.gemini_language or 'English'}
        """
        
        raw_response = self.env.company.get_gemini_response(prompt)
        
        # Membersihkan format markdown jika ada
        clean_response = re.sub(r'```json|```', '', raw_response).strip()
        
        try:
            res_data = json.loads(clean_response)
            
            # Ambil list pertanyaan dari JSON
            questions_list = res_data.get('questions', [])
            
            # Pastikan setiap item memiliki bullet point di depannya
            # Kita gunakan format " - " agar rapi di UI Odoo
            formatted_questions = "\n".join([f"- {q}" for q in questions_list])

            self.write({
                'ai_score': res_data.get('score', 0),
                'ai_summary': res_data.get('summary', ''),
                'ai_questions': formatted_questions
            })
        except Exception:
            # Fallback jika JSON gagal di-parse, simpan mentahnya saja
            self.write({
                'ai_summary': raw_response
            })