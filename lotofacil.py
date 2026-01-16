import random

# ==========================
# Configurações principais
# ==========================

QTDE_DEZENAS_TOTAL = 25
QTDE_DEZENAS_POR_JOGO = 15


# ==========================
# Funções básicas
# ==========================

def gerar_jogo_lotofacil():
    """
    Gera um jogo da Lotofácil com 15 dezenas entre 1 e 25, sem repetir.
    """
    return sorted(random.sample(range(1, QTDE_DEZENAS_TOTAL + 1), QTDE_DEZENAS_POR_JOGO))


def contar_pares_impares(jogo):
    """
    Conta quantos números pares e ímpares existem no jogo.
    """
    pares = sum(1 for n in jogo if n % 2 == 0)
    impares = len(jogo) - pares
    return pares, impares


def jogo_valido(jogo,
                min_pares=5, max_pares=10,
                soma_min=150, soma_max=250,
                min_repetidos=None, max_repetidos=None,
                jogo_base=None):
    """
    Aplica filtros ao jogo:
    - quantidade mínima e máxima de pares
    - faixa mínima e máxima da soma dos números
    - quantidade de dezenas repetidas em relação a um jogo base (opcional)
    """

    # Filtro de pares/ímpares
    pares, impares = contar_pares_impares(jogo)
    if not (min_pares <= pares <= max_pares):
        return False

    # Filtro de soma
    soma = sum(jogo)
    if not (soma_min <= soma <= soma_max):
        return False

    # Filtro de repetidos com um jogo anterior (se fornecido)
    if jogo_base is not None and min_repetidos is not None and max_repetidos is not None:
        repetidos = len(set(jogo) & set(jogo_base))
        if not (min_repetidos <= repetidos <= max_repetidos):
            return False

    return True


def gerar_jogos_filtrados(qtd_jogos,
                          min_pares=5, max_pares=10,
                          soma_min=150, soma_max=250,
                          min_repetidos=None, max_repetidos=None,
                          jogo_base=None,
                          limite_tentativas=1_000_000):
    """
    Gera a quantidade desejada de jogos que passam pelos filtros definidos.
    """
    jogos = []
    tentativas = 0

    while len(jogos) < qtd_jogos and tentativas < limite_tentativas:
        tentativas += 1
        jogo = gerar_jogo_lotofacil()
        if jogo_valido(jogo,
                       min_pares=min_pares, max_pares=max_pares,
                       soma_min=soma_min, soma_max=soma_max,
                       min_repetidos=min_repetidos, max_repetidos=max_repetidos,
                       jogo_base=jogo_base):
            if jogo not in jogos:  # evita jogos duplicados
                jogos.append(jogo)

    return jogos, tentativas


# ==========================
# Interface de texto
# ==========================

def ler_int_padrao(msg, valor_padrao):
    """
    Lê um número inteiro do usuário. Se vazio, usa valor padrão.
    """
    texto = input(f"{msg} (padrão = {valor_padrao}): ").strip()
    if texto == "":
        return valor_padrao
    return int(texto)


def ler_sim_nao(msg):
    """
    Pergunta algo do tipo [s/n] e retorna True/False.
    """
    while True:
        resp = input(f"{msg} [s/n]: ").strip().lower()
        if resp in ("s", "sim"):
            return True
        if resp in ("n", "nao", "não"):
            return False
        print("Responda apenas com s ou n.")


def main():
    print("=" * 50)
    print(" GERADOR DE JOGOS - LOTOFÁCIL ")
    print("=" * 50)
    print()

    qtd_jogos = ler_int_padrao("Quantos jogos você quer gerar?", 10)

    print("\n--- Filtros de pares/ímpares ---")
    min_pares = ler_int_padrao("Mínimo de pares", 5)
    max_pares = ler_int_padrao("Máximo de pares", 10)

    print("\n--- Filtro de soma dos números ---")
    soma_min = ler_int_padrao("Soma mínima", 150)
    soma_max = ler_int_padrao("Soma máxima", 250)

    print("\n--- Filtro de repetição em relação a um jogo anterior (opcional) ---")
    usar_jogo_base = ler_sim_nao("Quer usar um jogo anterior como referência?")
    jogo_base = None
    min_repetidos = None
    max_repetidos = None

    if usar_jogo_base:
        print("Digite o jogo base com 15 números entre 1 e 25, separados por espaço.")
        while True:
            try:
                linha = input("Jogo base: ").strip()
                numeros = [int(x) for x in linha.split()]
                if len(numeros) != QTDE_DEZENAS_POR_JOGO:
                    print(f"Você precisa informar exatamente {QTDE_DEZENAS_POR_JOGO} números.")
                    continue
                if any(n < 1 or n > QTDE_DEZENAS_TOTAL for n in numeros):
                    print("Todos os números devem estar entre 1 e 25.")
                    continue
                jogo_base = sorted(set(numeros))
                if len(jogo_base) != QTDE_DEZENAS_POR_JOGO:
                    print("Não pode haver números repetidos.")
                    continue
                break
            except ValueError:
                print("Entrada inválida. Digite apenas números separados por espaço.")

        min_repetidos = ler_int_padrao("Mínimo de dezenas repetidas com o jogo base", 5)
        max_repetidos = ler_int_padrao("Máximo de dezenas repetidas com o jogo base", 10)

    print("\nGerando jogos, aguarde...")

    jogos, tentativas = gerar_jogos_filtrados(
        qtd_jogos=qtd_jogos,
        min_pares=min_pares,
        max_pares=max_pares,
        soma_min=soma_min,
        soma_max=soma_max,
        min_repetidos=min_repetidos,
        max_repetidos=max_repetidos,
        jogo_base=jogo_base
    )

    print(f"\nTentativas realizadas: {tentativas}")
    print(f"Jogos gerados: {len(jogos)}\n")

    for i, jogo in enumerate(jogos, start=1):
        numeros_formatados = " ".join(f"{n:02d}" for n in jogo)
        pares, impares = contar_pares_impares(jogo)
        soma = sum(jogo)
        print(f"Jogo {i:02d}: {numeros_formatados}  | Pares: {pares:2d}  Ímpares: {impares:2d}  Soma: {soma}")

    if len(jogos) < qtd_jogos:
        print("\nAviso: não foi possível gerar todos os jogos com esses filtros.")
        print("Tente afrouxar um pouco as condições (pares, soma, repetidos).")


if __name__ == "__main__":
    main()