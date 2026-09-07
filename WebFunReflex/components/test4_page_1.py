import random
import math

import reflex as rx

import statemachine as sm

from functional.statemachine import rxState, StateMachine


MIN_RANGE: int = 0
MAX_RANGE: int = 100

MAX_ATTEMPTS: int = int(1.5 * math.log2(MAX_RANGE - MIN_RANGE))


class GuessTheNumberSM(StateMachine):
	"""State machine for the enhanced 'Guess the Number' game."""
	rx_state: rx.State = None

	# States
	idle: sm.State = sm.State(initial=True, value="Idle")
	is_higher: sm.State = sm.State(value="Higher")
	is_lower: sm.State = sm.State(value="Lower")
	mini_game: sm.State = sm.State(value="MiniGame")
	won: sm.State = sm.State(value="Won")
	lost: sm.State = sm.State(value="Lost")

	# Transitions
	_higher = (
		idle.to(is_higher)
		| is_lower.to(is_higher)  # noqa: W503
	)


class GameState(rxState, rx.State):
	"""State for the enhanced game."""
	_game_sm: GuessTheNumberSM = GuessTheNumberSM()
	target_number: int = random.randint(MIN_RANGE, MAX_RANGE)
	attempts_left: int = MAX_ATTEMPTS
	current_guess: int = (MAX_RANGE - MIN_RANGE) // 2
	hint: str = "??"  # Whether the player has a hint token
	finished: bool = False  # Result of the mini-game

	@rx.var
	def current_state(self) -> str:
		return self._game_sm.current_state_value

	def start_game(self):
		"""Initialize the game."""
		self._game_sm.start_game()
		self.target_number = random.randint(MIN_RANGE, MAX_RANGE)
		self.attempts_left = MAX_ATTEMPTS
		self.current_guess = MAX_ATTEMPTS // 2
		self.hint_token = False
		self.finished = False

		self._game_sm.begin_playing()

	def make_guess(self, guess: int):
		"""Process a guess."""
		self.current_guess = guess
		self.attempts_left -= 1

		if guess == self.target_number:
			self._game_sm._win_game()
		elif self.attempts_left <= 0:
			self._game_sm._lose_game()

	def gen_hint(self):
		"""Generate a hint."""
		if self.hint == "??":
			self.hint = "Higher" if self.current_guess < self.target_number else "Lower"
		return self.hint

	def reset_game(self):
		"""Reset the game."""
		self._game_sm.reset_game()


def gen_page_1(main_state: type) -> rx.Component:
	"""Generate the enhanced game page."""
	return rx.vstack(
		rx.heading(f"Guess the Number from {MIN_RANGE} to {MAX_RANGE}", size="6"),
		rx.text(f"State: {GameState.current_state}", font_weight="bold"),
		rx.cond(
			GameState.current_state == "Idle",
			rx.vstack(
				rx.text("Welcome to the enhanced game!"),
				rx.button("Start Game", on_click=GameState.start_game),
				spacing="3",
			),
		),
		rx.cond(
			GameState.current_state == "Playing",
			rx.vstack(
				rx.text(
					f"Guess a number between {GameState.min_range} "
					f"and {GameState.max_range}"
				),
				rx.text(f"Attempts left: {GameState.attempts_left}"),
				rx.input(
					placeholder="Your guess",
					type="number",
					on_change=lambda val: GameState.make_guess(int(val)),
				),
				rx.cond(
					GameState.hint_token,
					rx.text(f"Hint: {GameState.use_hint_token()}"),
					rx.text("Play the mini-game to earn a hint token!"),
				),
				spacing="3",
			),
		),
		rx.cond(
			GameState.current_state == "MiniGame",
			rx.vstack(
				rx.text("Quick! Press the button in time!"),
				rx.button(
					"Click Me!",
					on_click=GameState.play_mini_game,
					color_scheme="green" if GameState.mini_game_success else "red",
				),
				spacing="3",
			),
		),
		rx.cond(
			GameState.current_state == "Won",
			rx.vstack(
				rx.text("Congratulations! You won!"),
				rx.text(f"The number was {GameState.target_number}"),
				rx.button("Play Again", on_click=GameState.reset_game),
				spacing="3",
			),
		),
		rx.cond(
			GameState.current_state == "Lost",
			rx.vstack(
				rx.text("Game Over! You ran out of attempts."),
				rx.text(f"The number was {GameState.target_number}"),
				rx.button("Try Again", on_click=GameState.reset_game),
				spacing="3",
			),
		),
		spacing="4",
	)
