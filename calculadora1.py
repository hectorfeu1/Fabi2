import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# MARKETPLACES EDITÁVEIS
# =========================
st.title("Simulador de Preço e Rebate")

st.subheader("Comissão por marketplace")

marketplaces = {
    "Amazon": 0.12,
    "Americanas": 0.17,
    "Magalu": 0.148,
    "Mercado Livre": 0.17,
    "Olist": 0.19,
    "Shopee": 0.14,
}

cols = st.columns(3)
marketplaces_edit = {}

for i,(nome,comissao) in enumerate(marketplaces.items()):
    with cols[i % 3]:
        val = st.number_input(f"{nome} (%)", value=comissao*100)
        marketplaces_edit[nome] = val/100

# =========================
# INPUT PRODUTO
# =========================
modo = st.radio("Entrada", ["Upload", "Manual"])
prod = None

if modo == "Upload":

    file = st.file_uploader("Arquivo (.txt ou .csv)", type=["csv","txt"])

    if file:
        df = pd.read_csv(file, sep="\t", encoding="latin-1")
        df.columns = df.columns.str.strip().str.lower()

        if not all(c in df.columns for c in ["sku","nome","custo_produto"]):
            st.error("Arquivo inválido")
            st.stop()

        df["custo_produto"] = df["custo_produto"].astype(float)

        sku = st.text_input("SKU")

        if sku:
            row = df[df["sku"].astype(str) == sku]
            if not row.empty:
                prod = row.iloc[0].to_dict()

else:
    c1,c2,c3 = st.columns(3)

    with c1:
        sku = st.text_input("SKU")
    with c2:
        nome = st.text_input("Produto")
    with c3:
        custo = st.number_input("Custo", 0.01)

    if sku and nome and custo > 0:
        prod = {"sku": sku, "nome": nome, "custo_produto": custo}

# =========================
# CÁLCULO
# =========================
if prod:

    st.subheader(prod["nome"])
    st.write(f"Custo: R$ {prod['custo_produto']:.2f}")

    col1,col2 = st.columns(2)

    with col1:
        preco = st.number_input("Preço", 0.01)

    with col2:
        desconto = st.number_input("Desconto %", 0.0, 90.0, 0.0)

    c1,c2 = st.columns(2)

    with c1:
        desc_voce = st.number_input("% você paga",0.0,100.0,100.0)

    with c2:
        rebate = st.number_input("% canal paga",0.0,100.0,0.0)

    desconto /= 100
    desc_voce /= 100
    rebate /= 100

    # =========================
    # MARGEM ALVO
    # =========================
    margem_alvo = st.slider("Margem alvo (%)", 0, 30, 10)

    if preco > 0:

        preco_desc = preco * (1 - desconto)
        valor_desc = preco - preco_desc

        parte_voce = valor_desc * desc_voce
        parte_canal = valor_desc * rebate

        receita = preco_desc + parte_canal

        st.markdown(f"""
        **Receita:** R$ {receita:.2f}  
        **Você paga:** R$ {parte_voce:.2f}  
        **Canal paga:** R$ {parte_canal:.2f}
        """)

        resultados = []

        for nome,comissao_percent in marketplaces_edit.items():

            comissao = receita * comissao_percent
            lucro = receita - comissao - prod["custo_produto"]
            margem = (lucro/receita)*100 if receita>0 else 0

            # PREÇO IDEAL PARA MARGEM ALVO
            margem_decimal = margem_alvo / 100

            preco_ideal = prod["custo_produto"] / (1 - comissao_percent - margem_decimal) if (1 - comissao_percent - margem_decimal) > 0 else 0

            resultados.append((nome, lucro, margem, preco_ideal))

        # =========================
        # MELHOR CANAL
        # =========================
        melhor = max(resultados, key=lambda x: x[1])

        st.markdown("### Resultados")

        cols = st.columns(3)

        for i,(nome,lucro,margem,preco_ideal) in enumerate(resultados):

            destaque = nome == melhor[0]

            if destaque:
                cor = "#00c853"
                titulo = f"🏆 {nome}"
            else:
                if margem < 2:
                    cor = "#ff4b4b"
                elif margem <= 5:
                    cor = "#f0ad4e"
                else:
                    cor = "#28a745"
                titulo = nome

            with cols[i % 3]:
                st.markdown(f"""
                <div style="
                border:2px solid {cor};
                border-radius:12px;
                padding:12px;
                text-align:center;">
                
                <b>{titulo}</b><br><br>

                Lucro<br>
                <b>R$ {lucro:.2f}</b><br><br>

                Margem<br>
                <b>{margem:.2f}%</b><br><br>

                Preço p/ {margem_alvo}%<br>
                <b>R$ {preco_ideal:.2f}</b>

                </div>
                """, unsafe_allow_html=True)
