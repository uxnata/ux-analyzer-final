#!/usr/bin/env python3
import sys
import os

# Добавляем текущую директорию в путь
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}")

try:
    from ux_analyzer_classes import CompanyConfig, BriefManager
    print("✅ ux_analyzer_classes imported successfully")
except ImportError as e:
    print(f"❌ Error importing ux_analyzer_classes: {e}")

try:
    from ux_analyzer_core import AdvancedUXAnalyzer
    print("✅ ux_analyzer_core imported successfully")
except ImportError as e:
    print(f"❌ Error importing ux_analyzer_core: {e}")

try:
    from ux_report_generator import EnhancedReportGenerator
    print("✅ ux_report_generator imported successfully")
except ImportError as e:
    print(f"❌ Error importing ux_report_generator: {e}")

print("Test completed")
