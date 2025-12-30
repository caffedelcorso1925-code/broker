import streamlit as st
import yfinance as yf
import pandas as pd

# --- CONFIGURAZIONE ---
TOKEN_BOT = "IL_TUO_TOKEN"
CHAT_ID_UTENTE = "IL_TUO_ID"

lista_strumenti = ['AAPL', 'NVDA', 'TSLA', 'BTC-USD', 'ETH-USD', 'GC=F']

st.title("🤖 Robot Massima Resa")

if st.button('🎯 Esegui Scansione Ora'):
    st.write("### Analisi in corso...")
    
    for t in lista_strumenti:
        try:
            # Scarichiamo i dati
            df = yf.download(t, period="5d", interval="1d", progress=False)
            
            if not df.empty:
                # FIX: Puliamo i nomi delle colonne (questo risolve l'errore che vedevi)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Prendiamo l'ultimo prezzo di chiusura
                prezzo_chiusura = df['Close'].iloc[-1]
                
                # Visualizziamo il risultato
                st.success(f"✅ {t}: {float(prezzo_chiusura):.2f}€")
            else:
                st.warning(f"⚠️ {t}: Nessun dato ricevuto")
                
        except Exception as e:
            st.error(f"❌ Errore su {t}: {str(e)}")

    st.write("---")
    st.info("Se vedi i prezzi qui sopra, il collegamento dati è ripristinato!")
