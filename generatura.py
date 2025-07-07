import os
import json
from PIL import Image, ImageDraw, ImageFont
import textwrap
import argparse
import csv
import chardet

def carregar_fonte(caminho_fonte, tamanho_fonte):
    try:
        return ImageFont.truetype(caminho_fonte, tamanho_fonte)
    except Exception as erro:
        raise ValueError(f"Erro ao carregar a fonte {caminho_fonte}: {str(erro)}")


def gerar_assinatura_email(
    caminho_template: str,
    diretorio_saida: str,
    dados_funcionarios: list[dict],
    config_campos: dict,
    qualidade: int = 75,
    metodo: int = 6
) -> None:
    if not isinstance(dados_funcionarios, list) or not all(isinstance(f, dict) for f in dados_funcionarios):
        raise ValueError("dados_funcionarios deve ser uma lista de dicionários")

    if not config_campos or not isinstance(config_campos, dict):
        raise ValueError("config_campos deve ser um dicionário não vazio")

    try:
        os.makedirs(diretorio_saida, exist_ok=True)
    except OSError as e:
        raise OSError(f"Não foi possível criar o diretório de saída: {str(e)}")

    try:
        template = Image.open(caminho_template)
    except Exception as e:
        raise FileNotFoundError(f"Erro ao carregar template: {str(e)}")

    for funcionario in dados_funcionarios:
        try:
            campos_obrigatorios = set(config_campos.keys()) - {'formatar', 'largura_maxima', 'espacamento_linhas', 'alinhamento'}
            campos_faltantes = campos_obrigatorios - funcionario.keys()

            if campos_faltantes:
                raise ValueError(
                    f"Funcionário {funcionario.get('nome', 'sem nome')} faltando campos: {campos_faltantes}. "
                    f"Campos obrigatórios: {campos_obrigatorios}"
                )

            if 'nome' in funcionario and not funcionario['nome'].strip():
                raise ValueError("Campo 'nome' está vazio.")

            assinatura = template.copy()
            desenho = ImageDraw.Draw(assinatura)

            for nome_campo, config in config_campos.items():
                if nome_campo in funcionario:
                    texto = str(funcionario[nome_campo])

                    if 'formatar' in config:
                        texto = config['formatar'].format(texto=texto)

                    if 'largura_maxima' in config:
                        quebra_texto = textwrap.TextWrapper(width=config['largura_maxima'])
                        texto = '\n'.join(quebra_texto.wrap(texto))

                    fonte = carregar_fonte(
                        config['caminho_fonte'],
                        config['tamanho_fonte'],
                    )

                    desenho.text(
                        tuple(config['posicao']),
                        texto,
                        fill=tuple(config['cor']) if isinstance(config['cor'], list) else config['cor'],
                        font=fonte,
                        spacing=config.get('espacamento_linhas', 4),
                        align=config.get('alinhamento', 'left')
                    )

            nome_arquivo = args.nome_arquivo.format(
                nome=funcionario.get("nome", "sem_nome").replace(" ", "_"),
                cargo=funcionario.get("cargo", "").replace(" ", "_"),
                email=funcionario.get("email", "").replace("@", "_at_"),
                telefone=funcionario.get("telefone", "").replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
            )
            caminho_completo = os.path.join(diretorio_saida, nome_arquivo)

            assinatura.save(
                caminho_completo,
                format='webp',
                quality=qualidade,
                method=metodo
            )

            print(f"Assinatura gerada: {caminho_completo}")

        except Exception as e:
            print(f"Erro ao processar funcionário {funcionario.get('nome', 'sem nome')}: {str(e)}")
            continue

def detectar_encoding(caminho_csv):
    """Lê alguns bytes do CSV para detectar o encoding automaticamente."""
    with open(caminho_csv, 'rb') as arquivo:
        resultado = chardet.detect(arquivo.read(4096))  # Analisa os primeiros 4KB
        return resultado['encoding'] if resultado['encoding'] else 'utf-8'

