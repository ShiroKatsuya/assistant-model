from typing import NamedTuple
import utils
from reasoners import WorldModel, LanguageModel
from world_model import BWState, BWAction
from reasoners import SearchConfig, LanguageModel
import copy

BWState = str
BWAction = str

class BlocksWorldModel(WorldModel[BWState, BWAction]):
    def __init__(self,
                 base_model: LanguageModel,
                 prompt: dict) -> None:
        super().__init__()
        self.base_model = base_model
        self.prompt = prompt

    def init_state(self) -> BWState:
        # extract the statement from a given problem
        # e.g., "the red block is clear, the blue block is clear..."
        return BWState(utils.extract_init_state(self.example)) 

    def step(self, state: BWState, action: BWAction) -> tuple[BWState, dict]:
        # call the LLM to predict the state transition
        state = copy.deepcopy(state)
        # load the prompt for the LLM to predict the next state
        # e.g. "... I have that <state>, if I <action>, then ..."
        world_update_prompt = self.prompt["update"].replace("<state>", state).replace("<action>", action)
        world_output = self.base_model.generate([world_update_prompt],
                                    eos_token_id="\n", hide_input=True, temperature=0).text[0].strip()
        new_state = utils.process_new_state(world_output)
        # till now, we have the new state after the action
        # the following part is to speed up the reward calculation

        # we want to check the portion of the satisfied subgoals, and use it as a part of the reward
        # since we have predicted the new state already, we can just check it here at convenience
        goal_reached = utils.goal_check(utils.extract_goals(self.example, new_state))
        # return the new state and the additional dictionary (to be passed to the reward function)
        return new_state, {"goal_reached": goal_reached}

    def is_terminal(self, state: BWState) -> bool:
        # define the condition the terminal state to stop the search
        # e.g., all the subgoals are met
        if utils.goal_check(utils.extract_goals(self.example), state.blocks_state) == 1:
            return True
        return False
    
