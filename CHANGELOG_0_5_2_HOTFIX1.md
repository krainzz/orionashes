# Cinzas de Órion 0.5.2 — HOTFIX 1

- Cockpit simplificado: removido o texto/disclaimer extra; permanece apenas o botão `VIAJAR PARA ...` para iniciar uma viagem.
- Equipamento restaurado ao padrão anterior: sem catálogo de designs sob o ícone do elmo e com botão `CONFIGURAR` seguindo o padrão das demais peças. O elmo não volta a ter ação manual de equipar/remover.
- Criada configuração simples do elmo acessada pelo botão `CONFIGURAR`, sem listar designs no painel principal.
- Loader de save endurecido: versões futuras/antigas e lacunas de mapas, criaturas e estatísticas passam por normalização antes da validação, evitando bloqueio desnecessário. O `save.json` corrompido não substitui mais um `bkp.json` válido durante uma nova gravação.
- Estatísticas simplificadas para permanecerem agregadas: combate, planetas e missões não exibem listas de criaturas, mapas ou missões individuais; esses detalhes ficam reservados aos menus apropriados.
- Um mapa de cada planeta novo foi marcado como arena reservada para boss futuro: Orionis, Kael, Nahr e Elyra. Nenhum boss foi criado nesta versão.
