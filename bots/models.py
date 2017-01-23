import numpy

MAX_GUESS_SIZE = 4


def create_team(n_players=1, seed=None, player_memory=False, team_memory=False):
    rand = numpy.random.RandomState(seed)
    players = [Player(rand, memory=player_memory) for _ in range(n_players)]
    return Team(players, memory=team_memory)


class Team:
    """Teams are groups of 1 or more players."""
    def __init__(self, players, memory=True):
        """Create a team from a list of players.

        Team memory records successful guesses from any of
        the team's players so they are not guessed again.
        """
        self.players = players
        self.active_players = []  # Players must be activated to use

        # Set the initial inventory for the team
        self.inventory = {'Big_Tree', 'Tree', 'Stone',
                          'Red_Berry', 'Blue_Berry', 'Antler'}

        # Control team memory
        self.is_memory_on = memory
        self.successful_guesses = []

    def make_guesses(self):
        return [player.guess_new(self.inventory, self.successful_guesses)
                for player in self.active_players]

    def update_inventory(self, new_items):
        self.inventory.update(set(new_items.values()))
        if self.is_memory_on:
            self.add_guesses_to_memory(new_items.keys())

    def add_guesses_to_memory(self, guesses):
        for guess in guesses:
            guess = set(guess)  # just to be sure
            if guess not in self.successful_guesses:
                self.successful_guesses.append(guess)


class Player:
    """Players make guesses."""
    def __init__(self, rand=None, memory=False):
        """Create a player from a random state.

        Player memory records a player's guesses and never
        guesses the same combination twice.
        """
        self.rand = rand or numpy.random.RandomState()
        self.is_memory_on = memory
        self.personal_memory = []

    def guess_new(self, inventory, team_guesses=None):
        """Keep guessing until one is found that isn't in past guesses."""
        team_guesses = team_guesses or []
        past_guesses = team_guesses + self.personal_memory

        while True:
            guess = self.guess(inventory)
            if guess not in past_guesses:
                break

        if self.is_memory_on:
            self.personal_memory.append(guess)

        return guess

    def guess(self, inventory):
        n_items = self.pick_guess_size()
        guess = self.rand.choice(list(inventory), size=n_items, replace=False)
        return set(guess)

    def pick_guess_size(self):
        return self.rand.choice(range(1, MAX_GUESS_SIZE+1))
