import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# INSERISCI I TUOI DATI
TOKEN_BOT = "IL_TUO_TOKEN"
CHAT_ID_UTENTE = "IL_TUO_ID"

# ABBIAMO CAMBIATO IL NOME DELLA VARIABILE PER FORZARE L'AGGIORNAMENTO
lista_strumenti = ['AAPL', 'NVDA', 'TSLA', 'BTC-USD', 'ETH-USD']

st.title("🤖 Robot Test")

if st.button('Esegui Scansione'):
    # Se l'errore era alla riga 14, ora qui siamo alla riga 16 circa
    for t in lista_strumenti:
        st.write(f"Controllo: {t}...")
        try:
            df = yf.download(t, period="1mo", progress=False)
            prezzo = df['Close'].iloc[-1]
            st.write(f"Prezzo attuale: {prezzo:.2f}")
        except:
            st.error(f"Errore su {t}")
