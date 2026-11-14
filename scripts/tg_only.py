#!/usr/bin/env python3
"""Nur Telegram auswerten (ohne Kursabruf). Laeuft am Wochenende, damit Meldungen nicht bis Montag warten."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update

if __name__ == "__main__":
    update.process_telegram()
    update.patch_public_files()
    update.flush_checkin()
