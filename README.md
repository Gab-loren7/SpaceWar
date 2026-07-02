# 🚀 Jogo da Nave com Pyxel

Este projeto é um jogo desenvolvido em Python utilizando a biblioteca **Pyxel**.

O objetivo é controlar uma nave espacial, coletar itens espalhados pelo mapa, aumentar a pontuação e evitar colidir com a estrela localizada no centro da tela.

---

## 🎮 Como jogar

Use as seguintes teclas para controlar a nave:

- `W` — acelerar
- `S` — frear
- `A` — girar para a esquerda
- `D` — girar para a direita
- `R` — reiniciar o jogo após o Game Over

---

## ⭐ Objetivo do jogo

O jogador deve coletar os itens coloridos que aparecem na tela.

Cada item possui uma pontuação diferente:

- 🔵 Itens positivos aumentam os pontos
- 🔴 Itens negativos diminuem os pontos
- 🔥 Coletar itens positivos em sequência aumenta o combo
- 💥 Coletar um item negativo quebra o combo

A estrela central possui uma força gravitacional que puxa a nave em sua direção.

---

## ❤️ Sistema de vidas

A nave começa com **5 vidas**.

Ao colidir com a estrela:

1. A nave perde uma vida
2. Uma animação de explosão é exibida
3. A nave reaparece no início
4. O jogador recebe alguns segundos de invencibilidade

Quando todas as vidas acabam, é exibida a tela de **Game Over**.

---

## 📈 Sistema de dificuldade

A dificuldade aumenta conforme a pontuação do jogador.

Quanto maior a pontuação:

- Maior será a força da gravidade
- Mais difícil será controlar a nave
- Maior será o desafio para coletar os itens

A dificuldade máxima é limitada para evitar que o jogo fique impossível.

---

## 🧩 Principais recursos

- Movimentação com aceleração e rotação
- Sistema de gravidade
- Sistema de colisões
- Pontuação positiva e negativa
- Sistema de combo
- Sistema de vidas
- Invencibilidade temporária
- Animação de explosão com partículas
- Aumento progressivo de dificuldade
- Tela de Game Over
- Reinício da partida

---

## 🛠️ Tecnologias utilizadas

- Python
- Pyxel
- Dataclasses
- Biblioteca `math`
- Biblioteca `random`

---

## 📁 Estrutura do projeto

```text
projeto/
├── main.py
├── my_resource.pyxres
└── README.md
