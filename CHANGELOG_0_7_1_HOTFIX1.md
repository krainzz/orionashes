# Cinzas de Órion — 0.7.1 HOTFIX 1

## Visualização de Equipamentos
- As visualizações de **Manopla, Elmo, Peitoral e Módulo de Locomoção** agora priorizam os arquivos oficiais em `assets/equips/`.
- Referências utilizadas: `Manopla.png`, `Elmo.png`, `Peitoral.png` e `Grevas.png`.
- Os arquivos não são incluídos nesta distribuição; devem ser colocados manualmente na pasta `assets/equips/`.
- A escala usa `pygame.transform.scale` para preservar a estética pixel-art.
- O desenho procedural anterior permanece como fallback caso algum arquivo ainda não esteja presente.
- Nenhuma regra de progressão/equipamento ou estrutura do save foi alterada.
