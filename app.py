import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
import pytz # Serve per l'orario italiano

# ... (tieni le funzioni invia_telegram e calcola_rsi di prima)

# Impostiamo il fuso orario italiano
italy_tz = pytz.timezone("Europe/Rome")

if st.button('🚀 Avvia Scansione Dinamica'):
    for t in titoli:
        df = yf.download(t, period="2mo", interval="1d", progress=False)
        
        if not df.empty and len(df) > 20:
            # Calcolo dati (come prima)
            chiusura = df['Close'].squeeze()
            # ... (codice calcolo RSI) ...
            
            rsi_attuale = float(rsi.iloc[-1])
            prezzo = float(chiusura.iloc[-1])
            
            # Recuperiamo l'ora esatta del segnale
            ora_segnale = datetime.now(italy_tz).strftime("%H:%M:%S")

            if rsi_attuale < 40:
                # Messaggio potenziato con l'orario
                msg = (f"🟢 SEGNALE DELLE {ora_segnale}\n"
                       f"Titolo: {t}\n"
                       f"Prezzo: {prezzo:.2f}€\n"
                       f"RSI: {rsi_attuale:.1f}\n"
                       f"👉 Mercato USA aperto da poco" if "15:30" < ora_segnale < "16:30" else "")
                
                st.success(msg)
                invia_telegram(msg)
            else:
                st.info(f"⚪ {t}: RSI {rsi_attuale:.1f} (Ore {ora_segnale})")
