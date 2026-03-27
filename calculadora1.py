import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# SESSION STATE
# =========================
if "custos" not in st.session_state:
    st.session_state.custos = {
        "plataforma": 382.0,
        "erp": 660.0,
        "ferramentas": 349.0,
        "operacao": 1945.38,
        "marketing": 17560.0,
        "outros": 17000.0,
        "pedidos_mes": 10000,
        "custo_pedido": 2.625,
        "icms": 0.0125,
        "difal": 0.0655,
        "pis_cofins": 0.0925,
        "armazenagem": 0.018
    }

c = st.session_state.custos

marketplaces = {
    "Amazon": {"comissao": 0.12},
    "Americanas": {"comissao": 0.17, "frete_percent": 0.08},
    "Magalu": {"comissao": 0.148},
    "Mercado Livre": {"comissao": 0.17},
    "Olist": {"comissao": 0.19, "frete_percent": 0.11},
    "Shopee": {"comissao": 0.14},
}

st.title("Calculadora de Margem")

# =========================
# INPUT PRODUTO
# =========================
modo = st.radio("Entrada", ["Upload", "Manual"])
prod = None

if modo == "Upload":
    file = st.file_uploader("Arquivo", type=["csv","txt"])

    if file:
        df = pd.read_csv(file)
        df.columns = df.columns.str.lower()

        sku = st.text_input("SKU")

        if sku:
            row = df[df["sku"].astype(str) == sku]
            if not row.empty:
                prod = row.iloc[0].to_dict()

else:
    col1, col2, col3 = st.columns(3)

    with col1:
        sku = st.text_input("SKU")
    with col2:
        nome = st.text_input("Produto")
    with col3:
        custo = st.number_input("Custo", 0.01)

    if sku and nome and custo > 0:
        prod = {"sku": sku, "nome": nome, "custo_produto": custo}

# =========================
# SE TEM PRODUTO
# =========================
if prod is not None:

    st.subheader(prod["nome"])
    st.write(f"Custo: R$ {prod['custo_produto']:.2f}")

    colp1, colp2 = st.columns(2)

    with colp1:
        preco = st.number_input("Preço", 0.01)

    with colp2:
        tipo_ml = st.selectbox("ML", ["Classico","Premium"])

    # =========================
    # DESCONTO
    # =========================
    st.markdown("### Desconto / Rebate")

    c1,c2,c3 = st.columns(3)

    with c1:
        desconto = st.number_input("Desc %",0.0,90.0,0.0)
    with c2:
        desc_voce = st.number_input("Você %",0.0,100.0,100.0)
    with c3:
        rebate = st.number_input("Canal %",0.0,100.0,0.0)

    desconto /= 100
    desc_voce /= 100
    rebate /= 100

    # =========================
    # CUSTOS EM CARDS COMPACTOS
    # =========================
    st.markdown("### Custos")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown("**Fixos**")
        c["plataforma"] = st.number_input("Plat", value=c["plataforma"])
        c["erp"] = st.number_input("ERP", value=c["erp"])
        c["ferramentas"] = st.number_input("Tools", value=c["ferramentas"])

    with col2:
        st.markdown("**Operação**")
        c["operacao"] = st.number_input("Operação", value=c["operacao"])
        c["marketing"] = st.number_input("Mkt", value=c["marketing"])
        c["outros"] = st.number_input("Outros", value=c["outros"])

    with col3:
        st.markdown("**Variáveis**")
        c["pedidos_mes"] = st.number_input("Pedidos", value=c["pedidos_mes"])
        c["custo_pedido"] = st.number_input("Pedido R$", value=c["custo_pedido"])
        c["armazenagem"] = st.number_input("Armaz %", value=c["armazenagem"])

    col4,col5,col6 = st.columns(3)

    with col4:
        c["icms"] = st.number_input("ICMS", value=c["icms"])
    with col5:
        c["difal"] = st.number_input("DIFAL", value=c["difal"])
    with col6:
        c["pis_cofins"] = st.number_input("PIS/COFINS", value=c["pis_cofins"])

    # =========================
    # CÁLCULO
    # =========================
    if preco > 0:

        preco_desc = preco * (1 - desconto)
        valor_desc = preco - preco_desc

        parte_voce = valor_desc * desc_voce
        parte_canal = valor_desc * rebate

        receita = preco_desc + parte_canal

        st.markdown(f"""
        **Receita:** R$ {receita:.2f} |  
        **Você paga:** R$ {parte_voce:.2f} |  
        **Canal paga:** R$ {parte_canal:.2f}
        """)

        custos_fixos = sum([
            c["plataforma"], c["erp"], c["ferramentas"],
            c["operacao"], c["marketing"], c["outros"]
        ])

        fixo = custos_fixos / c["pedidos_mes"]
        impostos_total = c["icms"] + c["difal"] + c["pis_cofins"]

        # =========================
        # RESULTADOS EM CARDS
        # =========================
        st.markdown("### Resultados")

        resultados = []

        for nome,dados in marketplaces.items():

            comissao_percent = dados["comissao"]
            frete = 0
            taxa_extra = 0

            if nome == "Mercado Livre":
                comissao_percent = 0.12 if tipo_ml=="Classico" else 0.17
                frete = 23

            elif nome == "Shopee":
                frete = 0

            elif nome == "Amazon":
                frete = 6.5 if preco_desc < 79 else 21.9

            elif nome == "Magalu":
                frete = 12

            else:
                frete = receita * dados.get("frete_percent",0)

            comissao = receita * comissao_percent
            impostos = receita * impostos_total
            armazenagem = receita * c["armazenagem"]

            custo_total = (
                prod["custo_produto"] + comissao + frete +
                impostos + armazenagem + fixo +
                c["custo_pedido"] + taxa_extra
            )

            lucro = receita - custo_total
            margem = (lucro/receita)*100 if receita>0 else 0

            resultados.append((nome, lucro, margem))

        cols = st.columns(3)

        for i,(nome,lucro,margem) in enumerate(resultados):

            if margem < 2:
                cor = "#ff4b4b"
            elif margem <= 5:
                cor = "#f0ad4e"
            else:
                cor = "#28a745"

            with cols[i % 3]:
                st.markdown(f"""
                <div style="
                border:2px solid {cor};
                border-radius:12px;
                padding:12px;
                text-align:center;">
                <b>{nome}</b><br>
                Lucro<br><b>R$ {lucro:.2f}</b><br>
                Margem<br><b>{margem:.2f}%</b>
                </div>
                """, unsafe_allow_html=True)
