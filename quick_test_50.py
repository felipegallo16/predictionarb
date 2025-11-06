#!/usr/bin/env python3
"""
Prueba rápida con umbral 50%
"""

from arbitrage_detector_quick import QuickArbitrageDetector

def quick_test():
    print("🚀 PRUEBA RÁPIDA CON UMBRAL 50%")
    
    # Crear detector con umbral 50%
    detector = QuickArbitrageDetector(similarity_threshold=50.0)
    
    # Ejecutar análisis completo
    detector.run(export_csv=False, export_json=False, top_n=5)

if __name__ == "__main__":
    quick_test()