from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import numpy as np
import random
#from otree_tools.models.fields import ListField

author = 'Salvatore Nunnari, Bocconi University'

doc = """
Dynamic legislative bargaining with three players and endogenous status quo
as in Battaglini, Marco and Thomas R. Palfrey, 2012, "The Dynamics of Distributive Politics"
or in Nunnari, 2019, "Veto Power in Standing Committees: An Experimental Study".
This app implements multiple instances of an infinitely repeated game (i.e., multiple "matches").
"""


class Constants(BaseConstants):
    name_in_url = 'dbarg_multiple'
    players_per_group = 3
    match_duration = np.random.geometric(p=0.25, size=10) # the first argument here is the probability the match ends after each round (i.e., 1 - \delta); the second argument is the number of matches. For documentation, see: https://docs.scipy.org/doc/numpy/reference/generated/numpy.random.geometric.html
    num_rounds = np.sum(match_duration)
    last_rounds = np.cumsum(match_duration)
    first_rounds = [1]
    for k in range(1, len(match_duration)):
        first_rounds.append(int(last_rounds[k - 1] + 1))
    budget = 60 # number of tokens to divide among committee members
    veto = False  # set to "True" for game with one veto player, set to "False" for game without veto players
    q = 2  # number of positive votes required for passage (if veto = True, this includes the veto player)
    rec_prob_1 = 1/3 # recognition probability of group member 1; if veto = True, this is the veto player
    rec_prob_2 = 1/3 # recognition probability of group member 2
    rec_prob_3 = 1/3 # recognition probability of group member 3
    die_roll_threshold = 75 # only used in end-of-round template

class Subsession(BaseSubsession):

    match_number = models.IntegerField()
    round_in_match_number = models.IntegerField()

    def creating_session(self):

        k = 0
        while k < len(Constants.last_rounds):
            if self.round_number <= Constants.last_rounds[k]:
                self.match_number = k + 1
                k = len(Constants.last_rounds)
            else:
                k += 1

        self.round_in_match_number = self.round_number - Constants.first_rounds[self.match_number-1] + 1


        if self.round_number == 1:
            players = self.get_players()
            for p in players:
                if p.id_in_group == 1:
                    p.participant.vars['type'] = 'Veto'
                else:
                    p.participant.vars['type'] = 'Non-Veto'

            groups = self.get_groups()
            for g in groups:

                # determine identity of proposer in this round
                rand_num_prop = np.random.random()
                if rand_num_prop <= Constants.rec_prob_1:
                    g.proposer = 1
                elif rand_num_prop > Constants.rec_prob_1 and rand_num_prop <= Constants.rec_prob_1 + Constants.rec_prob_2:
                    g.proposer = 2
                else:
                    g.proposer = 3
                # g.proposer = np.random.randint(1, 4) # alternative way to randomly determine proposer with even probabilities

                # determine initial status quo in this match (draw one random vector of three integers which sum to budget)
                sq = [0,0,0]
                sq[0] = np.random.randint(0, Constants.budget + 1)  # return random integer from low (inclusive) to high (exclusive)
                if sq[0] < Constants.budget:
                    sq[1] = np.random.randint(0, Constants.budget + 1 - sq[0])
                else:
                    sq[1] = 0
                sq[2] = Constants.budget - sq[0] - sq[1]
                np.random.shuffle(sq) # this command shuffles sq vector in place; to store shuffled vector use sq_shuffled = random.sample(sq, len(sq))
                g.sq_to_1 = sq[0]
                g.sq_to_2 = sq[1]
                g.sq_to_3 = sq[2]

        elif self.round_number > 1 and self.round_number in Constants.first_rounds:

            #shuffle groups; each group has 1 veto player and 2 non-veto players; roles are fixed throughout the whole session
            players = self.get_players()
            random.shuffle(players)
            veto_players = [p for p in players if p.participant.vars['type'] == 'Veto']
            nonveto_players = [p for p in players if p.participant.vars['type'] == 'Non-Veto']
            group_matrix = []
            num_groups = int(len(players) / Constants.players_per_group)
            # Note that by this construction veto players are ID 1, non-veto players are ID 2 and 3
            for i in range(num_groups):
                new_group = [
                    veto_players.pop(),
                    nonveto_players.pop(),
                    nonveto_players.pop(),
                ]
                group_matrix.append(new_group)
            self.set_groups(group_matrix)

            groups = self.get_groups()
            for g in groups:

                # determine identity of proposer in this round
                rand_num_prop = np.random.random()
                if rand_num_prop <= Constants.rec_prob_1:
                    g.proposer = 1
                elif rand_num_prop > Constants.rec_prob_1 and rand_num_prop <= Constants.rec_prob_1 + Constants.rec_prob_2:
                    g.proposer = 2
                else:
                    g.proposer = 3
                # g.proposer = np.random.randint(1, 4) # alternative way to randomly determine proposer with even probabilities

                # determine initial status quo in this match (draw one random vector of three integers which sum to budget)
                sq = [0,0,0]
                sq[0] = np.random.randint(0, Constants.budget + 1)  # return random integer from low (inclusive) to high (exclusive)
                if sq[0] < Constants.budget:
                    sq[1] = np.random.randint(0, Constants.budget + 1 - sq[0])
                else:
                    sq[1] = 0
                sq[2] = Constants.budget - sq[0] - sq[1]
                np.random.shuffle(sq) # this command shuffles sq vector in place; to store shuffled vector use sq_shuffled = random.sample(sq, len(sq))
                g.sq_to_1 = sq[0]
                g.sq_to_2 = sq[1]
                g.sq_to_3 = sq[2]

        else:

            groups = self.get_groups()
            for g in groups:

                # determine identity of proposer in this round
                rand_num_prop = np.random.random()
                if rand_num_prop <= Constants.rec_prob_1:
                    g.proposer = 1
                elif rand_num_prop > Constants.rec_prob_1 and rand_num_prop <= Constants.rec_prob_1 + Constants.rec_prob_2:
                    g.proposer = 2
                else:
                    g.proposer = 3
                # g.proposer = np.random.randint(1, 4) # alternative way to randomly determine proposer with even probabilities

class Group(BaseGroup):

    sq_to_1 = models.IntegerField(null=True)
    sq_to_2 = models.IntegerField(null=True)
    sq_to_3 = models.IntegerField(null=True)
    proposer = models.IntegerField()
    chosen_offer_to_1 = models.IntegerField()
    chosen_offer_to_2 = models.IntegerField()
    chosen_offer_to_3 = models.IntegerField()
    outcome = models.CharField()
    allocation_to_1 = models.IntegerField()
    allocation_to_2 = models.IntegerField()
    allocation_to_3 = models.IntegerField()

class Player(BasePlayer):

    offer_to_1 = models.IntegerField(
        max=Constants.budget,
        min=0
    )
    offer_to_2 = models.IntegerField(
        max=Constants.budget,
        min=0
    )
    offer_to_3 = models.IntegerField(
        max=Constants.budget,
        min=0
    )

    vote = models.CharField(
        choices=['Proposal', 'Status Quo'],
        verbose_name='What allocation do you vote for?',
        widget=widgets.RadioSelect
    )

    vote_for_sq = models.IntegerField()

    def role(self):
        if self.id_in_group == 1:
            return 'Veto'
        else:
            return 'Non-Veto'