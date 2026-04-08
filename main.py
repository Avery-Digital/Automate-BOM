import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from gui.app import BOMApp

if __name__ == "__main__":
    app = BOMApp()
    app.mainloop()
