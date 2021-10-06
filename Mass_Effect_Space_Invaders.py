import pygame
import os
import random

# initialize pygame
pygame.init()
# get fonts
pygame.font.init()

# set display size
Width = 1920; Height = 1080
WIN = pygame.display.set_mode((Width,Height))
pygame.display.set_caption("Space_Invaders_pygame")

# load images for enemy ships (Reaper, Geth and Cerberus) and resize
ReaperShip = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_Reaper_Sovereign.png")), (50,int(50*550/189)))
GethShip = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_geth_dreadnought.png")), (50,int(50*287/78)))
CerberusShip = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_cerberus_cruiser.png")), (50,int(50*215/76)))
# we use an image of the SSV Normandy as player ship
PlayerShip = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_SSV_Normandy_SR2.png")), (50,int(50*666/375)))

# background (scaled to WidthxHeigth pixels)
Background = pygame.transform.scale(pygame.image.load(os.path.join("assets","background_citadel.jpg")), (Width,Height))
Background2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background_citadel_destroyed.png")), (Width, Height))

# laser beams (scaled to 30x60 pixels)
laserSize = (30,60)
BlueLaser = pygame.transform.scale(pygame.image.load(os.path.join("assets","laser_blue.png")), laserSize)
GreenLaser = pygame.transform.scale(pygame.image.load(os.path.join("assets","laser_green.png")), laserSize)
RedLaser = pygame.transform.scale(pygame.image.load(os.path.join("assets","laser_red.png")), laserSize)
YellowLaser = pygame.transform.scale(pygame.image.load(os.path.join("assets","laser_yellow.png")), laserSize)

# ship with all attributes x,y Position and health
class Ship:
    #frames until we can shoot laser again (we use 60 FPS)
    cooldownTime = 20
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.shipIMG = None
        self.laserIMG = None
        self.lasers = []
        self.laserCooldown = 0

    def draw(self, window):
        for laser in self.lasers:
            laser.draw(WIN)
        window.blit(self.shipIMG, (self.x, self.y))

    def cooldown(self):
        if self.laserCooldown >= self.cooldownTime:
            self.laserCooldown = 0
        elif self.laserCooldown > 0:
            self.laserCooldown += 1

    def shoot(self):
        if self.laserCooldown == 0:
            laser = Laser(self.x - int(self.shipIMG.get_width()/2), self.y, self.laserIMG)
            self.lasers.append(laser)
            self.laserCooldown = 1

    def moveLasers(self, speed, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            # if laser goes off screen remove it
            if laser.offScreen(Height):
                self.lasers.remove(laser)
            # if laser hits object (like player or enemy) reduce health and remove laser
            elif laser.collision(obj):
                obj.health = max(0,obj.health-10)
                self.lasers.remove(laser)
            # else laser moves on
            else:
                laser.move(speed)


# use ship class to get class for player ship
class Player(Ship):
    def __init__(self, x, y, health=100):
        super(Player, self).__init__(x, y, health)
        self.shipIMG = PlayerShip
        self.laserIMG = BlueLaser
        self.mask = pygame.mask.from_surface(self.shipIMG)
        self.health = health
        self.score = 0

    def moveLasers(self, speed, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(speed)
            # if laser goes off screen remove it
            if laser.offScreen(Height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    # if laser hits enemy object remove laser and enemy
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.score += obj.scoreValue
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                    # else laser moves on
                    else:
                        laser.move(speed)

    # draw health bar with rectangular shapes
    def healthbar(self, window):
        # red part
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.shipIMG.get_height() + 10, self.shipIMG.get_width(), 10))
        # green part, length determined by health
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.shipIMG.get_height() + 10, int(self.health/100*(self.shipIMG.get_width())), 10))

    # extend draw method with drawing the healthbar
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

# use ship class to get class for enemy ships
class Enemy(Ship):
    # different ship types with point values
    typeMap = {"Reaper":(ReaperShip,RedLaser,500), "Geth":(GethShip,GreenLaser,300), "Cerberus":(CerberusShip,YellowLaser,150)}
    def __init__(self, x, y, enemytype, health=100):
        super(Enemy, self).__init__(x, y, health)
        self.shipIMG , self.laserIMG, self.scoreValue = self.typeMap[enemytype]
        self.mask = pygame.mask.from_surface(self.shipIMG)

    def move(self, speed):
        self.y = int(self.y + speed)

