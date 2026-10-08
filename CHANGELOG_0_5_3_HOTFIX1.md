# Cinzas de Órion — 0.5.3 HOTFIX 1

## Correção da identidade dos tipos e dos efeitos táticos

- Consolidada a lista de tipos de criaturas/cartas em apenas: **Terra, Metal, Fogo, Água, Elétrico, Planta, Luz e Trevas**.
- Tipos que haviam sido introduzidos indevidamente (`Vento`, `Cristal`, `Sal`, `Biológico` e `Energia`) foram retirados dos campos de tipo. Termos como sal, cristal e gelo continuam podendo existir normalmente como nomes de materiais, regiões ou características visuais; não são tratados como tipos.
- Os tipos já válidos que faziam parte da fauna permanecem preservados. Criaturas que estavam com um tipo inválido receberam um tipo pertencente ao conjunto canônico, sem alterar nome, atributos ou função de combate.

## Efeitos táticos por tipo

- **Elétrico:** chance de **Atordoamento** por 1 turno.
- **Água:** chance de **Afogamento**. Não causa dano; dobra o custo do próximo ataque especial do alvo.
- **Metal:** chance de reduzir o **ATQ** do alvo em percentual por duração limitada.
- **Terra:** identidade defensiva já estabelecida, incluindo **Escudo** e outros bônus defensivos já presentes nas cartas.
- **Fogo:** chance de aplicar **Queimadura (DoT)** moderada.
- **Planta, Luz e Trevas:** permanecem sem efeito tático específico novo nesta versão.

Os efeitos que haviam sido associados de forma indevida a redução de DEF, redução de Precisão e enfraquecimento em tipos ainda não definidos foram removidos das cartas atuais.

## Afogamento

- O efeito é persistente até que o próximo ataque especial seja utilizado.
- Se o alvo usar um ataque básico antes da técnica especial, o Afogamento continua ativo.
- O custo dobrado é aplicado somente ao próximo ataque especial efetivamente utilizado.
- Não existe dano periódico de Afogamento.

## Compatibilidade

- Nenhuma alteração no formato do save é necessária.
- A versão persistida continua sendo `53`, mantendo compatibilidade com os saves da série 0.5.x.
