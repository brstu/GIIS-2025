import secrets
import tkinter as tk
from tkinter import messagebox

suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
          'J': 10, 'Q': 10, 'K': 10, 'A': 11}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.name = f"{suit}{rank}"
        self.value = values[rank]

    def __str__(self):
        return self.name

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.shuffle_deck()

    def shuffle_deck(self):
        secrets.SystemRandom().shuffle(self.cards)

    def deal_card(self, high_only=False):
        if high_only:
            high_cards = [card for card in self.cards if card.value >= 10]
            if high_cards:
                card = secrets.choice(high_cards)
                self.cards.remove(card)
                return card
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def __str__(self):
        return ' '.join(str(card) for card in self.cards)

class BlackjackGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")

        self.initial_money = 1050
        self.money = self.initial_money
        self.bet = 100

        self.init_ui()
        self.reset_game_ui()

    def init_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.money_label = tk.Label(self.frame, text=f"Баланс: {self.money} монет")
        self.money_label.grid(row=0, column=0, columnspan=3, sticky='w')

        self.bet_entry = tk.Entry(self.frame)
        self.bet_entry.insert(0, str(self.bet))
        self.bet_entry.grid(row=1, column=0)
        self.bet_button = tk.Button(self.frame, text="Сделать ставку", command=self.start_game)
        self.bet_button.grid(row=1, column=1)

        self.new_game_button = tk.Button(self.frame, text="Новая игра", command=self.reset_game_ui)
        self.new_game_button.grid(row=1, column=2)

        self.player_label = tk.Label(self.frame, text="Твои карты:")
        self.player_label.grid(row=2, column=0, sticky='w')
        self.player_cards = tk.Label(self.frame, text="")
        self.player_cards.grid(row=2, column=1, columnspan=2, sticky='w')

        self.dealer_label = tk.Label(self.frame, text="Карты дилера:")
        self.dealer_label.grid(row=3, column=0, sticky='w')
        self.dealer_cards = tk.Label(self.frame, text="")
        self.dealer_cards.grid(row=3, column=1, columnspan=2, sticky='w')

        self.result_label = tk.Label(self.frame, text="", font=('Arial', 12, 'bold'), fg='blue')
        self.result_label.grid(row=4, column=0, columnspan=3)

        self.hit_button = tk.Button(self.frame, text="Hit", command=self.hit)
        self.hit_button.grid(row=5, column=0)
        self.stand_button = tk.Button(self.frame, text="Stand", command=self.stand)
        self.stand_button.grid(row=5, column=1)
        self.luck_button = tk.Button(self.frame, text="Luck (-150)", command=self.luck)
        self.luck_button.grid(row=5, column=2)
        self.double_button = tk.Button(self.frame, text="Удвоить выигрыш (-300)", command=self.double_win)
        self.double_button.grid(row=6, column=1)

    def reset_game_ui(self):
        self.money = self.initial_money
        self.money_label.config(text=f"Баланс: {self.money} монет")
        
        self.player_cards.config(text="")
        self.dealer_cards.config(text="")
        self.result_label.config(text="")
        self.hit_button.config(state='disabled')
        self.stand_button.config(state='disabled')
        self.luck_button.config(state='disabled')
        self.double_button.config(state='disabled')
        self.bet_button.config(state='normal')
        self.bet_entry.config(state='normal')

    def start_game(self):
        self.result_label.config(text="")
        try:
            self.bet = int(self.bet_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Ставка должна быть числом")
            return

        if self.money < self.bet:
            messagebox.showerror("Ошибка", "Недостаточно средств")
            return

        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.luck_used = False
        self.double_used = False

        self.money -= self.bet
        self.money_label.config(text=f"Баланс: {self.money} монет")

        self.player_hand.add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())

        self.update_ui()

        self.hit_button.config(state='normal')
        self.stand_button.config(state='normal')
        self.luck_button.config(state='normal')
        self.double_button.config(state='normal')
        self.bet_button.config(state='disabled')
        self.bet_entry.config(state='disabled')

    def update_ui(self, reveal_dealer=False):
        self.player_cards.config(text=str(self.player_hand) + f" (Сумма: {self.player_hand.get_value()})")
        if reveal_dealer:
            self.dealer_cards.config(text=str(self.dealer_hand) + f" (Сумма: {self.dealer_hand.get_value()})")
        else:
            dealer_card = self.dealer_hand.cards[0] if self.dealer_hand.cards else ''
            self.dealer_cards.config(text=str(dealer_card))

        self.money_label.config(text=f"Баланс: {self.money} монет")
        self.root.update_idletasks()

    def hit(self):
        self.player_hand.add_card(self.deck.deal_card())
        self.update_ui()
        if self.player_hand.get_value() > 21:
            self.end_game("Перебор! Ты проиграл.", reveal_dealer=True)

    def stand(self):
        self.hit_button.config(state='disabled')
        self.stand_button.config(state='disabled')
        self.root.after(1000, self.dealer_turn)

    def dealer_turn(self):
        if self.dealer_hand.get_value() < 17:
            self.dealer_hand.add_card(self.deck.deal_card())
            self.update_ui(reveal_dealer=True)
            self.root.after(1000, self.dealer_turn)
        else:
            self.finish_game()

    def finish_game(self):
        self.update_ui(reveal_dealer=True)
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()

        if dealer_value > 21 or player_value > dealer_value:
            winnings = self.bet * 2
            if self.double_used:
                winnings *= 2
            self.money += winnings
            self.end_game("Ты выиграл!", reveal_dealer=True)
        elif player_value < dealer_value:
            self.end_game("Ты проиграл.", reveal_dealer=True)
        else:
            self.money += self.bet
            self.end_game("Ничья.", reveal_dealer=True)

    def end_game(self, message, reveal_dealer=False):
        self.update_ui(reveal_dealer)
        self.result_label.config(text=message)
        self.hit_button.config(state='disabled')
        self.stand_button.config(state='disabled')
        self.luck_button.config(state='disabled')
        self.double_button.config(state='disabled')
        self.bet_button.config(state='normal')
        self.bet_entry.config(state='normal')
        if self.money <= 0:
            messagebox.showinfo("Конец игры", "У тебя закончились монеты. Игра перезапускается.")
            self.money = self.initial_money
            self.money_label.config(text=f"Баланс: {self.money} монет")
        self.root.update_idletasks()

    def luck(self):
        if self.luck_used:
            messagebox.showinfo("Инфо", "Ты уже использовал удачу в этом раунде.")
            return
        if self.money < 150:
            messagebox.showinfo("Инфо", "Недостаточно монет для удачи.")
            return
        self.money -= 150
        self.luck_used = True
        self.player_hand.add_card(self.deck.deal_card(high_only=True))
        self.update_ui()
        if self.player_hand.get_value() > 21:
            self.end_game("Перебор! Ты проиграл.", reveal_dealer=True)

    def double_win(self):
        if self.double_used:
            messagebox.showinfo("Инфо", "Ты уже удваивал выигрыш в этом раунде.")
            return
        if self.money < 300:
            messagebox.showinfo("Инфо", "Недостаточно монет для удвоения.")
            return
        self.money -= 300
        self.double_used = True
        self.money_label.config(text=f"Баланс: {self.money} монет")

if __name__ == '__main__':
    root = tk.Tk()
    game = BlackjackGame(root)
    root.mainloop()
