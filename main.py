import os
import subprocess
import sys
from pydriller.git import Git
from pathlib import Path
import shutil

REPO_URL = 'https://github.com/traccar/traccar.git'

LOCAL_REPO_PATH = 'traccar'

SPOTBUGS_CMD = 'spotbugs'

# Caminho absoluto para o jar do plugin FindSecBugs
FINDBUGS_PLUGIN_JAR = './findsecbugs-plugin-1.12.0.jar'

# Caminho absoluto para o jar do RefactoringMiner
REFACTORING_MINER_JAR = 'RefactoringMiner'

# Caminho absoluto para o jar do CK Metrics
CK_METRICS_JAR = './ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar'

# Pasta onde os CSVs do CK serão salvos
CK_OUTPUT_DIR = 'ck_metrics_output'

# Comando de build (Gradle Wrapper) pulando os testes
BUILD_CMD = ['./gradlew', 'assemble']


# ----------------------------
#  FUNÇÕES AUXILIARES
# ----------------------------

def clone_or_update_repo():
    """
    Clona o repositório se não existir, ou faz 'git fetch --tags' caso já esteja clonado.
    """
    if not os.path.isdir(LOCAL_REPO_PATH):
        print(f'[1/5] Clonando {REPO_URL} em "{LOCAL_REPO_PATH}"…')
        os.system(f'git clone {REPO_URL}')
    else:
        print(f'[1/5] Repositório já existe em "{LOCAL_REPO_PATH}". Atualizando tags…')
        # Para fazer fetch apenas das tags mais recentes
        subprocess.run(['git', 'fetch', '--tags'], cwd=LOCAL_REPO_PATH, check=True)


def get_last_n_tags(n=20):
    """
    Retorna uma lista com os nomes das últimas n tags (releases),
    ordenadas da mais recente para a mais antiga, usando a data do committer.
    """
    print(f'[2/5] Obtendo últimas {n} releases (tags) do repositório…')
    git = Git(LOCAL_REPO_PATH)
    all_tags = git.repo.tags  # lista de strings com todas as tags
    tags_with_dates = []

    for tag in all_tags:
        try:
            commit = git.get_commit_from_tag(tag.name)
            tags_with_dates.append((tag.name, commit.committer_date))
        except Exception:
            # Caso haja tag sem commit válido, ignora
            continue

    # Ordena por committer_date desc → [ (tag, date), ... ]
    tags_sorted = sorted(tags_with_dates, key=lambda x: x[1], reverse=True)
    last_tags = [tag for tag, _ in tags_sorted[:n]][::-1]
    print(f'    → Tags selecionadas: {last_tags}')
    return last_tags


def checkout_tag(tag):
    """
    Dá checkout na tag especificada dentro do repositório local.
    """
    print(f'[3/5] Fazendo checkout na tag "{tag}"…')
    subprocess.run(['git', 'checkout', tag], cwd=LOCAL_REPO_PATH, check=True)


def build_project():
    """
    Roda o comando de build (Gradle) pulando os testes.
    """
    print(f'[4/5] Buildando o projeto (skip tests)…')
    # Observação: assume que o script "./gradlew" está na raiz do LOCAL_REPO_PATH
    subprocess.run(BUILD_CMD, cwd=LOCAL_REPO_PATH, check=True)
    print(f'[4.1/5] Build realizado!')


def run_spotbugs(tag):
    """
    Executa o SpotBugs no diretório de classes compiladas, apontando para o plugin FindSecBugs.
    Salva o XML de saída em "spotbugs_<tag>.xml" na pasta atual onde o script foi chamado.
    """
    print(f'[5/7] Executando SpotBugs (FindSecBugs) para a tag "{tag}"…')
    # Ajuste este path conforme a estrutura do build do traccar:
    # normalmente, classes compiladas ficam em: build/classes/java/main
    classes_dir = os.path.join(LOCAL_REPO_PATH,'target', f'tracker-server.jar')
    output_file = '/spotbugs'
    dir_path = os.path.dirname(output_file)
    os.makedirs(dir_path, exist_ok=True)

    base_dir = Path('spotbugs')

    # Cria todo o caminho se não existir
    base_dir.mkdir(parents=True, exist_ok=True)

    # Agora monte o arquivo dentro desse diretório
    output_file = f"-xml={base_dir}/spotbugs_{tag[1:]}.xml"

    cmd = [
        'spotbugs',
        '-textui',
        '-effort:max',
        output_file,
        classes_dir
    ]
    subprocess.run(cmd, check=True)
    print(f'    → SpotBugs finalizado, saída em "{output_file}"')


def run_refactoringminer(prev_tag, tag):
    """
    Executa o RefactoringMiner comparando o prev_tag com a tag atual.
    Gera um JSON "refactoring_<prev_tag>_to_<tag>.json" na pasta corrente.
    """
    print(f'[6/6] Executando RefactoringMiner de "{prev_tag}" → "{tag}"…')
    output_folder = f'refactoring-miner'
    dir_path = os.path.join(output_folder)
    os.makedirs(dir_path, exist_ok=True)

    cmd = [
        REFACTORING_MINER_JAR,
        '-bt',
        LOCAL_REPO_PATH, prev_tag, tag,
        '-json', f'{output_folder}/refactoring_{prev_tag}_to_{tag}.json',
    ]
    subprocess.run(cmd, check=True)
    print(f'    → RefactoringMiner finalizado, saída em "{output_folder}/refactoring_{prev_tag}_to_{tag}.json"')


def run_ck_metrics(tag):
    """
    Executa a ferramenta CK nas fontes do projeto e gera um CSV com as métricas.
    O CSV será salvo em "CK_OUTPUT_DIR/<tag>/ck_metrics.csv".
    """
    print(f'[7/7] Executando CK metrics para a tag "{tag}"…')
    output_dir = os.path.join(CK_OUTPUT_DIR, tag)
    os.makedirs(output_dir, exist_ok=True)
    output_csv = os.path.join(output_dir, 'ck_metrics.csv')

    # A forma de invocação do CK varia conforme a versão.
    # Abaixo supõe-se que o jar do CK aceita parâmetros "--project" (pasta do projeto)
    # e "--output" (arquivo CSV de saída). Ajuste se sua versão usar flags diferentes.
    cmd = [
        'java', '-jar', CK_METRICS_JAR,
        f'{LOCAL_REPO_PATH}/src/main/java/org/traccar',
        'true', '0', 'true',
         output_csv
    ]
    subprocess.run(cmd, check=True)
    print(f'    → CK metrics gerado em "{output_csv}"')


def main():
    # 1) Clonar ou atualizar o repositório
    clone_or_update_repo()

    # 2) Obter as últimas 20 tags
    tags = get_last_n_tags(19)

    prev_tag = None
    for tag in tags:
        try:
            # 3) Checkout na tag atual
            checkout_tag(tag)

            # 4) Build do projeto (ignorando testes)
            build_project()

            # 5) Rodar SpotBugs + FindSecBugs
            # run_spotbugs(tag)

            # 6) Rodar RefactoringMiner comparando com a tag anterior
            if prev_tag:
                run_refactoringminer(prev_tag, tag)
            #
            # # 7) Rodar CK Metrics
            # run_ck_metrics(tag)

            # Atualiza prev_tag para a próxima iteração
            prev_tag = tag

            print('\n' + '='*60 + '\n')

        except subprocess.CalledProcessError as e:
            print(f'ERRO: comando retornou código {e.returncode}.')
            print(f'      Comando: {" ".join(e.cmd)}')
            sys.exit(1)


if __name__ == '__main__':
    main()
