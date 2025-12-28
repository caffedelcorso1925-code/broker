import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Il Mio Robot Finanziario", page_icon="📈")
st.title("💰 Il Mio Generatore di Capitale")

# Funzione matematica per l'RSI semplificata
def calcola_rsi(serie, window=14):
    delta = serie.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=window-1, adjust=False).mean()
    ema_down = down.ewm(com=window-1, adjust=False).mean()
    rs = ema_up / ema_down
    return 100 - (100 / (1 + rs))

titoli = ['AAPL', 'TSLA', 'NVDA', 'AMZN', 'MSFT', 'BTC-USD', 'ETH-USD']

if st.button('🤖 Avvia Scansione Ora'):
    for t in titoli:
        # Scarichiamo i dati
        df = yf.download(t, period="2mo", interval="1d", progress=False)
        
        if not df.empty and len(df) > 20:
            # Forza l'estrazione della colonna 'Close' come serie singola
            # Questo risolve il ValueError che hai visto
            if isinstance(df.columns, pd.MultiIndex):
                chiusura = df['Close'][t]
            else:
                chiusura = df['Close']
            
            # Calcolo RSI e Variazione
            rsi_serie = calcola_rsi(chiusura)
            rsi_attuale = float(rsi_serie.iloc[-1])
            prezzo_attuale = float(chiusura.iloc[-1])
            prezzo_5gg_fa = float(chiusura.iloc[-5])
            variazione = ((prezzo_attuale - prezzo_5gg_fa) / prezzo_5gg_fa) * 100

            # Logica dei segnali
            if rsi_attuale < 35: # Leggermente più flessibile per vedere risultati
                st.success(f"🔥 OCCASIONE SU {t}!")
                st.write(f"Prezzo: {prezzo_attuale:.2f}€ | RSI: {rsi_attuale:.1f} | Var. 5gg: {variazione:.1f}%")
            else:
                st.info(f"⚪ {t}: Prezzo {prezzo_attuale:.2f}€ (RSI: {rsi_attuale:.1f})")
        else:
            st.warning(f"⚠️ {t}: Dati non disponibili al momento.")
            
    st.success("✅ Scansione completata!")
