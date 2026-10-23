# Subjetivo

Escuta a música que está tocando ao redor (ou no próprio celular), identifica e
entrega os links: Spotify, Apple Music, Deezer, YouTube, YouTube Music e uma
página com todas as plataformas.

A identificação usa a API [AudD](https://audd.io) (token gratuito em
https://dashboard.audd.io). O programa só usa a biblioteca padrão do Python.

## Como funciona

1. Grava um trecho curto (12 s) do microfone.
2. Envia o trecho para a AudD, que reconhece a música.
3. Mostra os links no terminal, dispara uma notificação no Android e grava em
   `~/.subjetivo/historico.jsonl`.
4. Espera 20 s e repete. A mesma música em sequência não é notificada de novo.

## Android (segundo plano, via Termux)

1. Instale **Termux** e **Termux:API** pelo F-Droid e conceda a permissão de microfone ao Termux:API.
2. No Termux:
   ```sh
   pkg install python termux-api git
   git clone https://github.com/matheusct2/subjetivo && cd subjetivo
   export AUDD_API_TOKEN=seu_token
   termux-wake-lock        # evita que o Android suspenda o processo
   python -m subjetivo
   ```
3. Minimize o Termux: ele continua escutando e envia uma notificação a cada
   música nova. Tocar na notificação abre o link.

Limitação do Android: um app em segundo plano só grava o *microfone*, então ele
ouve a música pelo alto-falante do aparelho. O Android não deixa apps comuns
capturar o áudio interno de outros apps.

## Desktop

```sh
pip install sounddevice
export AUDD_API_TOKEN=seu_token
python -m subjetivo
```

## Opções

```
--seconds N   duração de cada gravação (padrão 12)
--pause N     espera entre ciclos (padrão 20)
--once        identifica uma vez e sai
--file ARQ    identifica um arquivo de áudio existente
--history P   caminho do histórico
```

## Testes

```sh
pip install pytest && python -m pytest
```
