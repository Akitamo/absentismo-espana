"""
Validador de reglas de negocio (stub temporal)
"""

import pandas as pd
from typing import Dict, Any

class BusinessValidator:
    """
    Validador de reglas de negocio ETCL
    """
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Stub - será implementado después"""
        return {'passed': True, 'warnings': [], 'errors': []}