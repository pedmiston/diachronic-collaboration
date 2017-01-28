import pandas

from landscapes.graph_db import connect_to_graph_db

class Landscape:
    def __init__(self):
        """Copies the landscape for faster lookups."""
        self.graph = connect_to_graph_db()
        recipes = pandas.DataFrame(self.graph.data("""
        MATCH (recipe) -[:CREATES]-> (result:Item)
        MATCH (result) -[:INHERITS]-> (requirement:Item)
        RETURN result.label as result,
               requirement.label as requirement;
        """))
        self.answer_key = {}
        for result, chunk in recipes.groupby('result'):
            requirements = frozenset(chunk.requirement.tolist())
            self.answer_key[requirements] = result

        self.max_items = self.graph.data("""
        MATCH (n:Item)
        RETURN count(n) as n_items
        """)[0]['n_items']  # graph.data always returns a list

        self.adjacent_recipes = {}

    def evaluate(self, guess):
        return self.answer_key.get(frozenset(guess))

    def evaluate_guesses(self, guesses):
        new_items = {}
        for guess in guesses:
            result = self.evaluate(guess)
            if result:
                new_items[frozenset(guess)] = result
        return new_items

    def determine_adjacent_possible(self, inventory):
        """Return a set of recipes obtainable with the given inventory."""
        inv = frozenset(inventory)
        if inv not in self.adjacent_recipes:
            self.adjacent_recipes[inv] = self._adjacent_possible(inv)
        return self.adjacent_recipes[inv]

    def _adjacent_possible(self, inventory):
        adjacent_query = """
        MATCH (n:Item) <-[:REQUIRES]- (r:Recipe)
        WHERE n.label IN {inventory}
        RETURN r.code as code
        """.format(inventory=list(inventory))
        adjacent_recipes = pandas.DataFrame(self.graph.data(adjacent_query))

        requirements_query = """
        MATCH (r:Recipe) -[:REQUIRES]-> (n:Item)
        WHERE r.code IN {codes}
        RETURN r.code as code, n.label as requirement
        """.format(codes=adjacent_recipes.code.tolist())
        requirements = pandas.DataFrame(self.graph.data(requirements_query))

        adjacent_possible = []
        for code, chunk in requirements.groupby('code'):
            if all(chunk.requirement.isin(inventory)):
                adjacent_possible.append(code)

        return adjacent_possible
