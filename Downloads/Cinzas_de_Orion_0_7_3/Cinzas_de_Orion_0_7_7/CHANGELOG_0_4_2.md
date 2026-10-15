# Cinzas de Órion — 0.4.2

## Sociedade

A 0.4.2 é a primeira atualização que transforma os vestígios do planeta em uma sociedade efetivamente presente no mundo. O objetivo é criar a fundação persistente para futuras missões, renome, hack e caminhos diplomáticos/violentos.

### Incluído

- Planeta inicial batizado como **Veyra**.
- Primeira civilização: **Avarin**.
- Primeiro idioma local: **Avari**.
- Primeiro assentamento: **Qaresh**.
- Identidade cultural: sociedade moldada pela escassez de água; reservatórios têm importância social, econômica e histórica.
- Assentamento desenhado diretamente no mapa com reservatório central, abrigos baixos, cobertura de tecido e torre de vigia.
- Três NPCs persistentes: **Iria** (guardiã de água), **Sarek** (vigia das dunas) e **Naevi** (coletora de sucata).
- Avistamento automático ao entrar no raio do assentamento.
- Primeiro contato por `E`: a língua continua incompreensível e a função observada do NPC é registrada.
- Estados persistentes de sociedade: assentamentos descobertos, habitantes observados e primeiro contato.
- Novo objetivo de diário: **Avistar o assentamento local**.
- Mapa de rotas passa a marcar assentamentos descobertos.
- Painel do Diário mostra identidade e cultura da civilização local.
- Migração `save_v041.json` → `save_v042.json`, preservando o save antigo.
- O alvo de save atual passou a ser `save_v042.json`.
- `ESC` passa a respeitar a origem da tela: hotkey/E retorna ao mundo; Menu → função → `ESC` retorna ao Menu.
- `iniciar.bat` passa a instalar o Pygame apenas uma vez por pasta, em `.deps/`, reutilizando-o nas aberturas seguintes.
- 3 novos testes sociais/migração; suíte total: **31 testes**.

### Conceito de Veyra / Avarin

Veyra é um planeta de dunas, pedra exposta e redes antigas de captação subterrânea. Os Avarin construíram seu cotidiano em torno da água: guardar, transportar, lembrar e repartir água são atos sociais de alto valor. A arquitetura evita grandes superfícies verticais, usando abrigos baixos, tecidos esticados e reservatórios protegidos contra poeira e calor.

O primeiro encontro deliberadamente não revela nomes nem traduz a fala. O jogador apenas observa comportamentos e funções. O elmo, numa atualização futura, será a ferramenta que transforma essa experiência em comunicação.


## Nota para 0.4.3
A próxima versão preserva a sociedade de Veyra e prepara uma camada visual de feedback e a economia de progressão por recursos de mundos futuros.
