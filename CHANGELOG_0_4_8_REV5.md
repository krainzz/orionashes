# Cinzas de Órion — Revisão 0.4.9 FINAL REV5

## Ajustes desta revisão

- Efeitos temporários de cartas passaram a ser tratados explicitamente como estado exclusivo do combate e são substituídos, nunca somados.
- Golpe de Manopla recebeu projétil visual próprio.
- Ataques das criaturas receberam efeitos visuais simples e específicos por espécie.
- Salvamento persistente migrado para `%LOCALAPPDATA%\Cinzas de Órion\save.json`, com criação automática do diretório e sobrescrita atômica do mesmo arquivo.
- Cartas fabricadas são registradas no Album e não são mais equipadas automaticamente.
- Tela da Manopla passou a oferecer um seletor de cartas fabricadas por slot.
- Bônus de ATQ das cartas migrados de valor flat para percentual do ATQ efetivo.
- Escala-base de ATQ percentual definida por raridade para acomodar a expansão futura para aproximadamente 150–200 cartas.

## Balanceamento atual de ATQ por raridade

- Comum: 1,0–1,5%
- Incomum: 1,5–3,0%
- Rara: 4,0–5,0%
- Mítica: 6,0–8,0%
- Lendária: 9,0–12,0%
- Única: 12,0–16,0%

As variantes Normal / + / ++ continuam usando seus multiplicadores existentes (1,0x / 1,5x / 2,0x).
