import re
from pydantic import BaseModel


class DrugSummary(BaseModel):
    brand_name: str
    summary: str
    warnings_precautions: str = "This a list of all the warnings and precautions labels from this section only"
    adverse_reactions_library_of_medicine: str = "This a list of all the adverse reactions from this section only"
    boxed_warning: str = "This a list of all the boxed warning from section only"

    def extract_categories(self):
        self.warnings_precautions = self._extract_category(self.summary, 'warnings_precautions')
        self.adverse_reactions_library_of_medicine = self._extract_category(self.summary, 'adverse_reactions_library_of_medicine')
        self.boxed_warning = self._extract_category(self.summary, 'boxed_warning')
    
    def as_response(self):
        return {
            'warnings_precautions': self.warnings_precautions,
            'adverse_reactions_library_of_medicine': self.adverse_reactions_library_of_medicine,
            'boxed_warning': self.boxed_warning
        }
    
    # Function to extract the categories with support for both formats
    def _extract_category(self, text: str, category: str) -> str:
        # Define the pattern for both formats
        pattern = fr'(?:"{category}":|{category}:)(.*?)(?=\n\n|$|\n\)|\n")'
        match = re.search(pattern, text, re.DOTALL)
        result = None
        if match:
            result = match.group(1).strip()
        return result