from google import genai # Library baru sesuai dokumentasi yang kamu kasih
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    gemini_api_key = fields.Char(string="Gemini API Key", password=True)
    gemini_language = fields.Char(
          string="AI Language Response",
    )

    def get_gemini_response(self, user_prompt):
        if not self.gemini_api_key:
            return "Error: API Key empty. Please set it in Company Settings."

        try:
            client = genai.Client(api_key=self.gemini_api_key)
            response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=user_prompt
            )
            
            return response.text
                
        except Exception as e:
            _logger.error("Gemini SDK Error: %s", str(e))
            return f"Error: {str(e)}"