# morpion.py
# " Un jeu du morpion réalisé avec Python et Tkinter. "


import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


TAILLE_PLATEAU = 3
LISTE_JOUEURS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green"),
)


class JeuduMorpion:
    def __init__(self, players=LISTE_JOUEURS, taille_plateau=TAILLE_PLATEAU):
        self._joueurs = cycle(players)
        self.taille_plateau = taille_plateau
        self.joueur_actuel = next(self._joueurs)
        self.combi_gagnante = []
        self._liste_coups = []
        self._jeu_gagnant = False
        self._combi_gagnantes = []
        self._setup_board()

    def _setup_board(self):
        self._liste_coups = [
            [Move(row, col) for col in range(self.taille_plateau)]
            for row in range(self.taille_plateau)
        ]
        self._combi_gagnantes = self._obtenir_combi_gagnantes()

    def _obtenir_combi_gagnantes(self):
        lignes = [
            [(move.row, move.col) for move in row]
            for row in self._liste_coups
        ]
        colonnes = [list(col) for col in zip(*lignes)]
        first_diagonal = [row[i] for i, row in enumerate(lignes)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(colonnes))]
        return lignes + colonnes + [first_diagonal, second_diagonal]

    def is_valid_move(self, move):
        """Return True if move is valid, and False otherwise """
        row, col = move.row, move.col
        move_was_not_played = self._liste_coups[row][col].label == ""
        no_winner = not self._jeu_gagnant
        return no_winner and move_was_not_played

    def process_move(self, move):
        """Process the current move and check if it's win. """
        row, col = move.row, move.col
        self._liste_coups[row][col] = move
        for combo in self._combi_gagnantes:
            results = set(
                self._liste_coups[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._jeu_gagnant = True
                self.combi_gagnante = combo
                break

    def has_winner(self):
        """Renvoie True si le jeu a un gagnant, et False sinon. """
        return self._jeu_gagnant

    def is_tied(self):
        """Renvoie True si le jeu est égalité, et False sinon"""
        no_winner = not self._jeu_gagnant
        played_moves = (
            move.label for row in self._liste_coups for move in row
        )
        return no_winner and all(played_moves)

    def toggle_player(self):
        """Change de joueur."""
        self.joueur_actuel = next(self._joueurs)

    def reset_game(self):
        """Initialise le jeu pour jouer à nouveau. """
        for row, row_content in enumerate(self._liste_coups):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row,col)
                self._jeu_gagnant = False
                self.combi_gagnante = []


class PlateaudeJeu(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Jeu du morpion")
        self._cases = {}
        self._jeu = game
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Jouer à nouveau ?",
                              command=self.reset_board
                              )
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=quit)
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(master=display_frame, text="Prêt ?", font=font.Font(size=28, weight="bold"), )
        self.display.pack()

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()

        for row in range(self._jeu.taille_plateau):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._jeu.taille_plateau):
                button = tk.Button(
                    master=grid_frame, text="", font=font.Font(size=36, weight="bold"), fg="black", width=3, height=1,
                    highlightbackground="lightblue", )
                self._cases[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew"
                            )

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._jeu.joueur_actuel.label)
        clicked_btn.config(fg=self._jeu.joueur_actuel.color)

    def play(self, event):
        """Gestion des mouvements des joueurs. """
        clicked_btn = event.widget
        row, col = self._cases[clicked_btn]
        move = Move(row, col, self._jeu.joueur_actuel.label)
        if self._jeu.is_valid_move(move):
            self._update_button(clicked_btn)
            self._jeu.process_move(move)
        if self._jeu.is_tied():
            self._update_display(msg="Egalité !", color="red")
        elif self._jeu.has_winner():
            self._highlight_cells()
            msg = f'Joueur "{self._jeu.joueur_actuel.label}" a gagné!'
            color = self._jeu.joueur_actuel.color
            self._update_display(msg, color)
        else:
            self._jeu.toggle_player()
            msg = f"{self._jeu.joueur_actuel.label} doit jouer."
            self._update_display(msg)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cases.items():
            if coordinates in self._jeu.combi_gagnante:
                button.config(highlightbackground="red")

    def reset_board(self):
        """Initialise le tableau de jeu pour Jouer à nouveau."""
        self._jeu.reset_game()
        self._update_display(msg="Prêt ?")
        for button in self._cases.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")


def main():
    """Crée leplateau de jeu et exécute sa boucle principale"""
    game = JeuduMorpion()
    board = PlateaudeJeu(game)
    board.mainloop()


if __name__ == "__main__":
    main()
