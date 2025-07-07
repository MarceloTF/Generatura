# Generatura

Um **gerador avançado de assinaturas de e-mail** a partir de um template de imagem, dados CSV de funcionários e configuração JSON de layout, gerando arquivos `.webp` prontos para uso em assinaturas padronizadas da empresa.

## Recursos

✅ Gera assinaturas personalizadas em lote a partir de CSV
✅ Utiliza template de imagem base
✅ Configuração flexível via JSON (posições, fonte, cor)
✅ Suporte a UTF-8 e UTF-8-BOM automaticamente
✅ Salva assinaturas em formato `.webp` com compressão ajustável
✅ Saída clara mostrando quais foram geradas e quais falharam

## Pré-requisitos

* Python 3.9+
* Bibliotecas:

  * pillow
  * argparse
  * json
  * csv

Instale o Pillow caso necessário:

```bash
pip install pillow
```

## Estrutura dos arquivos

* `generatura.py` → script principal

* `template.png` → imagem de fundo da assinatura

* `funcionarios.csv` → dados dos funcionários com colunas:

  * `nome`
  * `cargo`
  * `email`
  * `telefone`

* `config.json` → define layout dos campos, fonte, tamanho, cor e posição de cada item.

Exemplo de estrutura no `config.json`:

```json
{
  "nome": {
    "posicao": [505, 41],
    "caminho_fonte": "fontes/Montserrat-Bold.ttf",
    "tamanho_fonte": 25,
    "cor": "0,0,0",
    "negrito": false,
    "italico": false,
    "formatar": "{texto}",
    "largura_maxima": 30,
    "alinhamento": "esquerda"
  },
  "cargo": {
    ...
  },
  "email": {
    ...
  },
  "telefone": {
    ...
  }
}
```

## Como utilizar

Execute no terminal dentro do diretório do projeto:

```bash
python generatura.py --template template.png --saida assinaturas/ --dados funcionarios.csv --config config.json --qualidade 85 --metodo 6
```

**Parâmetros:**

* `--template`: caminho para a imagem de template.
* `--saida`: pasta onde as assinaturas serão salvas.
* `--dados`: CSV com os dados dos funcionários.
* `--config`: arquivo JSON de configuração dos campos.
* `--qualidade` (opcional): qualidade do WebP (0-100, padrão: 75).
* `--metodo` (opcional): método de compressão do WebP (0-6, padrão: 6).

## Resultado

* Geração de arquivos `.webp` no diretório de saída com os nomes:

  * `Nome_Funcionario_assinatura.webp`
* Mensagens de sucesso/erro durante o processamento no terminal.

## Licença

Este projeto pode ser usado internamente para padronização de assinaturas em empresas sem restrição. Caso compartilhe, mantenha referência ao autor original.
