import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# =========================
# SESSION STATE (CUSTOS)
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

# =========================
# MARKETPLACES
# =========================
marketplaces = {
    "Amazon": {"comissao": 0.12},
    "Americanas": {"comissao": 0.17, "frete_percent": 0.08},
    "Magalu": {"comissao": 0.148},
    "Mercado Livre": {"comissao": 0.17},
    "Olist": {"comissao": 0.19, "frete_percent": 0.11},
    "Shopee": {"comissao": 0.14},
}

# =========================
# TITLE
# =========================
st.title("Calculadora de Margem - Fabricante Online")

# =========================
# INPUT MODO
# =========================
modo = st.radio("Entrada de dados", ["Upload", "Manual"])

prod = None

# =========================
# UPLOAD
# =========================
if modo == "Upload":

    file = st.file_uploader("Upload arquivo", type=["csv","txt"])

    if file:
        try:
            try:
                df = pd.read_csv(file, sep="\t", encoding="latin-1")
            except:
                df = pd.read_csv(file, sep=",", encoding="latin-1")

            df.columns = df.columns.str.strip().str.lower()

            if not all(c in df.columns for c in ["sku","nome","custo_produto"]):
                st.error("Arquivo precisa ter: sku, nome, custo_produto")
                st.stop()

            df["custo_produto"] = df["custo_produto"].astype(float)

            sku = st.text_input("Digite o SKU")

            if sku:
                row = df[df["sku"].astype(str) == sku]

                if row.empty:
                    st.warning("SKU não encontrado")
                else:
                    prod = row.iloc[0].to_dict()  # ✅ PADRONIZAÇÃO

        except Exception as e:
            st.error(e)

# =========================
# MANUAL
# =========================
else:
    st.subheader("Produto manual")

    sku = st.text_input("SKU")
    nome = st.text_input("Nome")
    custo = st.number_input("Custo", 0.01)

    if sku and nome and custo > 0:
        prod = {
            "sku": sku,
            "nome": nome,
            "custo_produto": custo
        }

# =========================
# SE TEM PRODUTO
# =========================
if prod is not None:  # ✅ CORREÇÃO DO ERRO

    st.subheader(prod["nome"])
    st.write(f"Custo: R$ {prod['custo_produto']:.2f}")

    preco = st.number_input("Preço de venda", 0.01)

    # =========================
    # DESCONTO
    # =========================
    st.subheader("Desconto / Rebate")

    c1,c2,c3 = st.columns(3)

    with c1:
        desconto = st.number_input("Desconto %",0.0,90.0,0.0)

    with c2:
        desc_voce = st.number_input("% você paga",0.0,100.0,100.0)

    with c3:
        rebate = st.number_input("% canal paga",0.0,100.0,0.0)

    desconto /= 100
    desc_voce /= 100
    rebate /= 100

    if round(desc_voce + rebate,4) != 1:
        st.warning("Split precisa somar 100%")

    tipo_ml = st.selectbox("Tipo anúncio ML",["Classico","Premium"])

    # =========================
    # AJUSTE DE CUSTOS
    # =========================
    st.subheader("Ajuste de custos (dinâmico)")

    col1,col2,col3 = st.columns(3)

    with col1:
        c["plataforma"] = st.number_input("Plataforma", value=c["plataforma"])
        c["erp"] = st.number_input("ERP", value=c["erp"])
        c["ferramentas"] = st.number_input("Ferramentas", value=c["ferramentas"])

    with col2:
        c["operacao"] = st.number_input("Operação", value=c["operacao"])
        c["marketing"] = st.number_input("Marketing", value=c["marketing"])
        c["outros"] = st.number_input("Outros", value=c["outros"])

    with col3:
        c["pedidos_mes"] = st.number_input("Pedidos/mês", value=c["pedidos_mes"])
        c["custo_pedido"] = st.number_input("Custo/pedido", value=c["custo_pedido"])
        c["armazenagem"] = st.number_input("Armazenagem %", value=c["armazenagem"])

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

        st.subheader("Memória de cálculo")

        st.markdown(f"""
Preço original: **R$ {preco:.2f}**  
Preço com desconto: **R$ {preco_desc:.2f}**

Desconto total: **R$ {valor_desc:.2f}**

Você paga: **R$ {parte_voce:.2f}**  
Canal paga (rebate): **R$ {parte_canal:.2f}**

**Receita final: R$ {receita:.2f}**
""")

        # =========================
        # CUSTOS DINÂMICOS
        # =========================
        custos_fixos = (
            c["plataforma"] + c["erp"] + c["ferramentas"] +
            c["operacao"] + c["marketing"] + c["outros"]
        )

        fixo = custos_fixos / c["pedidos_mes"]

        impostos_total = c["icms"] + c["difal"] + c["pis_cofins"]

        st.subheader("Resultado por marketplace")

        for nome,dados in marketplaces.items():

            comissao_percent = dados["comissao"]
            frete = 0
            taxa_extra = 0

            if nome == "Mercado Livre":
                comissao_percent = 0.12 if tipo_ml=="Classico" else 0.17
                frete = 23

                if receita < 79:
                    taxa_extra = 6.75

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
                prod["custo_produto"] +
                comissao +
                frete +
                impostos +
                armazenagem +
                fixo +
                c["custo_pedido"] +
                taxa_extra
            )

            lucro = receita - custo_total
            margem = (lucro/receita)*100 if receita>0 else 0

            st.write(f"{nome} → Lucro: R$ {lucro:.2f} | Margem: {margem:.2f}%")
