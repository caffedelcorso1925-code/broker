import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Il Mio Robot Finanziario", page_icon="📈")
st.title("💰 Il Mio Generatore di Capitale")

# Funzione matematica per l'RSI (senza bisogno di librerie esterne)
def calcola_rsi(serie, window=14):
    delta = serie.diff()
    guadagno = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    perdita = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = guadagno / perdita
    return 100 - (100 / (1 + rs))

titoli = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD']

if st.button('🤖 Avvia Scansione Ora'):
    stato = st.empty()
    
    for t in titoli:
        stato.info(f"🔍 Analisi di: {t}...")
        
        # Scarichiamo 2 mesi di dati
        dati = yf.download(t, period="2mo", interval="1d", progress=False)
        
        if not dati.empty and len(dati) > 14:
            # Usiamo la nostra funzione per l'RSI
            prezzi_chiusura = dati['Close']
            rsi_valori = calcola_rsi(prezzi_chiusura)
            rsi_attuale = rsi_valori.iloc[-1]
            
            # Calcolo variazione % degli ultimi 5 giorni
            prezzo_oggi = prezzi_chiusura.iloc[-1]
            prezzo_5gg_fa = prezzi_chiusura.iloc[-5]
            var_settimanale = ((prezzo_oggi - prezzo_5gg_fa) / prezzo_5gg_fa) * 100

            # Se il calcolo è riuscito (non è un errore "NaN")
            if pd.notnull(rsi_attuale):
                if rsi_attuale < 30 and var_settimanale < -10:
                    st.success(f"🔥 OCCASIONE SU {t}!")
                    st.write(f"Prezzo: {prezzo_oggi:.2f} | RSI: {rsi_attuale:.2f} | Calo: {var_settimanale:.2f}%")
                else:
                    st.write(f"⚪ {t}: Prezzo {prezzo_oggi:.2f} - (RSI: {rsi_attuale:.2f})")
            else:
                st.warning(f"⚠️ {t}: Dati insufficienti per il calcolo oggi.")
        else:
            st.error(f"❌ {t}: Impossibile scaricare i dati.")
            
    stato.success("✅ Scansione completata!")