# create Laser class
class Laser:
    def __init__(self, x, y, laserIMG):
        self.x = x
        self.y = y
        self.laserIMG = laserIMG
        self.mask = pygame.mask.from_surface(self.laserIMG)

    def draw(self, window):
        window.blit(self.laserIMG, (int(self.x) + 18 +laserSize[0]//2, int(self.y) + laserSize[1]//2))

    def move(self, speed):
        self.y += speed

    def offScreen(self, height):
        return not (0 <= self.y <= height)

    def collision(self,obj):
        return collide(obj,self)

# check if 2 objects overlap (e.g. laser hits a ship)
def collide(obj1, obj2):
    xOffset = int(obj2.x - obj1.x + 18 +laserSize[0]//2)
    yOffset = int(obj2.y - obj1.y)
    # overlap returns point of overlapping, None else, hence we get true if we overlap, else False
    return obj1.mask.overlap(obj2.mask, (xOffset,yOffset)) != None

# main loop that runs game
def mainGame():
    # basic game variables
    run = True  #True as long as we want to run game
    FPS = 60    #frames per second we want the game to run
    level = 0; lives = 4; lost = False; lostCount = 0;
    mainFont = pygame.font.SysFont("Sans Serif",40)      #we choose the system Sans Serif font to display text
    lostFont = pygame.font.SysFont("Sans Serif",160)

    # enemy variables
    enemies = []
    enemiesPerWave = 5; enemySpeed = 1

    for enemy in enemies:
        enemy.draw(WIN)

    # player ship initially at center bottom position, movement speed set to 10 pixels per frame
    player = Player(int((Width - PlayerShip.get_width())/2), int(Height - PlayerShip.get_height() - 20))
    speed = 10; player.score = 0

    clock = pygame.time.Clock()

    # get next Frame with current state
    def refreshFrame():
        # take background image and draw at location, (0,0) is top left
        # once lostCount is 1 or higher change background image
        if lostCount < 1:
            WIN.blit(Background, (0,0))
        else:
            WIN.blit(Background2, (0,0))

        # variables that display remaining lives, current level and score
        livesLabel = mainFont.render(f"Lives remaining : {lives}",1, (255,255,255))     #1 means, we use anti-aliasing, (255,255,255) is RGB value of white
        levelLabel = mainFont.render(f"Level : {level}",1, (255,255,255))
        scoreLabel = mainFont.render(f"Score : {player.score}", 1, (255, 255, 255))

        # draw labels
        WIN.blit(livesLabel, (10,10))
        WIN.blit(levelLabel, (Width - levelLabel.get_width(),10))
        WIN.blit(scoreLabel, (int( (Width - scoreLabel.get_width())/2 ),10))

        # draw all enemies
        for enemy in enemies:
            enemy.draw(WIN)

        # draw ship on new position
        player.draw(WIN)

        # display lost message, if we lose
        if lost:
            lostLabel = lostFont.render(f"You Lost! Final Score: {finalScore}",1, (255,255,255))
            WIN.blit(lostLabel, (int((Width - lostLabel.get_width())/2), int(Height/2)))

        # refreshes the display
        pygame.display.update()

    while run:
        # we set clock speed according to given FPS, and refresh frame
        clock.tick(FPS)
        refreshFrame()

        # we check if we still have enough lives, if not we, set lost to True and increase lost counter
        if lost == False and lives <= 0 or player.health <= 0:
            finalScore = player.score
            lost = True
            lostCount += 1

        # once we lost, after 5 seconds (equal to 5*FPS) we set run to false (exiting the loop)
        if lostCount > FPS * 5:
            run = False

        # if all enemies are gone, we go to the next level and create the next batch of enemies
        if len(enemies) == 0:
            player.health = min(100, player.health + 30)
            level += 1; lives += 1
            enemiesPerWave += 5; enemySpeed += 0.2
            for _ in range(enemiesPerWave):
                # on random position spawn random type enemy until we have enough for next wave (y value negative, such that enemie is incoming from above)
                enemy = Enemy( random.randrange(int(0.1*Width),int(0.9*Width)), random.randrange(-1500+level*(-200),-100), random.choice(["Reaper","Geth","Cerberus"]))
                enemies.append(enemy)

        # if we quit the game (press x in the top right corner) set run to False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # get a dictionary of all keys, and if they are pressed or not, for example pygame.K_a stands for a on keyboard
        keys = pygame.key.get_pressed()
        # go left with a key
        if keys[pygame.K_a] and player.x - speed >= 0:
            player.x -= speed
        # go right with d key
        if keys[pygame.K_d] and player.x + speed <= Width - player.shipIMG.get_width():
            player.x += speed
        # go up with w key
        if keys[pygame.K_w] and player.y - speed >= 0:
            player.y -= speed
        # go down with s key
        if keys[pygame.K_s] and player.y + speed <= Height - player.shipIMG.get_height() - 20:
            player.y += speed
        # shoot with space bar
        if keys[pygame.K_SPACE]:
            player.shoot()

        # move enemies at every frame
        for enemy in enemies:
            enemy.move(enemySpeed)
            enemy.moveLasers(enemySpeed+1, player)

            # on average an enemy shoots all 3 seconds
            if random.randrange(0,3*FPS) == 1:
                enemy.shoot()

            # if enemy is at bottom of screen remove enemy from list, and decrease lives
            if enemy.y + enemy.shipIMG.get_height() > Height:
                lives = max(0, lives-1)
                enemies.remove(enemy)

            # if player ship collides with enemy
            if collide(enemy, player):
                player.health = max(0, player.health-20)
                enemies.remove(enemy)

        player.moveLasers(-int(speed*0.5), enemies)

# main menu
def mainMenu():
    titleFont = pygame.font.SysFont("Sans Serif", 80)
    run = True
    while run:
        WIN.blit(Background, (0,0))
        titleLabel = titleFont.render("Press mouse key to begin", 1, (255,255,255))
        WIN.blit(titleLabel, (int((Width - titleLabel.get_width()) / 2), int(Height / 2)))
        titleLabel = titleFont.render("Use W,A,S,D to move, SPACEBAR to shoot", 1, (255, 255, 255))
        WIN.blit(titleLabel, (int((Width - titleLabel.get_width()) / 2), int(Height / 2)-80))

        pygame.display.update()
        for event in pygame.event.get():
            # quit game if we press "x" in top right corner
            if event.type == pygame.QUIT:
                run = False
            # run game if we click with mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                mainGame()

    pygame.quit()

# run game from main menu
mainMenu()


