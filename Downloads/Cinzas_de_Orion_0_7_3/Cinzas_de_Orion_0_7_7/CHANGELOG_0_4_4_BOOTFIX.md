# Cinzas de Órion 0.4.4 — correção do inicializador

## Correção
- Removido o uso de `venv` persistente em `%LOCALAPPDATA%`, que podia sofrer redirecionamento quando o Python vinha da Microsoft Store e deixar o caminho de `Scripts\\python.exe` inválido.
- O inicializador agora mantém apenas os pacotes Python necessários em `%LOCALAPPDATA%\\CinzasDeOrion\\deps`.
- O Pygame é reutilizado entre diferentes pastas e versões do jogo.
- O inicializador testa primeiro o Python do sistema com Pygame já disponível.
- A instalação persistente só é executada quando o import de Pygame realmente falha.
