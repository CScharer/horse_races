import json
import os
import random
import sys
sys.path.append("..")  # Replace with the actual path
import time
from enum import Enum
from typing import Optional
from pathlib import Path
from pydantic import BaseModel


def clear_console() -> None:
    command: str = "cls" if os.name in ("nt", "dos") else "clear"
    os.system(command)

class Sort(Enum):
    ASCENDING = "Ascending"
    DESCENDING = "Descending"
    RANDOM = "Random"
    
    
    def all():
        return [Sort.ASCENDING.value, Sort.DESCENDING.value, Sort.RANDOM.value]

    
class CardName(BaseModel):
    name: str
    number: int


class CardSuit(BaseModel):
    name: str
    image: str


class Card(BaseModel):
    card: CardName
    suit: CardSuit


class Horse(BaseModel):
    card: str
    pegs: int
    current_peg: int  = 0
    scratched: bool = False
    scratch_cost: float = 0.0
    percent: float = 0.0


class Player(BaseModel):
    name: str
    order: Optional[int] | None = None
    cards: Optional[list[Card] | None] = []
    paid: float | None = 0.0
    up_down: float | None = 0.0
    won: float | None = 0.0


def get_buffer(name: str) -> str:
    return (5 - len(name)) * " "


def get_dice_roll() -> int:
    # Generate a random integer between 1 and 6 (inclusive)
    return random.randint(1, 6)


def get_formatted_amount(amount: float) -> str:
    return f"${(amount):,.2f}"


def get_formatted_percent(amount: float) -> str:
    return f"{amount:,.0%}"


def get_random_card(cards: list[Card]) -> int:
    return random.randint(0, len(cards) - 1)


CARD_NAMES: list[CardName] = [
    CardName(name="2", number=2),
    CardName(name="3", number=3),
    CardName(name="4", number=4),
    CardName(name="5", number=5),
    CardName(name="6", number=6),
    CardName(name="7", number=7),
    CardName(name="8", number=8),
    CardName(name="9", number=9),
    CardName(name="10", number=10),
    CardName(name="J", number=11),
    CardName(name="Q", number=12),
]
CARD_SUITS: list[CardSuit] = [
    CardSuit(name="Clubs", image="♣️"),
    CardSuit(name="Diamonds", image="♦️"),
    CardSuit(name="Hearts", image="❤️"),
    CardSuit(name="Spades", image="♠️"),
]
CARDS: list[Card] = []
for suit in CARD_SUITS:
    for card in CARD_NAMES:
        CARDS.append(Card(card=CardName(name=card.name, number=card.number), suit=CardSuit(image=suit.image, name=suit.name)))
HORSES: dict = {
    2: Horse(card="2", pegs=2, current_peg=0),
    3: Horse(card="3", pegs=6, current_peg=0),
    4: Horse(card="4", pegs=8, current_peg=0),
    5: Horse(card="5", pegs=11, current_peg=0),
    6: Horse(card="6", pegs=14, current_peg=0),
    7: Horse(card="7", pegs=16, current_peg=0),
    8: Horse(card="8", pegs=14, current_peg=0),
    9: Horse(card="9", pegs=11, current_peg=0),
    10: Horse(card="10", pegs=8, current_peg=0),
    11: Horse(card="J", pegs=6, current_peg=0),
    12: Horse(card="Q", pegs=2, current_peg=0),
}
DEFAULT_BUY_IN: float = 2.00
DEFAULT_SCRATCHED_HORSE_COST: float = 0.25
DEFAULT_SCRATCHED_HORSE_ORDER: Sort = Sort.ASCENDING  # "ascending", "descending", "random"
IMAGE_PATH = Path("images")
IMAGE_FILES: list[Path] = [entry for entry in IMAGE_PATH.iterdir() if entry.is_file() and entry.suffix.lower() == '.png']
PLAYER_NAMES: list[str] = [str(image_file).replace("images/", "").replace(".png", "") for image_file in IMAGE_FILES]
PAYOUT_SPLIT: int = 4

