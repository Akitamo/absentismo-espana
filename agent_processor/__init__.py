"""
Agent Processor - Sistema de procesamiento de datos ETCL
Transforma datos crudos del INE en tabla unificada para análisis de absentismo
"""

__version__ = "1.0.0"
__author__ = "AbsentismoEspana"

from .processor import ProcessorETCL

__all__ = ['ProcessorETCL']