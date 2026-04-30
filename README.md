# Pintor de Municípios do Ceará

Aplicação local (Streamlit) para destacar municípios do Ceará em um mapa estático bonito (Matplotlib), com exportação em PNG, SVG e PDF.

## 1) Instalação

No terminal, dentro da pasta `projeto_mapa_ceara/`:

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\\Scripts\\activate  # Windows (PowerShell)

pip install -r requirements.txt
```

## 2) Executar

```bash
streamlit run app.py
```

## 2.1) Publicar na Web (via Streamlit Community Cloud)

1. Suba este projeto para um repositório no GitHub.
2. Acesse o Streamlit Community Cloud e clique em **New app**.
3. Selecione o repositório e a branch `main`.
4. Em **Main file path**, use `app.py`.
5. Clique em **Deploy** e use o link gerado.

## 3) Como usar

1. **GeoJSON do Ceará**:
   - Por padrão, a aplicação tenta usar `data/municipios_ceara.geojson`.
    - Você também pode fazer **upload** do seu GeoJSON na interface (caso tenha um arquivo com colunas diferentes).

2. **Informar municípios para pintar** (qualquer uma das opções, ou as duas):
   - **Lista com todos os municípios (recomendado)**:
     - use o seletor com busca; digite e selecione (o mapa atualiza automaticamente);
   - **Digite manualmente** (um por linha ou separados por vírgula), por exemplo:
     - `Fortaleza`
     - `Caucaia, Sobral`
   - **Upload de JSON** com um dos formatos aceitos:
     - `{"municipios": ["Fortaleza", "Caucaia"]}`
     - `{"municipios_pintar": ["Fortaleza", "Caucaia"]}`
     - `["Fortaleza", "Caucaia"]`
     - `[{"municipio": "Fortaleza"}, {"municipio": "Caucaia"}]`
   - Exemplo pronto em `data/exemplo_municipios.json`.

3. **Escolha a cor** no seletor (padrão `#0057A8`).

4. (Opcional) Defina **título** e **subtítulo** do mapa.

5. O mapa atualiza automaticamente conforme você seleciona municípios na lista.
   - Se usar a aba **Colar/JSON**, clique em **Aplicar entrada** para incluir os municípios.

6. Clique em **Limpar seleção** para voltar ao mapa inicial.

7. Clique em **Preparar downloads** e baixe o resultado em **PNG (300 DPI)**, **SVG** e **PDF**.

## 4) Observações sobre o GeoJSON

A aplicação tenta identificar automaticamente a coluna do nome do município testando:

- `NM_MUN`, `NM_MUNICIP`, `NM_MUNICIPIO`, `nome`, `municipio`, `Município`, `MUNICIPIO`, `name`

Se não encontrar, ela mostra as colunas disponíveis para você ajustar o arquivo.

## 5) Logos

As logos exibidas no topo do app ficam em `assets/`:

- `assets/logo_PMCE.png`
- `assets/logo_CPRAIO.jpg`
