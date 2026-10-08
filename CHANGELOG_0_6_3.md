# Cinzas de Órion — Versão 0.6.3

## Ataque básico da Manopla
- Refeito o efeito visual do Golpe de Manopla para um feixe tecnológico luminoso.
- Implementado bloom nativo do Pygame com `BLEND_RGB_ADD`, sem bibliotecas externas.
- O feixe usa camadas externas de brilho, núcleo branco, estrias de plasma, halo do emissor e partículas determinísticas no impacto.
- O novo efeito substitui apenas a apresentação visual do ataque básico; cálculo de dano, custo de Memória e demais regras de combate permanecem inalterados.

## Dimensões do personagem
- Sprites de exploração frente/costa/lado: superfície base de `44 x 58 px`.
- Sprite específico de combate frontal: superfície base de `84 x 66 px`.
- Na cena de combate, o sprite frontal é renderizado com escala `1.95`, resultando em aproximadamente `164 x 129 px` de área de superfície.
- O perfil lateral não ganha uma Manopla espelhada: a Manopla continua somente no lado direito, conforme a definição visual do projeto.
