from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import random

class Proposal(Page):
    #def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
    #    return self.session.vars['alive'] == True

    form_model = 'player'
    form_fields = ['offer_to_1','offer_to_2','offer_to_3']

    def error_message(self, values):
      if values['offer_to_1'] + values['offer_to_2'] + values['offer_to_3'] != Constants.budget:
                    return 'Your provisional allocation proposal must add up to {}'.format(Constants.budget)

class ProposalWaitPage(WaitPage):
    #def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
    #    return self.session.vars['alive'] == True

    def after_all_players_arrive(self):
        group = self.group
        players = group.get_players()
        if group.proposer == 1:
            group.chosen_offer_to_1 = group.get_player_by_id(1).offer_to_1
            group.chosen_offer_to_2 = group.get_player_by_id(1).offer_to_2
            group.chosen_offer_to_3 = group.get_player_by_id(1).offer_to_3
        elif group.proposer == 2:
            group.chosen_offer_to_1 = group.get_player_by_id(2).offer_to_1
            group.chosen_offer_to_2 = group.get_player_by_id(2).offer_to_2
            group.chosen_offer_to_3 = group.get_player_by_id(2).offer_to_3
        else:
            group.chosen_offer_to_1 = group.get_player_by_id(3).offer_to_1
            group.chosen_offer_to_2 = group.get_player_by_id(3).offer_to_2
            group.chosen_offer_to_3 = group.get_player_by_id(3).offer_to_3

class Vote(Page):
    #def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
    #    return self.session.vars['alive'] == True

    form_model = 'player'
    form_fields = ['vote']

class VoteWaitPage(WaitPage):
    #def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
    #    return self.session.vars['alive'] == True

    def after_all_players_arrive(self):
        group = self.group
        players = group.get_players()
        for p in players:
            if p.vote == "Status Quo":
                p.vote_for_sq = 1
            else:
                p.vote_for_sq = 0
        veto_votes_for_sq = group.get_player_by_role('Veto').vote_for_sq
        votes_for_sq = [p.vote_for_sq for p in players]

        if Constants.veto == True and sum(votes_for_sq) < Constants.q and veto_votes_for_sq == 0:
            group.outcome = "Proposal"
            group.allocation_to_1 = group.chosen_offer_to_1
            group.allocation_to_2 = group.chosen_offer_to_2
            group.allocation_to_3 = group.chosen_offer_to_3
        elif Constants.veto == False and sum(votes_for_sq) < Constants.q:
            group.outcome = "Proposal"
            group.allocation_to_1 = group.chosen_offer_to_1
            group.allocation_to_2 = group.chosen_offer_to_2
            group.allocation_to_3 = group.chosen_offer_to_3
        else:
            group.outcome = "Status Quo"
            group.allocation_to_1 = group.sq_to_1
            group.allocation_to_2 = group.sq_to_2
            group.allocation_to_3 = group.sq_to_3

        for p in players:
            if p.id_in_group==1:
                p.payoff = group.allocation_to_1
            elif p.id_in_group==2:
                p.payoff = group.allocation_to_2
            else:
                p.payoff = group.allocation_to_3

        if self.round_number < Constants.num_rounds:
            group.in_round(self.round_number + 1).sq_to_1 = group.allocation_to_1
            group.in_round(self.round_number + 1).sq_to_2 = group.allocation_to_2
            group.in_round(self.round_number + 1).sq_to_3 = group.allocation_to_3

class Results(Page):
    #def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
    #    return self.session.vars['alive'] == True
    timeout_seconds = 30

    def vars_for_template(self):
        return {
            'vote1': self.group.get_player_by_id(1).vote,
            'vote2': self.group.get_player_by_id(2).vote,
            'vote3': self.group.get_player_by_id(3).vote,
        }

class ResultsWaitPage(WaitPage):
    pass
    #def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
    #    return self.session.vars['alive'] == True
    #def after_all_players_arrive(self):
    #    self.session.vars['random'] = random.uniform(0, 1)
    #    if self.session.vars['random'] > Constants.discount:
    #        self.session.vars['alive'] = False

class EndRound(Page):
    timeout_seconds = 30
#    def is_displayed(self): # alternative way to implement an infinitely repeated game in the laboratory
#        return self.session.vars['alive'] == False
#    def is_displayed(self):
#        return self.round_number == Constants.num_rounds

page_sequence = [
    Proposal,
    ProposalWaitPage,
    Vote,
    VoteWaitPage,
    Results,
    ResultsWaitPage,
    EndRound
]