class HorseGame():
    gui: any = None
    by_in: float = DEFAULT_BUY_IN
    cards: list[Card] = CARDS.copy()
    horses: list[Horse] = HORSES.copy()
    players: list[Player] = []
    die1: int = None
    die2: int = None
    roll: int = None
    horses_scratched: list[int] = []
    pot: float = 0.0
    finished: bool = False
    winning_horse: int = None
    def __init__(
            self,
            gui: any = None,
            by_in: float = DEFAULT_BUY_IN,
            scratched_horse_cost: float = DEFAULT_SCRATCHED_HORSE_COST,
            scratched_horse_order: Sort = 
            DEFAULT_SCRATCHED_HORSE_ORDER
            ) -> None:
        self.gui = gui
        self.by_in = by_in
        print(f"DEFAULT_BUY_IN: {DEFAULT_BUY_IN}, by_in: {self.by_in}")
        self.scratched_horse_cost = scratched_horse_cost
        self.scratched_horse_order = scratched_horse_order


    def reset(self) -> None:
        self.cards = CARDS
        self.horses = HORSES
        for player in self.players:
            player.cards = []
            player.paid = self.by_in
            player.up_down = player.paid * -1.0
            player.won = 0.0
        self.horses_scratched = []
        self.pot = (self.by_in * len(self.players))
        self.finished = False
        self.winning_horse = None


    def add_player(self, player: Player) -> None:
        order: int = len(self.players) + 1
        player.order = int(order)
        player.paid = self.by_in
        player.up_down = player.paid * -1.0
        self.pot += self.by_in
        self.players.append(player)


    def deal_cards(self, display: bool=False) -> None:
        cards_total: int = len(self.cards)
        cards_left: int = cards_total
        cards_dealt: int = 0
        message: str = ""
        while len(self.cards) > 0:
            for player in self.players:
                card_index: int = get_random_card(self.cards)
                card = self.cards.pop(card_index)
                cards_left = len(self.cards)
                cards_dealt += 1
                player.cards.append(card)
                # self.show_player(player)
                if display:
                    clear_console()
                    message = (
                        f"Cards: {cards_total}, Cards Dealt: {cards_dealt}, Cards Remaining: {cards_left}\n"
                        f"{player.name}{get_buffer(player.name)} was dealt a {card.card.name} of {card.suit.image}\n"
                    )
                    message += self.show_players()
                    print(message)
                    if self.gui:
                        self.gui.lbl.setText(message)
                        self.gui.update()
                    time.sleep(0.1)
                if len(self.cards) == 0:
                    return


    def get_amount_per_card(self) -> float:
        return int(self.pot) / PAYOUT_SPLIT


    def get_cards_for_player(self, player: Player) -> list[str]:
        # Sorts the cards by their number ascending and then by the first letter of their suit.name descending
        # sorted_cards = sorted(player.cards, key=lambda card: (card.card.number, -ord(card.suit_name[0])))
        # Sorts the cards by their number ascending and then by the first letter of their suit.name ascending
        # sorted_cards: list[Card] = sorted(player.cards, key=lambda card: (card.card.number, card.suit_name[0]))
        sorted_cards: list[Card] = sorted(player.cards, key=lambda card: (card.card.number, card.suit.name[0]))
        cards_list: list[str] = []
        cards_dict: dict = {}
        for card in sorted_cards:
            name = f" {card.card.name}"[-2:3]
            if name not in cards_dict:
                cards_dict[name] = []
            cards_dict[name].append(card.suit.image)
        for card_name, card_suits in cards_dict.items():
            if len(card_suits) == 1:
                cards_list.append(f"{card_name} {card_suits[0]}")
            else:
                cards_list.append(f"{card_name} [{' ,'.join(card_suits)} ]")
        return cards_list
    

    def get_place(self, peg: int) -> str:
        if peg == 1:
            return "1st"
        elif peg == 2:
            return "2nd"
        elif peg == 3:
            return "3rd"
        else:
            return f"{peg}th"
        

    def get_players_for_card(self, horse_card: str) -> list[str]:
        winners_list: list[str] = []
        for player in self.players:
            winning_cards: list[Card] = [card for card in player.cards if card.card.name == horse_card]
            if winning_cards:
                cards: str = ", ".join([f"{card.suit.image} " for card in winning_cards])
                winners_list.append(f"{player.name} {card.name}{cards}")
        return winners_list


    def play(self) -> None:
        while not self.finished:
            for player in self.players:
                # try_again: bool = True
                # while try_again:
                self.die1 = get_dice_roll()
                self.die2 = get_dice_roll()
                self.roll = self.die1 + self.die2
                # try_again = self.roll < 9
                horse: Horse = self.horses.get(self.roll)
                clear_console()
                roll_message: str = f"{player.name}{get_buffer(player.name)} rolled a {self.die1} and a {self.die2} totalling {self.roll}"
                if horse.scratched:
                    amount_to_pay: float = horse.scratch_cost
                    player.paid += amount_to_pay
                    player.up_down -= amount_to_pay
                    self.pot += amount_to_pay
                    roll_message += f" and has to pay {get_formatted_amount(amount_to_pay)} which brings the pot to {get_formatted_amount(self.pot)}"
                else:
                    horse.current_peg += 1
                    horse.percent = horse.current_peg / horse.pegs
                    if horse.current_peg == horse.pegs:
                        self.finished = True
                        self.winning_horse = self.roll
                    roll_message += (
                        f" and now horse #{horse.card} has won the race!!!" if self.finished else f" and now horse #{horse.card} is one peg closer to winning!"
                    )
                message: str = self.show_horses_scratched()
                message += f"\n{self.show_horses_standings()}"
                message += f"\n{self.show_players()}\n"
                message += f"\n{roll_message}"
                message += f"\n{self.show_pot()}"
                if horse.scratched:
                    message += "\nPlease pay the pot and press any key for the next player to roll."
                print(message)
                # if horse.scratched: input()
                if self.gui:
                    self.gui.lbl.setText(message)
                    self.gui.update()
                time.sleep(0.5)
                if self.finished:
                    clear_console()
                    self.show_winners()
                    message: str = self.show_horses_scratched()
                    message += f"\n{self.show_horses_standings()}"
                    message += f"\n{self.show_players()}\n"
                    message += f"\n{self.show_pot()}"
                    message += f"\n{roll_message}\n"
                    message += f"\n{self.show_winners()}"
                    print(message)
                    if self.gui:
                        self.gui.lbl.setText(message)
                        self.gui.update()
                    time.sleep(0.5)
                    return


    def remove_player(self, player_name: str) -> None:
        # Create a new list without the player to be removed
        self.players = [player for player in self.players if player.name != player_name]
        for i, player in enumerate(self.players):
            player.order = i + 1
        self.pot -= self.by_in


    def scratch_horses(self) -> None:
        scratch_costs: list[int] = [self.scratched_horse_cost * i for i in range(1, 5)]
        if self.scratched_horse_order == Sort.DESCENDING:
            scratch_costs.sort(reverse=True) and scratch_pegs.sort(reverse=True)
        elif self.scratched_horse_order == Sort.RANDOM:
            random.shuffle(scratch_costs)
        scratch_pegs: list[int] = [int(scratch_costs[i] / self.scratched_horse_cost * -1) for i in range(len(scratch_costs))]
        message: str = (
            f"Scratching horses with costs {scratch_costs} and pegs {scratch_pegs} "
            f"and order {self.scratched_horse_order}\n"
        )
        while len(self.horses_scratched) < PAYOUT_SPLIT:
            self.die1: int = get_dice_roll()
            self.die2: int = get_dice_roll()
            self.roll = self.die1 + self.die2
            if self.roll not in self.horses_scratched:
                self.horses_scratched.append(self.roll)
                horse: Horse = self.horses.get(self.roll)
                horse.scratched = True
                horse.scratch_cost = scratch_costs[len(self.horses_scratched) - 1]
                horse.current_peg = scratch_pegs[len(self.horses_scratched) - 1]
        message += self.show_horses_scratched()
        print(message)        
        if self.gui:
            self.gui.lbl.setText(message)
            self.gui.update()
        time.sleep(0.5)


    def show_horse(self, horse_id: int, horse: Horse) -> str:
        message: str = (
            f"horse #{horse_id} ({horse.card}) "
            f"has {horse.pegs} pegs "
            f"is currenlty at peg [{horse.current_peg} of {horse.pegs}] ({get_formatted_percent(horse.current_peg/horse.pegs)}) "
            f"and costs {get_formatted_amount(horse.scratch_cost)}"
            )
        return message


    def show_horses(self) -> None:
        horses: list[str] = []
        for horse_id in self.horses:
            horse: Horse = self.horses.get(horse_id)
            horses.append(self.show_horse(horse_id=horse_id, horse=horse))
        return f"Horses: {','.join(horses)}"


    def show_horses_scratched(self) -> str:
        message: str = f"Scratched Horses: {self.scratched_horse_order}\n"
        for horse_index in self.horses_scratched:
            horse: Horse = self.horses.get(horse_index)
            # message += f"{horse_index}={horse.card} ({get_formatted_amount(horse.scratch_cost)} [{'], ['.join((self.get_palyers_for_card(horse.card)))}])\n"
            message += f"-{self.get_place(horse.current_peg * -1)}={horse.card} {get_formatted_amount(horse.scratch_cost)} (peg {horse.current_peg}/{horse.pegs} {get_formatted_percent(horse.current_peg/horse.pegs)} [{'], ['.join((self.get_players_for_card(horse.card)))}])\n"
            # message += f"  #{horse_index} ({horse.card}) cost {get_formatted_amount(horse.scratch_cost)}\n"
        return message

    
    def show_horses_standings(self) -> str:
        # Get a list of horses that were not scratched.
        horses_racing: list[Horse] = [self.horses[horse_index] for horse_index in self.horses if not self.horses[horse_index].scratched]
        # Sort them descending so the closest to the finish line is first.
        horses_racing.sort(key=lambda horse: horse.percent, reverse=True)
        message: str = f"Horse Standings:\n"
        horse_index = 0
        for horse in horses_racing:
            horse_index += 1
            message += f"{self.get_place(horse_index)}={horse.card} (peg {horse.current_peg}/{horse.pegs} {get_formatted_percent(horse.current_peg/horse.pegs)} [{'], ['.join((self.get_players_for_card(horse.card)))}])\n"
        return message


    def show_player(self, player: Player) -> str:
        player_cards: list[str] = self.get_cards_for_player(player)
        up_down_even: str = "Up" if player.up_down > 0 else "Down" if player.up_down < 0 else "Even"
        message: str = (
            f"Player: [{player.name}]{get_buffer(player.name)} "
            f"[{player.order}] "
            f"Paid: [{get_formatted_amount(player.paid)}] "
            f"Wins: [{get_formatted_amount(player.won)}] "
            # f"Up: " if player.up_down > 0 else "Down: " if player.up_down < 0 else "Even: "
            # f" [{get_formatted_amount(player.up_down)}] "
            f"{up_down_even}: [{get_formatted_amount(player.up_down)}] "
            f"Cards: {' ,'.join(player_cards).strip()}"
        )
        return message


    def show_players(self) -> str:
        players: list[str] = []
        for player in self.players:
            players.append(self.show_player(player))
        return f"Players:\n{'\n'.join(players)}"


    def show_pot(self) -> str:
        amount_per_card = self.get_amount_per_card()
        remainder = (self.pot - (amount_per_card * PAYOUT_SPLIT))
        message: str = (
            f"The current pot is {get_formatted_amount(self.pot)}.  "
            f"Split {PAYOUT_SPLIT} ways that is {get_formatted_amount(amount_per_card)} per card "
            f"with a remainded of {get_formatted_amount(remainder)}"
            )
        return message


    def show_winners(self) -> str:
        winners_dict: dict = {}
        message: str = "Winners:\n"
        for player in self.players:
            cards: list[Card] = player.cards
            winnings: float = 0.0
            for card in cards:
                if card.card.number == self.winning_horse:
                    winning_card: Card = Card(card=card.card, suit=card.suit)
                    if player.name in winners_dict:
                        players_cards: list[Card] = winners_dict[player.name].get("cards", [])
                        players_cards.append(winning_card)
                        winners_dict[player.name]["cards"] = players_cards
                    else:
                        winners_dict[player.name] = {"cards": [winning_card]}
                    winnings = (self.get_amount_per_card() * len(winners_dict[player.name]["cards"]))
                    player.won = winnings
            player.up_down = winnings - player.paid
        # message += (f"Winners: [{'], ['.join((self.get_palyers_for_card(self.horses[self.winning_horse].card)))}]")
        # print(winners_dict)
        for winner in winners_dict:
            winnder_cards: list[Card] = winners_dict[winner].get("cards", [])
            winner_card_count = len(winnder_cards)
            cards_display: list[str] = [f"{card.suit.image}" for card in winnder_cards]
            winner_percent: float = get_formatted_percent((winner_card_count / PAYOUT_SPLIT))
            winner_amount: float = get_formatted_amount((winner_card_count * self.get_amount_per_card()))
            message += (
                f"{winner} has {winner_card_count} cards: {card.card.name}[{' , '.join(cards_display)} ] "
                f"and wins {winner_percent} of the pot "
                f"or {winner_amount}.\n"
            )
        return message


if __name__ == '__main__':    
    clear_console()
    # horse_game = HorseGame()
    horse_game = HorseGame(by_in=2.0, scratched_horse_cost=0.25, scratched_horse_order=Sort.RANDOM)    
    for player in PLAYER_NAMES:
        horse_game.add_player(player=Player(name=player))
    # horse_game.remove_player(player_name="Chris")
    horse_game.deal_cards(display=True)
    horse_game.scratch_horses()
    horse_game.show_horses_scratched()
    horse_game.play()
    # horse_game.show_winners()
    # horse_game.show_horses()
    # horse_game.show_players()
    # horse_game.show_pot()
