import streamlit as st
import pypdf
import requests

# Configuração da API do Gemini via HTTP Direto
GOOGLE_API_KEY = "AQ.Ab8RN6IFyRyKy5oYnRn1OZV5XnvUqGoX12NeE43aDkddf-w0IA"
URL_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?x-goog-api-key={GOOGLE_API_KEY}"

st.set_page_config(page_title="Analytics de Contratos - Procurement", layout="wide")
st.title("📄 Contrato Simples")
st.write("Insira o PDF do contrato e defina os parâmetros que deseja extrair.")

# Sidebar para configurações adicionais
st.sidebar.header("Configure seu Prompt abaixo")
prompt_padrao = (
    "Atue como um especialista em Procurement e Auditoria de Contratos. "
    "Analise o contrato em anexo e extraia rigorosamente as seguintes informações em formato de tópicos:\n"
    "- Objeto do Contrato (Tipo de serviço que será prestado)\n"
    "- Valor Total Bruto e Condições de Pagamento (As vezes o valor bruto não aparecerá explicito, neste caso, somar o valor dos serviços listados e, multiplicar pela quantidade de meses da duração do contrato.)\n"
    "- Vigência."
)
prompt_usuario = st.sidebar.text_area("Instruções de Extração:", value=prompt_padrao, height=250)

# Upload do Arquivo
uploaded_file = st.file_uploader("Arraste seu contrato em PDF aqui", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF carregado com sucesso!")
    
    if st.button("Analisar Contrato 🚀"):
        with st.spinner("A IA está analisando o documento... Por favor, aguarde."):
            try:
                # Lendo o PDF
                pdf_reader = pypdf.PdfReader(uploaded_file)
                texto_completo = ""
                for page in pdf_reader.pages:
                    texto_completo += page.extract_text() + "\n"
                
                # Montando o payload para a API HTTP
                prompt_final = f"{prompt_usuario}\n\n--- TEXTO DO CONTRATO ---\n{texto_completo}"
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_final}]
                    }]
                }
                
                # Fazendo a requisição post sem depender de bibliotecas externas pesadas
                headers = {'Content-Type': 'application/json'}
                response = requests.post(URL_API, json=payload, headers=headers)
                
                if response.status_code == 200:
                    dados_resposta = response.json()
                    # Extraindo o texto retornado pelo Gemini
                    texto_ia = dados_resposta['candidates'][0]['content']['parts'][0]['text']
                    
                    st.subheader("📋 Resumo Estruturado do Contrato")
                    st.markdown(texto_ia)
                else:
                    st.error(f"Erro na API do Gemini (Status {response.status_code}): {response.text}")
                
            except Exception as e:
                st.error(f"Erro ao processar o contrato: {e}")
