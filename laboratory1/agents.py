import logging

from typing import Literal

from mesa import Agent, Model
from mesa.agent import AgentSet
from mesa.space import MultiGrid

logger = logging.getLogger(__name__)


class TrendSpreadingAgent(Agent):
    '''
    Base class for agents in the trend spreading model.

    Attributes:
    model (Model): Reference to the Mesa model instance.
    grid (MultiGrid): Reference to the Mesa grid instance.
    type (str): Type of the agent, either 'RegularPerson' or 'SportInfluencer'.
    '''
    grid: MultiGrid | None
    model: Model
    _type: Literal['RegularPerson', 'SportInfluencer']

    def __init__(self, model: Model):
        super().__init__(model)
        self.grid: MultiGrid | None = model.grid
        self._type = 'RegularPerson' if isinstance(self, PersonAgent) else 'SportInfluencer'


    def introduce_self(self):
        '''
        Method introducing the agent.
        '''
        print(f'Hello, I am {self.type}. My unique id is {self.unique_id}.')


class PersonAgent(TrendSpreadingAgent):
    '''
    Agent represents a regular person that performs 2 actions:
    1. Move around the grid.
    2. Spread the news about a trend among other agents.

    Attributes:
    sport_enthusiast (bool): Indicates if the agent is a sport enthusiast.
    _knows_about_trend (bool): Indicates if the agent knows about the trend.
    _gossip_prob (float): Probability of the agent spreading the information.
    _skepticism_prob (float): Probability of the agent to follow the trend.
    '''
    sport_enthusiast: bool
    _knows_about_trend: bool
    _gossip_prob: float
    _skepticism_prob: float


    def __init__(self, model: Model, 
                 sport_enthusiast: bool=True,
                 knows_about_trend: bool=False,
                 gossip_prob: float=0.5,
                 skepticism_prob: float=0.2):
        super().__init__(model)
        
        self.sport_enthusiast = sport_enthusiast
        self._gossip_prob = gossip_prob
        self._knows_about_trend = knows_about_trend
        self._skepticism_prob = skepticism_prob


    @property
    def knows_about_trend(self) -> bool:
        '''
        Property indicating if the agent knows about the trend.
        '''
        return self._knows_about_trend
    

    def learn_about_trend(self, agent_id: str):
        '''
        Method that makes the agent learn about the trend.

        Attributes:
        agent_id (str): Unique ID of the agent that shared the trend.
        '''
        if self.random.random() < self._skepticism_prob:
            self._knows_about_trend = True
            logger.info(f'[{self.unique_id}] I learned about the trend from {agent_id}!')
        else:
            logger.warning(f'[{self.unique_id}] I am not going to follow the trend shared by {agent_id}.')


    def move_around(self):
        '''
        Method that moves the agent around the grid.
        Important! The grid must be initialized as part of the model under the variable with name 'grid'.
        '''
        self.check_grid_initialization(error_msg='The agent cannot move around the grid.')

        logger.info(f'[{self.unique_id}] My current position is {self.pos}.')

        possible_movements = self.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        self.grid.move_agent_to_one_of(self, list(possible_movements), handle_empty='error')


    def spread_news(self):
        '''
        Method that makes the agent spread the news among other agents encountered at the same grid cell.
        '''
        self.check_grid_initialization(error_msg='The agent cannot spread the news.')
        
        if self.knows_about_trend:
            encountered_agents = self.grid.get_cell_list_contents([self.pos])
            encountered_agents.pop(encountered_agents.index(self))

            for agent in encountered_agents:
                if not agent.knows_about_trend and \
                    (agent.sport_enthusiast or self.random.random() < self._gossip_prob):
                    agent.learn_about_trend(self.unique_id)
        else:
            logger.warning(f"[{self.unique_id}] I don't know anything that I could share.")
        
    
    def check_grid_initialization(self, error_msg: str = ''):
        '''
        Method that checks if the grid is initialized and raises an error with a custom message if not.

        Attributes:
        error_msg (str): Custom message to be displayed in the error.
        '''
        if self.grid is None:
            logger.error("Couldn't perform operation on the grid: {error_msg}.")
            raise ValueError(f'The grid has not been initialized: {error_msg}')
            

class InfluencerAgent(TrendSpreadingAgent):
    '''
    Agent represents a sport influencer that can spread the trend among their followers.
    '''

    def __init__(self, model):
        super().__init__(model)

    
    def spread_news_among_followers(self, followers: AgentSet):
        '''
        Method that makes the agent spread the news among their followers.
        Important! The grid must be initialized as part of the model under the variable with name 'grid'.
        '''
        for agent in followers:
            agent.learn_about_trend(self.unique_id)


    