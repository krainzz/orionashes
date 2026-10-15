# Cinzas de Órion 0.4.6 — Kuvaar e Combate Tático

- Seleção explícita de alvo em combate; boss com partes do corpo e ponto fraco.
- Barra de HP inimigo visível sem valor numérico antes do Scan.
- Primeiro boss: Kuvaar, o Sorvedouro.
- Quest A Sede de Qaresh: rastros falsos/verdadeiros, preparação de Água Pura e três abordagens.
- Bacia Seca de Kuvaar, Couraça de Sal, camadas de exposição e Fenda Ventral.
- Água Bruta, Purificador persistente e Água Pura produzível.
- Simulador de Combate na nave liberado após a primeira vitória de boss; Carga de Simulação para rematches virtuais sob condições favoráveis.
- Boss derrotado passa a poder ser reenfrentado virtualmente para novas recompensas.
- Atributos técnicos continuam ocultos durante combate; inimigos revelam dados completos somente com Scan futuro.
- 0.4.6 prepara o caminho para Renome/Notoriedade/Incidentes e evolução social.

- Polimento final: seleção de alvo sem numeração conflitante com as teclas de ataque.
- Purificador improvisado passa a impedir fabricação duplicada quando já está instalado.
- Mensagem de vitória distingue corretamente confronto real de rematch virtual.


## Revisão pós-validação
- Refatoração visual do combate para eliminar sobreposições.
- Barra de HP inimiga mantida sem números.
- Kuvaar destacado no mapa e Bacia Seca com alerta de perigo.
- Simulador passa a ser um projeto que precisa ser fabricado na nave depois da primeira vitória.
- Vitória contra Kuvaar agora gera pensamento narrativo sobre repetir o confronto.


### Revisão de dano por zona (0.4.6)
Precisão/Evasão determina somente a chance de acerto. Depois do acerto, a zona corporal altera apenas a Defesa local. Não existe multiplicador de dano escondido por zona; o dano segue exclusivamente a fórmula central.
