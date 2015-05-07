#Close Castles (PyGame Version)
Final Project for CSE 30322: Programming Paradigms

This project is an imitation of the game called Close Castles designed by Asher Vollmer, who is known for another game he designed called Threes!. The original game is still under development and more details can be found on their website (http://closecastles.com/). A link to an interesting gameplay video for Close Castles is also attached here (https://www.youtube.com/watch?v=NN7lXhaDTxs), and most of our designs are based on the original ones.

A server is required before the clients could be started. To start a server on any machine, run
```
python runserver.py
```
Then to start the client, run
```
python rungame.py -s <server_host>
```
where <server_host> is the host address of your server. This game requires at least two players (and at most four) to play, so invite your friends to join the game by running the rungame.py script in the same way you had.

Use arrow keys to navigate through items and make your selection using Space to get started. During the game, press A to build houses, S to build markets, and D to build towers. Each different construction requires a different amount of money (specified in the game), and markets will help you increase the rate of income. You can navigate your cursor with the arrow keys to a house you built, press Space, and then use the arrow keys to create a path from the house to your enemies’ buildings. Houses will then produce soldiers that follow the paths you constructed to attack your rivals. You can also reroute your paths by pressing Space on a house again. Towers are helpful for defending your castle by “vaporizing” the incoming soldiers. Keep in mind that whoever can defend her castle until the end wins, so plan out your strategies and play like a champ!
