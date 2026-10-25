"""The standard ProcGen catalog; legacy coinrun_old is intentionally excluded."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    id: str
    title: str
    description: str


GAMES = (
    Game("bigfish", "Big Fish", "Eat smaller fish to grow, and avoid fish larger than you."),
    Game("bossfight", "Boss Fight", "Dodge the boss ship's attacks and shoot when its shields drop."),
    Game("caveflyer", "Cave Flyer", "Pilot a rotating ship through caves, obstacles, and enemies to the exit."),
    Game("chaser", "Chaser", "Collect the green orbs while avoiding enemies in a maze."),
    Game("climber", "Climber", "Climb platforms and collect every star while avoiding flying monsters."),
    Game("coinrun", "CoinRun", "Run and jump past hazards to reach the coin at the end of the level."),
    Game("dodgeball", "Dodgeball", "Defeat enemies with dodgeballs, then reach the unlocked exit."),
    Game("fruitbot", "FruitBot", "Guide a robot through gaps and collect fruit while avoiding other objects."),
    Game("heist", "Heist", "Find colored keys, open matching locks, and steal the gem."),
    Game("jumper", "Jumper", "Explore and double-jump through hazards to find the carrot."),
    Game("leaper", "Leaper", "Cross busy roads and hop across river logs to reach the finish."),
    Game("maze", "Maze", "Navigate a maze as a mouse to find the cheese."),
    Game("miner", "Miner", "Dig for diamonds, avoid falling rocks, and find the exit."),
    Game("ninja", "Ninja", "Charge jumps across narrow ledges and avoid bombs to reach the mushroom."),
    Game("plunder", "Plunder", "Fire at the target pirate ships while conserving time and avoiding friendly ships."),
    Game("starpilot", "StarPilot", "Fly through a scrolling field of enemy ships, projectiles, and obstacles."),
)

GAME_IDS = tuple(game.id for game in GAMES)
GAME_BY_ID = {game.id: game for game in GAMES}
