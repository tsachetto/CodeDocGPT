import argparse
import os
from pathlib import Path
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description='AutoDocGPT - Documentação automática de código usando OpenAI')
    parser.add_argument('input_script', help='Caminho do arquivo de entrada a ser analisado')
    parser.add_argument('output_script', help='Caminho do arquivo de saída documentado')
    parser.add_argument('dicas', nargs='?', default='', help='Dicas adicionais para orientar a documentação')
    args = parser.parse_args()

    # Verifica extensões dos arquivos
    input_ext = Path(args.input_script).suffix
    output_ext = Path(args.output_script).suffix
    if input_ext != output_ext:
        print("Erro: As extensões dos arquivos de entrada e saída devem ser iguais.")
        exit(1)

    # Lê o código fonte com limite de caracteres
    try:
        with open(args.input_script, 'r', encoding='utf-8') as f:
            code_content = f.read(10000)
    except Exception as e:
        print(f"Erro ao ler arquivo de entrada: {e}")
        exit(1)

    # Configura o prompt
    system_role = "Você é um engenheiro de software experiente que escreve documentação clara e objetiva de códigos."
    base_prompt = "Reescreva integralmente o código fornecido, ignorando a documentação atual e recriando uma nova documentação perfeita adequada a ele. Complementando, crie uma introdução em forma de comentário após a importação das libs sobre o código analisado, sua funcionalidade, objetivos e saidas.\n"
    
    if args.dicas:
        prompt_final = f"Como dica sobre o código temos: {args.dicas}\nInclua comentários relevantes em cada parte."
    else:
        prompt_final = "Analise o código e detecte sua finalidade para criar comentários adequados.\n"
    
    prompt_final += "A saída deve ser apenas o código comentado, sem texto adicional ou formatação Markdown."

    # Monta a requisição para OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": f"{base_prompt}{prompt_final}\n\nCódigo:\n{code_content}"}
            ],
            max_tokens=2000
        )
    except Exception as e:
        print(f"Erro na API OpenAI: {e}")
        exit(1)

    # Processa a resposta
    documented_code = response.choices[0].message.content.strip()
    
    # Remove blocos de código Markdown se existirem
    if documented_code.startswith("```"):
        documented_code = '\n'.join(documented_code.split('\n')[1:-1])

    # Salva o arquivo de saída
    try:
        with open(args.output_script, 'w', encoding='utf-8') as f:
            f.write(documented_code)
        print(f"Documentação gerada com sucesso em {args.output_script}")
    except Exception as e:
        print(f"Erro ao salvar arquivo de saída: {e}")
        exit(1)

if __name__ == "__main__":
    main()
