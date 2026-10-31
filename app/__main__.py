from .agent import SupportAgent


def main() -> None:
    agent = SupportAgent()
    print("Empório da Música | Assistente de atendimento")
    print(f"Provedor: {agent.provider_name}")
    if agent.provider_name.startswith("modo local"):
        print("Dica: configure GEMINI_API_KEY no .env para habilitar o Gemini.\n")
    print("Digite sua mensagem (ou 'sair' para encerrar).\n")
    while True:
        try:
            message = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté mais!")
            break
        if message.casefold() in {"sair", "exit", "quit"}:
            print("Empório: Obrigado por conversar com a gente. Até mais! 🎶")
            break
        if not message:
            continue
        try:
            print(f"Consultando ({agent.provider_name})...", flush=True)
            response = agent.reply(message)
            print(f"Empório: {response}\n")
        except Exception as exc:
            print(f"Emp\u00f3rio: A consulta falhou ({type(exc).__name__}). Confira modelo, conex\u00e3o e configura\u00e7\u00e3o. N\u00e3o compartilhe a chave da API.")

if __name__ == "__main__":
    main()
