import logging

from mesa import Model
from mesa.space import MultiGrid

from agents import PersonAgent, InfluencerAgent

logger = logging.getLogger(__name__)


class TrendSpreadModel(Model):
    '''
    Model class that simulates the spread of a trend in a population.

    Attributes:
    population_size (int): Total number of agents in the model.
    influencer_group_size (int): Number of influencer agents in the model.
    grid_width (int): Width of the grid.
    grid_height (int): Height of the grid.
    seed (int): Seed for random number generation.
    '''
    population_size: int
    influencer_group_size: int
    grid_width: int
    grid_height: int
    seed: int


    def __init__(self, 
                 population_size: int = 5, 
                 influencer_group_size: int = 1,
                 grid_width: int = 10, 
                 grid_height: int = 10, 
                 seed=None):
        super().__init__(seed=seed)
        self.population_size = population_size
        self.influencer_group_size = influencer_group_size

        self.grid = MultiGrid(grid_width, grid_height, True)

        self.generate_person_agents()
        self.generate_influencer_agents()


    def generate_person_agents(self):
        '''
        Method generates regular person agents and places them on the grid.
        '''
        sport_enthusiasts = self.random.randint(1, self.population_size)
        non_sport_enthusiasts = self.population_size - sport_enthusiasts

        PersonAgent.create_agents(self, sport_enthusiasts, sport_enthusiast=True, knows_about_trend=False)
        PersonAgent.create_agents(self, non_sport_enthusiasts, sport_enthusiast=False, knows_about_trend=False)
        PersonAgent(self, sport_enthusiast=True, knows_about_trend=True)
        self.population_size += 1

        self.place_agents_on_grid()

    
    def generate_influencer_agents(self):
        '''
        Method generates influencer agents.
        Important! These agents do not operate on the grid!
        '''
        InfluencerAgent.create_agents(self, self.influencer_group_size)


    def place_agents_on_grid(self):
        '''
        Method that randomly places agents on the grid.
        '''
        x_range = self.rng.integers(0, self.grid.width, size=(self.population_size,))
        y_range = self.rng.integers(0, self.grid.height, size=(self.population_size,))

        for agent, x_coord, y_coord in zip(self._agents_by_type[PersonAgent], x_range, y_range):
            self.grid.place_agent(agent, (x_coord, y_coord))


    def _stop_condition(step) -> None:
        '''
        Method that checks if the simulation should stop.
        '''
        def perform_step(self):
            if len(self._agents_by_type[PersonAgent].select(lambda agent: not agent.knows_about_trend)) == 0:
                self.running = False
                logger.info("All agents know about the trend. Stopping the simulation.")
            else:
                step(self)

        return perform_step


    @_stop_condition
    def step(self):
        '''
        Method that advances the simulation by one tick.
        ''' 
        self._agents_by_type[PersonAgent].do('move_around')
        self._agents_by_type[PersonAgent].do('spread_news')

        regular_agents = self.agents.select(lambda agent: isinstance(agent, PersonAgent) and not agent.knows_about_trend)
        influencer_agents = self.agents.select(lambda agent: isinstance(agent, InfluencerAgent))
        grouped_regular_agents = regular_agents.groupby('sport_enthusiast')
        

        for sport_enthusiast, agents in grouped_regular_agents:
            if sport_enthusiast:
                influencer_agents.do('spread_news_among_followers', agents)
            else:
                agents.do('move_around')



    
        
        


    