def ler_funcionarios_csv(caminho_csv):
    """Lê o CSV independentemente do encoding e do delimitador, garantindo robustez."""
    encoding_detectado = detectar_encoding(caminho_csv)
    
    funcionarios = []
    
    try:
        with open(caminho_csv, mode='r', encoding=encoding_detectado, newline='') as arquivo:
            leitor = csv.DictReader(arquivo)  # Detecta delimitador automaticamente
            
            colunas_esperadas = set(leitor.fieldnames)
            for i, linha in enumerate(leitor, 1):
                if not linha or set(linha.keys()) != colunas_esperadas:
                    raise ValueError(f"Linha {i} tem estrutura diferente do cabeçalho")
                
                if not any(valor.strip() for valor in linha.values()):
                    continue  # Ignora linha vazia
                
                funcionarios.append({k: v.strip() for k, v in linha.items()})
        
        return funcionarios

    except Exception as erro:
        raise ValueError(f"Erro ao ler arquivo CSV ({encoding_detectado}): {str(erro)}")

def ler_configuracao_json(caminho_json):
    try:
        with open(caminho_json, 'r', encoding='utf-8') as arquivo:
            config = json.load(arquivo)
            for campo, valores in config.items():
                if isinstance(valores.get('cor'), str):
                    config[campo]['cor'] = tuple(map(int, valores['cor'].split(',')))
            return config
    except Exception as erro:
        raise ValueError(f"Erro ao ler arquivo JSON: {str(erro)}")

class TradutorArgumentos(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        mensagem_ptbr = message.replace('the following arguments are required:', 'os seguintes argumentos são obrigatórios:')
        mensagem_ptbr = mensagem_ptbr.replace('error:', 'erro:')
        print(f"\n{self.prog}: {mensagem_ptbr}")
        self.exit(2)

if __name__ == "__main__":
    parser = TradutorArgumentos(
        prog='generatura.py',
        description='Gerador avançado de assinaturas de e-mail.',
        usage='%(prog)s --template ARQUIVO --saida DIRETORIO --dados CSV --config JSON [opções]',
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    grupo_obrigatorios = parser.add_argument_group('Argumentos obrigatórios')
    grupo_obrigatorios.add_argument('--template', required=True, metavar='ARQUIVO', help='Caminho para o template de fundo (PNG/JPG)')
    grupo_obrigatorios.add_argument('--saida', required=True, metavar='DIRETORIO', help='Diretório de saída para as assinaturas')
    grupo_obrigatorios.add_argument('--dados', required=True, metavar='CSV', help='Arquivo CSV com dados dos funcionários')
    grupo_obrigatorios.add_argument('--config', required=True, metavar='JSON', help='Arquivo JSON com configuração dos campos')

    grupo_opcionais = parser.add_argument_group('Opções')
    grupo_opcionais.add_argument('-h', '--ajuda', action='help', default=argparse.SUPPRESS, help='Mostrar esta mensagem de ajuda e sair')
    grupo_opcionais.add_argument('--qualidade', type=int, default=75, metavar='QUALIDADE', help='Qualidade WebP (0-100, padrão: 75)')
    grupo_opcionais.add_argument('--metodo', type=int, default=6, metavar='MÉTODO', help='Método de compressão WebP (0-6, padrão: 6)')
    grupo_opcionais.add_argument('--nome-arquivo', default="{nome}_assinatura.webp", metavar="FORMATO", help="Formato do nome do arquivo de saída. Use {nome}, {cargo}, {email}, {telefone}.")

    args = parser.parse_args()

    try:
        dados_funcionarios = ler_funcionarios_csv(args.dados)
        config_campos = ler_configuracao_json(args.config)

        sucesso = 0
        falha = 0

        for funcionario in dados_funcionarios:
            try:
                gerar_assinatura_email(
                    caminho_template=args.template,
                    diretorio_saida=args.saida,
                    dados_funcionarios=[funcionario],
                    config_campos=config_campos,
                    qualidade=args.qualidade,
                    metodo=args.metodo
                )
                sucesso += 1
            except Exception as erro_func:
                print(f"Erro ao processar {funcionario.get('nome', 'funcionário sem nome')}: {str(erro_func)}")
                falha += 1

        if sucesso > 0:
            print(f"\n{sucesso} assinatura(s) gerada(s) com sucesso!")
        if falha > 0:
            print(f"{falha} funcionário(s) não processado(s) por erro.")

    except Exception as erro:
        print(f"\nErro fatal: {str(erro)}")
        exit(1)