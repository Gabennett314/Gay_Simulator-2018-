#################################################################
# 15-112-n18 Term Project
# Your Name: George Austin Bennett
# Your Andrew ID: gbennett
# Your Section: A
#################################################################
import math
import random
import os
#################################################################
# Classes:
#################################################################

# Superclass for all moving objects (player, chad, wbc member, etc.)
class movingObject (object):
    # Initializes standard values for moving object
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.width = 50
        self.height = 50
    
    # Checks all four points plus center for a collision to check if two
    # Shapes collide at any point in time
    def isCollision(self, other):
        objectPoints = [(self.cx - self.width//2, self.cy - self.height//2),
                   (self.cx + self.width//2, self.cy - self.height//2),
                   (self.cx - self.width//2, self.cy + self.height//2),
                   (self.cx + self.width//2, self.cy + self.height//2),
                   (self.cx, self.cy)]
        # Checks each of the points in the shape
        for oPoint in objectPoints:
            if (oPoint[0] > other.cx - other.width//2 
            and oPoint[0] < other.cx + other.width//2
            and oPoint[1] > other.cy - other.height//2 
            and oPoint[1] < other.cy + other.height//2):
                return True
        return False
    
    # This checks if the object being checked collides with the wall
    def isCollisionWithWall(self, width, height):
        return(self.cx - self.width//2 < 0 or self.cx + self.width//2 > width or
            self.cy - self.height//2 < 0 or self.cy + self.height//2 > height- 50)  
    
    # Moves the object (normally on timer fired)
    def move(self, direction):
        self.cx += self.speed*direction[0]
        self.cy += self.speed*direction[1]
    
    # Undoes move (in case of move being invalid)
    def undoMove(self, direction):
        self.cx -= self.speed*direction[0]
        self.cy -= self.speed*direction[1]
    
class player (movingObject):
    # Defines values for the player
    def __init__(self, cx, cy):
        super().__init__(cx, cy)
        self.width = 30
        self.height = 50
        self.speed = 3
        self.health = 500
    
    # Draws the player (Freddie Mercury Sprite)
    def draw (self, canvas, data):
        canvas.create_image(self.cx, self.cy, image = data.playerImage)
    
    # Checks if the player was hit with a NoHomo or a bill
    def hitWithProjectile(self, data):
        for projectile in data.projectiles:
            # Checks for collision with NoHomo
            if (self.isCollision(projectile) and isinstance(projectile, noHomo)):
                self.health -=25
                data.projectiles.remove(projectile)
            # Checks for collision with bill
            elif (self.isCollision(projectile) and isinstance(projectile, bill)):
                self.speed = (self.speed*2)/3
                data.projectiles.remove(projectile)
    
    def collideWithEnemy(self, data):
        # Checks if player collides with enemy, if they do, the enemy is removed
        # And the player loses 50 health
        for enemy in data.enemies:
            if (self.isCollision(enemy) == True):
                data.enemies.remove(enemy)
                self.health -= 50
                
    # Does all timer fired actions for the player
    def onTimerFired(self, data):
        # Moves the player
        self.move(data.direction)
        # Checks if the player collides with the wall
        if (self.isCollisionWithWall(data.width, data.height) == True):
            self.undoMove(data.direction)
        # Checks to make sure that the player isn't colliding with any borders
        for barrier in data.barriers:
            if (self.isCollision(barrier) == True):
                self.undoMove(data.direction)
        # Checks to make sure that player isn't colliding with any spawners
        for spawnLocation in data.spawnLocations:
            if (self.isCollision(spawnLocation) == True):
                self.undoMove(data.direction)
        # Checks for collision with enemy
        self.collideWithEnemy(data)
        # Checks if hit with projectile
        self.hitWithProjectile(data)
        # Ends game if player is dead
        if (self.health <= 0):
            data.gameOver = True
        
class chad(movingObject):
    # Defines values for a Chad
    def __init__(self, cx, cy, angle):
        super().__init__(cx, cy)
        self.angle = angle
        self.width = 20
        self.height = 50
        self.health = 100
        self.speed = 1.5
        
    # Draws chad (Hands-Folded White Guy Sprite)
    def draw (self, canvas, data):
        canvas.create_image(self.cx, self.cy, image = data.chadImage)
                                
    # Checks if the player hit chad with a flag
    def hitWithFlag(self, data):
        for flag in data.rainbowFlagList:
            # Chad loses 25 health if true and flag is removed
            if (flag.isCollision(self) == True):
                self.health -=25
                data.rainbowFlagList.remove(flag)
    
    # Sets the angle which chad uses to persue the player
    def setAngle(self, data):
        angleX = data.player.cx - self.cx
        angleY = data.player.cy - self.cy
        self.angle = math.atan2(angleY, angleX)
    
    # Has chad run off the screen if RuPaul powerup is active
    def runAway (self):
        self.speed = 10
        # These if/else statments help determine what direction chad runs off in
        # Based on his current location and legal moves he can make
        if (self.cx <= 600):
            if ((self.cx <= 545 and self.cx >= 505) or 
                (self.cx <= 545 and self.cx >= 405) or 
                (self.cx >= 80 and self.cx <= 120) or 
                (self.cx >= 80 and self.cx <= 220)):
                self.move((1, 0))
            else:
                if (self.cy >= 300):
                    self.move ((0, 1))
                else:
                    self.move((0, -1))
        else:
            if ((self.cx <= 695 and self.cx >= 655) or (self.cx <= 795 and self.cx >= 655) 
            or (self.cx <= 1120 and self.cx >= 1080) or (self.cx <= 1120 and self.cx >= 980)):
                self.move((-1, 0))
            else:
                if (self.cy >= 300):
                    self.move ((0, 1))
                else:
                    self.move((0, -1))
               
    # Actions for Chad if Pride Parade is active
    def onPrideParade(self, data):
        if ((self.cx >= data.player.cx - 50 and self.cx <= data.player.cx + 50) or
            (self.cy >= data.player.cy - 50 and self.cy <= data.player.cx + 50)):
                data.enemies.remove(self)

    # Executes all timer fired actions for chad
    def onTimerFired(self, data):
        # Checks for is RuPaul is active
        if (data.ruPaulShow > 0):
            self.runAway()
            if (self.isCollisionWithWall(data.width, data.height) == True):
                data.enemies.remove(self)
        # Calculates distance from player (Important for later actions)
        distFromPlayer = ((self.cx - data.player.cx)**2 + 
                          (self.cx - data.player.cx)**2)**0.5
        # Checks if pride parade is active
        if (data.prideCounter > 0):
            self.onPrideParade(data)
        # Chad follow player if player is within 300 pixels of him
        if (distFromPlayer <= 300):
            self.setAngle(data)
        # Moves if both RuPaul and Alan Turing are inactive
        if (data.stunCounter == 0 and data.ruPaulShow == 0):
            self.move((math.cos(self.angle), math.sin(self.angle)))
        # Checks if the chad collides with the wall
        if (self.isCollisionWithWall(data.width, data.height) == True):
            self.undoMove((math.cos(self.angle), math.sin(self.angle)))
            self.angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        # Checks to make sure that the chad isn't colliding with any barriers
        for barrier in data.barriers:
            if (self.isCollision(barrier) == True):
                self.undoMove((math.cos(self.angle), math.sin(self.angle)))
                self.angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        # Checks to make sure that chad isn't colliding with any spawners
        for spawnLocation in data.spawnLocations:
            if (self.isCollision(spawnLocation) == True):
                self.undoMove((math.cos(self.angle), math.sin(self.angle)))
                self.angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        self.hitWithFlag(data)
        # If his health is 0 he is deleted and 1 is added to the score
        if (self.health <= 0):
            data.enemies.remove(self)
            data.score += 1
        # Fires NoHomo at player if the player is within 300 pixels of him
        if (data.counter % 100 == 0 and distFromPlayer <= 300 
            and data.stunCounter == 0):
               data.projectiles.append(noHomo(self.cx, self.cy, 
                                              70, 20, self.angle))

class baptistChurchMember(movingObject):
    # Initializes important values for the baptist church member
    def __init__(self, cx, cy):
        super().__init__(cx, cy)
        self.angle = 0
        self.width = 40
        self.height = 40
        self.health = 100
        self.speed = 1
    
    # Draws the baptist church member (Westboro Baptist Church Member Sprite)
    def draw (self, canvas, data):
        canvas.create_image(self.cx, self.cy, image = data.BCMImage)

    
    # Checks if the player hit church member with a flag
    def hitWithFlag(self, data):
        for flag in data.rainbowFlagList:
            # Church member loses 25 health if true and flag is removed
            if (flag.isCollision(self) == True):
                self.health -=25
                data.rainbowFlagList.remove(flag)
    
    # Sets angle that the church member uses to follow the player
    def setAngle(self, data):
        angleX = data.player.cx - self.cx
        angleY = data.player.cy - self.cy
        self.angle = math.atan2(angleY, angleX)
    
    # Has chad run off the screen if RuPaul powerup is active
    def runAway (self):
        self.speed = 10
        # These if/else statments help determine what direction the member
        # Runs off in based on their current location and legal moves
        if (self.cx <= 600):
            if ((self.cx <= 545 and self.cx >= 505) or 
                (self.cx <= 545 and self.cx >= 405) or
                (self.cx >= 80 and self.cx <= 120) or 
                (self.cx >= 80 and self.cx <= 220)):
                self.move((1, 0))
            else:
                if (self.cy >= 300):
                    self.move ((0, 1))
                else:
                    self.move((0, -1))
        else:
            if ((self.cx <= 695 and self.cx >= 655) or 
                (self.cx <= 795 and self.cx >= 655) or 
                (self.cx <= 1120 and self.cx >= 1080) or 
                (self.cx <= 1120 and self.cx >= 980)):
                self.move((-1, 0))
            else:
                if (self.cy >= 300):
                    self.move ((0, 1))
                else:
                    self.move((0, -1))
    
    # Actions for church member if pride parade is active
    def onPrideParade(self, data):
        if ((self.cx >= data.player.cx - 50 and self.cx <= data.player.cx + 50) or
            (self.cy >= data.player.cy - 50 and self.cy <= data.player.cx + 50)):
                data.enemies.remove(self)
                
    def onTimerFired(self, data):
        # Checks to see if RuPaul is active
        if (data.ruPaulShow > 0):
            self.runAway()
            if (self.isCollisionWithWall(data.width, data.height) == True):
                data.enemies.remove(self)
        # Checks to see if Pride Parade is active
        if (data.prideCounter > 0):
            self.onPrideParade(data)
        # Calculates distance from player (Important for later actions)
        distFromPlayer = ((self.cx - data.player.cx)**2 + 
                          (self.cx - data.player.cx)**2)**0.5
        # If the player is within 300 pixels, the church member follows them
        # And the church member's speed triples
        if (distFromPlayer <= 300):
            self.speed = 3
            self.setAngle(data)
        else:
            self.speed = 1
        # Moves if Alan Turing and RuPaul aren't active
        if (data.stunCounter == 0 and data.ruPaulShow == 0):
            self.move((math.cos(self.angle), math.sin(self.angle)))
        # Checks if the church member collides with the wall
        if (self.isCollisionWithWall(data.width, data.height) == True):
            self.undoMove((math.cos(self.angle), math.sin(self.angle)))
            self.angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        # Checks to make sure that the church member isn't hitting any barriers
        for barrier in data.barriers:
            if (self.isCollision(barrier) == True):
                self.undoMove((math.cos(self.angle), math.sin(self.angle)))
                self.angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        # Checks to make sure that church members isn't hitting any spawners
        for spawnLocation in data.spawnLocations:
            if (self.isCollision(spawnLocation) == True and 
                not isinstance(spawnLocation, baptistChurch)):
                self.undoMove((math.cos(self.angle), math.sin(self.angle)))
                self.angle = random.choice([0, math.pi/2, math.pi, 3*math.pi/2])
        # Checks if church member is hit with flag
        self.hitWithFlag(data)
        # If his health is 0 he is deleted
        if (self.health <= 0):
            data.enemies.remove(self)
            data.score += 1
    
# CURVING MOVING WEAPONS
class curvingMovingWeapon (movingObject):
    # Defines all values for the weapon
    def __init__(self, cx, cy, width, height, angle):
        super().__init__(cx, cy)
        self.width = width
        self.height = height
        self.angle = angle
        self.speed = 5
                           
    # Moves the weapon according to the angle of the click from the player
    def move (self):
        self.cx += self.speed*math.cos(self.angle)
        self.cy += self.speed*math.sin(self.angle)

class rainbowFlag (curvingMovingWeapon):
    # Defines all values for the rainbow flag
    def __init__(self, cx, cy, width, height, angle):
        super().__init__(cx, cy, width, height, angle)
        self.speed = 5
    
    # Draws a rainbow flag on the canvas
    def draw (self, canvas):
        flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
        # Draws all 6 stripes of the standard LGBTQIA+ flag
        for stripe in range (0, 6, 1):
            canvas.create_rectangle (self.cx - self.width//2, 
                            self.cy - self.height//2 + (self.height*stripe//6), 
                            self.cx + self.width//2, 
                            self.cy-self.height//2+((stripe+1)*self.height//6), 
                           fill = flagColors[stripe], width = 0)
        
    # Does all timer fired actions for the flag
    def onTimerFired(self, data):
        # Deletes the flag if it runs into the wall
        if (self.isCollisionWithWall(data.width, data.height) == True):
            data.rainbowFlagList.remove(self)
            return
        # Deletes the flag if it runs into any of the barriers
        for barrier in data.barriers:
            if (self.isCollision(barrier) == True):
                data.rainbowFlagList.remove(self)
                return
        # Moves the flag
        self.move()

class projectile (curvingMovingWeapon):
    # Defines important values for a projectile
    def __init__(self, cx, cy, width, height, angle):
        super().__init__(cx, cy, width, height, angle)
        self.speed = 3
    
    def hitWithFlag(self, data):
        for flag in data.rainbowFlagList:
            # Projectile is destroyed if it is hit with flag
            if (self.isCollision(flag) == True):
                data.projectiles.remove(self)
                return
    
    # Pride Parade actions for projectile
    def onPrideParade(self, data):
        if ((self.cx >= data.player.cx - 50 and self.cx <= data.player.cx + 50) or
            (self.cy >= data.player.cy - 50 and self.cy <= data.player.cx + 50)):
                data.projectiles.remove(self)
                
    # Does all timer fired actions for the projectile
    def onTimerFired(self, data):
        # Deletes the projectile if it runs into the wall
        if (self.isCollisionWithWall(data.width, data.height) == True):
            data.projectiles.remove(self)
            return
        # Deletes the projectile if it runs into any of the barriers
        for barrier in data.barriers:
            if (self.isCollision(barrier) == True):
                data.projectiles.remove(self)
                return
        # Checks if Pride Parade is active
        if (data.prideCounter > 0):
            self.onPrideParade(data)
        # Checks if the projectile is hit with a flag
        self.hitWithFlag(data)
        self.move()
    
    
class noHomo (projectile):
    # Defines important values for a NoHomo
    def __init__(self, cx, cy, width, height, angle):
        super().__init__(cx, cy, width, height, angle)
        self.speed = 3
    
    # Draws a NoHomo
    def draw (self, canvas, data):
        canvas.create_rectangle(self.cx-self.width//2, self.cy-self.height//2,
                                self.cx+self.width//2, self.cy+self.height//2,
                                fill = "salmon", width = 0)
        canvas.create_text(self.cx, self.cy, text = "No Homo!",
                           font = "ComicSansMS 16 bold")

class bill (projectile):
    # Defines important values for a Bill
    def __init__(self, cx, cy, width, height, angle):
        super().__init__(cx, cy, width, height, angle)
        self.speed = 3
    # Draws a Bill
    def draw (self, canvas, data):
        canvas.create_image(self.cx, self.cy, image = data.BillImage)

class spawnLocation (object):
    # Defines important values for a spawn location
    def __init__(self, cx, cy, width, height):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.health = 1000
    
    # Checks all four points plus center for a collision to check if two
    # Shapes collide at any point in time
    def isCollision(self, other):
        objectPoints = [(self.cx - self.width//2, self.cy - self.height//2),
                   (self.cx + self.width//2, self.cy - self.height//2),
                   (self.cx - self.width//2, self.cy + self.height//2),
                   (self.cx + self.width//2, self.cy + self.height//2),
                   (self.cx, self.cy)]
        # Checks each of the points in the shape
        for oPoint in objectPoints:
            if (oPoint[0] > other.cx - other.width//2 
            and oPoint[0] < other.cx + other.width//2
            and oPoint[1] > other.cy - other.height//2 
            and oPoint[1] < other.cy + other.height//2):
                return True
        return False
    
    # Checks if the player hit building with a flag
    def hitWithFlag(self, data):
        for flag in data.rainbowFlagList:
            # Building loses 25 health if true and flag is removed
            if (flag.isCollision(self) == True):
                self.health -=25
                data.rainbowFlagList.remove(flag)

class mississippi (spawnLocation):
    # Defines important values for mississippi
    def __init__(self, cx, cy, width, height):
        super().__init__(cx, cy, width, height)
        self.angle = 0
        self.health = 1000
    
    # Represented by purple square for now but will be a sprite
    def draw (self, canvas, data):
        canvas.create_rectangle(self.cx - 50, self.cy - 50, self.cx + 50, 
                                self.cy + 50, fill = "pink", width = 0)
        canvas.create_image(self.cx, self.cy, image = data.mississippiImage)
    
    # Timer fired actions for mississippi
    def onTimerFired(self, data):
        # Important value used for lated actions
        distFromPlayer = ((self.cx - data.player.cx)**2 + 
                          (self.cx - data.player.cx)**2)**0.5
        # Spawns two bills every 100 seconds if a player is within 300 pixels
        # And Alan Turing is not active
        if (data.counter % 100 == 0 and distFromPlayer <= 300 
            and data.stunCounter == 0):
            if (self.cx > 600):
                data.projectiles.append(bill(self.cx, self.cy, 20, 20, 0))
            else:
                data.projectiles.append(bill(self.cx, self.cy, 
                                             20, 20, math.pi))
            if (self.cy > 300):
                data.projectiles.append(bill(self.cx, self.cy, 
                                             20, 20, math.pi/2))
            else:
                data.projectiles.append(bill(self.cx, self.cy, 
                                             20, 20, 3*math.pi/2))
        # Checks if hit with flag
        self.hitWithFlag(data)
        # If mississippi is killed it is removed from the board
        if (self.health <= 0):
            data.spawnLocations.remove(self)
                    
class baptistChurch (spawnLocation):
    # Important values for the baptist church
    def __init__(self, cx, cy, width, height):
        super().__init__(cx, cy, width, height)
        self.angle = 0
    
    # Draws church, yellow rectange for now but will be a sprite
    def draw (self, canvas, data):
        canvas.create_rectangle(self.cx - 50, self.cy - 50, self.cx + 50, 
                                self.cy + 50, fill = "pink", width = 0)
        canvas.create_image(self.cx, self.cy, image = data.baptistChurchImage)

    
    # Timer fired actions for the baptist church
    def onTimerFired (self, data):
        # If Alan Turing isn't active, it spawns a baptist church member every 
        # Five Seconds.
        if (data.counter % 200 == 0 and data.stunCounter == 0):
            data.enemies.append(baptistChurchMember(self.cx, self.cy))
        # Checks if it is hit with a flag
        self.hitWithFlag(data)
        # If the church is killed it is removed from the board
        if (self.health <= 0):
            data.spawnLocations.remove(self)

class barrier (object):
    # Defines all values for the barrier
    def __init__(self, cx, cy, width, height):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
    
    # Draws the barrier on the board
    def draw (self, canvas):
        canvas.create_rectangle(self.cx-self.width//2, self.cy-self.height//2,
                                self.cx+self.width//2, self.cy+self.height//2,
                                fill = "black", width = 0)
                                
####################4#############################################
# Helper Functions:
##################################################################

# These functions load the images for the sprites
def loadPlayer (data):
    filename = "FreddieMercury.gif"
    data.playerImage = PhotoImage(file = filename)
    
def loadChad (data):
    filename = "Chad.gif"
    data.chadImage = PhotoImage(file = filename)

def loadBaptistChurchMember(data):
    filename = "BaptistChurchMember.gif"
    data.BCMImage = PhotoImage(file = filename)

def loadMississippi(data):
    filename = "Mississippi.gif"
    data.mississippiImage = PhotoImage(file = filename)

def loadBaptistChurch(data):
    filename = "BaptistChurch.gif"
    data.baptistChurchImage = PhotoImage(file = filename)

def loadBill (data):
    filename = "Bill.gif"
    data.BillImage = PhotoImage(file = filename)
    
def loadRuPaul (data):
    data.ruPaulImages = []
    for index in range(1, 8, 1):
        filename = "RuPaul" + os.sep + "RuPaulShow%d.gif" % (index)
        data.ruPaulImages.append(PhotoImage(file = filename))

def loadAlanTuring (data):
    data.AlanTuringImages = []
    for index in range(1, 8, 1):
        filename = "AlanTuring" + os.sep + "AlanTuring%d.gif" % (index)
        data.AlanTuringImages.append(PhotoImage(file = filename))

def loadLadyGaga (data):
    data.LadyGagaImages = []
    for index in range(1, 12, 1):
        filename = "Gaga" + os.sep + "Gaga%d.gif" % (index)
        data.LadyGagaImages.append(PhotoImage(file = filename))
        
# Draws the blank board using the barriers and spawnLocations lists
def makeBoard (canvas, data):
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws all 6 stripes of the standard LGBTQIA+ flag
    for stripe in range (0, 6, 1):
        canvas.create_rectangle(0, (550/6)*stripe, data.width, (550/6)*(stripe+1), 
                                fill = flagColors[stripe], width = 0)
    # Draws all barriers
    for barrier in data.barriers:
        barrier.draw(canvas)
    # Draws all spawn locations
    for spawnLocation in data.spawnLocations:
        spawnLocation.draw(canvas, data)

# Creates a chad every two seconds in one of four locations if
# An Alan Turing has not been used in the last five seconds
def createChad(data):
    if (data.counter % 100 == 0 and data.stunCounter == 0):
        if (data.counter % 400 == 0):
            data.enemies.append(chad(data.width//2, 26, math.pi/2))
        if (data.counter % 400 == 100):
            data.enemies.append(chad(data.width//2,data.height-76, 3*math.pi/2))
        if (data.counter % 400 == 200):
            data.enemies.append(chad(10, data.height//2, 0))
        if (data.counter % 400 == 300):
            data.enemies.append(chad(data.width - 10, data.height//2, math.pi))

# Draws the statistics for the bottom screen
def drawBottomScreen (canvas, data):
    # Creates bottom bar
    canvas.create_rectangle(0, 550, 1200, 600, fill = "white", width = 0)
    canvas.create_text(150, 575, text = "Level: %d" % (data.level), 
                       font = "TimesNewRoman 24")
    canvas.create_text(300, 575, text = "Score: %d" % (data.score), 
                       font = "TimesNewRoman 24")
    canvas.create_text(450, 575, text = "Health: %d" % (data.player.health), 
                       font = "TimesNewRoman 24")
    canvas.create_text(700, 575, text = "Time remaining: %d" % (data.timeRemaining//50),
                       font = "TimesNewRoman 24")
    # Displays powerup amounts
    canvas.create_text(1000, 575, text = "RP: %d AT: %d LG: %d PP: %d" % 
    (data.powerups["RuPaul"], data.powerups["Alan Turing"], data.powerups["Lady Gaga"], data.powerups["Pride Parade"]),
    font = "TimesNewRoman 24")

# Actions if RuPaul is used
def callRuPaul(data):
    data.ruPaulShow = 150
    data.ruPaulIndex = 0
    data.powerups["RuPaul"] -= 1

# Actions if Alan Turing is used
def callAlanTuring(data):
    data.stunCounter = 500
    data.AlanTuringIndex = 0
    data.powerups["Alan Turing"] -= 1

# Actions if Gaga and Britney is used
def callLadyGaga(data):
    data.player.health = 500
    data.LadyGagaIndex = 0
    data.powerups["Lady Gaga"] -= 1

# Actions if Pride Parade is used
def prideParade(data):
    for key in data.powerups:
        data.powerups[key] += 1
    data.prideCounter = 200
    data.powerups["Pride Parade"] -= 2

# Draws the pride parade on the screen
def drawPrideParade(canvas, data):
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws all 6 stripes of the standard LGBTQIA+ flag in vertical direction
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (data.player.cx - 50 + (100/6)*stripe, 0,
                                 data.player.cx - 50 + (100/6)*(stripe+1), 
                                 data.height, fill = flagColors[stripe], 
                                 width = 0)
    # Draws all 6 stripes of the standard LGBTQIA+ flag in horizontal direction
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, data.player.cy - 50 + (100/6)*stripe,
                                 data.width, data.player.cy - 50 + (100/6)*(stripe+1), 
                                 fill = flagColors[stripe], width = 0)

# Draws ruPaul animation after powerup is used
def drawRuPaul(canvas, data):
    message = "Rupaul scares away all Chads and WBC Members!"
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws ruPaul gif
    canvas.create_image(600, 300, image = data.ruPaulImages[data.ruPaulIndex%7])
    # Draws the background for the message
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, 450 + 25*stripe, 1200, 450 + 25*(stripe + 1),
                                 fill = flagColors[stripe], width = 0)
    # Draws message
    canvas.create_text(600, 525, text = message, font = "TimesNewRoman 44 bold")
    
# Draws Alan Turing animation after powerup is used
def drawAlanTuring(canvas, data):
    message = "Alan Turing confuses everyone to the point of stopping!"
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws Alan Turing gif
    canvas.create_image(600, 300, image = data.AlanTuringImages[data.AlanTuringIndex%7])
    # Draws the background for the message
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, 450 + 25*stripe, 1200, 450 + 25*(stripe + 1),
                                 fill = flagColors[stripe], width = 0)
    # Draws message
    canvas.create_text(600, 525, text = message, font = "TimesNewRoman 40 bold")

# Draws Lady Gaga animation after powerup is used
def drawLadyGaga(canvas, data):
    message = "Lady Gaga serenades you back to full health!"
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws Lady Gaga gif
    canvas.create_image(600, 300, image = data.LadyGagaImages[data.LadyGagaIndex%11])
    # Draws the background for the message
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, 450 + 25*stripe, 1200, 450 + 25*(stripe + 1),
                                 fill = flagColors[stripe], width = 0)
    # Draws message
    canvas.create_text(600, 525, text = message, font = "TimesNewRoman 44 bold")

def drawStartScreen (canvas, data):
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws all 6 stripes of the standard LGBTQIA+ flag
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, 100*stripe, 1200, 100*(stripe+1), 
                                 fill = flagColors[stripe], width = 0)
    # Draws all boxes and text
    canvas.create_rectangle(data.width//2 - 250, 115, data.width//2 + 250, 185, fill = "pink", width = 0)
    canvas.create_text (600, 150, text = "Gay Simulator", 
                        font = "TimesNewRoman 72")
    canvas.create_rectangle(data.width//2 - 150, 215, data.width//2 + 150, 285, fill = "pink", width = 0)
    canvas.create_text (600, 250, text = "By: Austin Bennett", 
                        font = "TimesNewRoman 36")
    canvas.create_rectangle(data.width//2 - 200, 415, data.width//2 + 200, 485, fill = "pink", width = 0)
    canvas.create_text (600, 450, text = "Click anywhere to start!", 
                        font = "TimesNewRoman 36")

def drawInstructionScreen (canvas, data):
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws all 6 stripes of the standard LGBTQIA+ flag as background
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, 100*stripe, 1200, 100*(stripe+1), 
                                 fill = flagColors[stripe], width = 0)
    # Draws all pink boxes
    canvas.create_rectangle(data.width//2 - 250, 15, data.width//2 + 250, 85, fill = "pink", width = 0)
    canvas.create_rectangle(100, 125, 500, 275, fill = "pink", width = 0)
    canvas.create_rectangle(700, 125, 1100, 275, fill = "pink", width = 0)
    canvas.create_rectangle(100, 325, 500, 475, fill = "pink", width = 0)
    canvas.create_rectangle(700, 325, 1100, 475, fill = "pink", width = 0)
    # Draws all text inside of pink boxes
    canvas.create_text(data.width//2, 50, text = "Instructions:", 
                        font = "TimesNewRoman 72")
    canvas.create_text(300, 150, text = "Shooting: ", font = "TimesNewRoman 24")
    canvas.create_text(300, 180, text = "~Shoot Homophobic people and buildings with Rainbow Flags!", font = "TimesNewRoman 12")
    canvas.create_text(300, 210, text = "~The Rainbow Flags will shoot towards the mouse click!")
    canvas.create_text(300, 240, text = "~You can shoot down enemy projectiles with a Rainbow Flag!", font = "TimesNewRoman 12")
    canvas.create_text(900, 150, text = "Powerups: ", font = "TimesNewRoman 24")
    canvas.create_text(900, 175, text = "~Press 1 to have RuPaul scare away all homophobes!", font = "TimesNewRoman 12")
    canvas.create_text(900, 200, text = "~Press 2 to have Alan Turing stop all activity on the board!")
    canvas.create_text(900, 225, text = "~Press 3 to have Lady Gaga serenade you to full health!", font = "TimesNewRoman 12")
    canvas.create_text(900, 250, text = "~Press Enter to use pride parade (a surprise powerup)", font = "TimesNewRoman12")
    canvas.create_text(300, 350, text = "Health: ", font = "TimesNewRoman 24")
    canvas.create_text(300, 375, text = "~You can take up to 500 damage!", font = "TimesNewRoman 12")
    canvas.create_text(300, 400, text = "~If you collide with a homophobe, you will lose 50 health!", font = "TimesNewRoman 12")
    canvas.create_text(300, 425, text = "~If you are hit with a NoHomo you will lose 25 health!", font = "TimesNewRoman 12")
    canvas.create_text(300, 450, text = "~If you are hit with a Bill you will go to 2/3 speed!", font = "TimesNewRoman 12")
    canvas.create_text(900, 350, text = "Gameplay: ", font = "TimesNewRoman 24")
    canvas.create_text(900, 375, text = "~Four flags will mollify a homophobe", font = "TimesNewRoman 12")
    canvas.create_text(900, 400, text = "~Forty flags will mollify a homophobic building!", font = "TimesNewRoman 12")
    canvas.create_text(900, 425, text = "~Eliminate all homophobic buildings to advance to the next level!", font = "TimesNewRoman 12")
    canvas.create_text(900, 450, text = "~If you don't eliminate all buildings in 180 sec you lose!", font = "TimesNewRoman 12")
    
# Taken from 112 website
def readFile(path):
    with open(path, "rt") as f:
        return f.read()
    
def drawGameOver(canvas, data):
    highScore = readFile("HighScore.txt")
    flagColors = ["red", "orange", "yellow", "green2", "blue", "purple"]
    # Draws all 6 stripes of the standard LGBTQIA+ flag
    for stripe in range (0, 6, 1):
        canvas.create_rectangle (0, 100*stripe, 1200, 100*(stripe+1), 
                                 fill = flagColors[stripe], width = 0)
    # Displays score and game over messages
    canvas.create_rectangle(data.width//2 - 250, 115, data.width//2 + 250, 185, fill = "pink", width = 0)
    canvas.create_text (600, 150, text = "Game Over!", 
                        font = "TimesNewRoman 72")
    canvas.create_rectangle(data.width//2 - 150, 215, data.width//2 + 150, 285, fill = "pink", width = 0)
    canvas.create_text (600, 250, text = "Score: %d" % (data.score), 
                        font = "TimesNewRoman 36")
    canvas.create_rectangle(data.width//2 - 200, 315, data.width//2 + 200, 385, fill = "pink", width = 0)
    canvas.create_text (600, 350, text = "High Score: %d" % int(highScore), 
                        font = "TimesNewRoman 36")
    canvas.create_rectangle(data.width//2 - 250, 415, data.width//2 + 250, 485, fill = "pink", width = 0)
    canvas.create_text (600, 450, text = "Press 'r' to play again!", 
                        font = "TimesNewRoman 36")
def setHighScore (data):
    contentsToWrite = readFile("HighScore.txt")
    currHighScore = readFile("HighScore.txt")
    if (int(currHighScore) < data.score):
        contentsToWrite = str(data.score)
    writeFile("HighScore.txt", contentsToWrite)

# Taken from 112 website
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def nextLevel(data, level):
    # Resets all resetting values for the next level and adds spawn locations
    # If the level is less than 5
    data.player.cx = data.width/2
    data.player.cy = data.height/2
    data.timeRemaining = 9000
    data.timerDelay = 1
    data.direction = (0, 0)
    data.counter = 0
    data.currPowerup = ""
    data.ruPaulShow = 0
    data.prideCounter = 0
    data.stunCounter = 0
    data.gameOver = False
    data.projectiles = []
    data.enemies = []
    data.rainbowFlagList = []
    data.spawnLocations = data.allSpawnLocations[0:2*min(level, 4)]
    for spawnLocation in data.spawnLocations:
        spawnLocation.health = 1000
        
#################################################################
# Animation:
#################################################################
from tkinter import *

####################################
# customize these functions
####################################

def init(data):
    # Initializes important values in data
    loadPlayer(data)
    loadMississippi(data)
    loadBaptistChurch(data)
    loadChad(data)
    loadBill(data)
    loadBaptistChurchMember(data)
    loadRuPaul(data)
    loadAlanTuring(data)
    loadLadyGaga(data)
    data.ruPaulIndex = 36
    data.AlanTuringIndex = 36
    data.LadyGagaIndex = 56
    data.level = 1
    data.timeRemaining = 9000
    data.player = player(data.width//2, data.height//2)
    data.score = 0
    data.timerDelay = 1
    data.direction = (0, 0)
    data.counter = 0
    data.currPowerup = ""
    data.ruPaulShow = 0
    data.prideCounter = 0
    data.stunCounter = 0
    data.startScreen = True
    data.instructionScreen = False
    data.gameOver = False
    data.projectiles = []
    data.enemies = []
    data.rainbowFlagList = []
    data.powerups = {"RuPaul": 3, "Alan Turing": 3, "Lady Gaga": 3, 
                     "Pride Parade": 2}
    data.allSpawnLocations = [baptistChurch(170, 120, 100, 100), 
                           baptistChurch(1030, 120, 100, 100),
                           baptistChurch(170, 429, 100, 100), 
                           baptistChurch(1030, 429, 100, 100),
                           mississippi(455, 130, 100, 100), 
                           mississippi(745, 130, 100, 100),
                           mississippi(455, 420, 100, 100), 
                           mississippi(745, 420, 100, 100),]
    data.spawnLocations = [baptistChurch(170, 120, 100, 100), 
                           baptistChurch(1030, 120, 100, 100)]
    data.barriers = [barrier(100, 100, 40, 140), barrier(1100, 100, 40, 140),
                     barrier(100, 449, 40, 140), barrier(1100, 449, 40, 140),
                     barrier(150, 50, 140, 40), barrier(1050, 50, 140, 40),
                     barrier(150, 499, 140, 40), barrier(1050, 499, 140, 40),
                     barrier(525, 150, 40, 140), barrier(525, 400, 40, 140),
                     barrier(675, 150, 40, 140), barrier(675, 400, 40, 140),
                     barrier(475, 200, 140, 40), barrier(475, 350, 140, 40),
                     barrier(725, 200, 140, 40), barrier(725, 350, 140, 40),
                                                                           ]

def mousePressed(event, data):
    # Moves past instruction screen
    if (data.instructionScreen == True and event.x > 0 and event.x < 1200 and 
                                                event.y > 0 and event.y < 600):
        data.instructionScreen = False
        data.timeRemaining = 9000
    # Moves past start screen
    if (data.startScreen == True and event.x > 0 and event.x < 1200 and 
                                                event.y > 0 and event.y < 600):
        data.startScreen = False
        data.instructionScreen = True
        return
    # Does nothing if game is over
    if (data.gameOver == True):
        return
    # These three lines determine the angle made from the player to the click
    # Of the mouse in radians.
    angleX = event.x - data.player.cx
    angleY = event.y - data.player.cy
    angle = math.atan2(angleY, angleX)
    # Makes a rainbow flag using the given angle of the click
    data.rainbowFlagList.append(rainbowFlag(data.player.cx, data.player.cy,
                                            20, 15, angle))

def keyPressed(event, data):
    # Restars game if game is over and r is pressed
    if (data.gameOver == True or data.startScreen == True):
        if (event.keysym == "r"):
            init(data)
        else:
            return
    # Using the standard WASD keys, it moves the player in various directions
    if (event.keysym == "a" or event.keysym == "A"):
        data.direction = (-1, 0)
    if (event.keysym == "d" or event.keysym == "D"):
        data.direction = (1, 0)
    if (event.keysym == "w" or event.keysym == "W"):
        data.direction = (0, -1)
    if (event.keysym == "s" or event.keysym == "S"):
        data.direction = (0, 1)
    # Activates the powerups if a key is pressed 
    if (event.keysym == "1" and data.powerups["RuPaul"] > 0):
        data.currPowerup = "RuPaul"
        callRuPaul(data)
    if (event.keysym == "2" and data.powerups["Alan Turing"] > 0):
        data.currPowerup = "Alan Turing"
        callAlanTuring(data)
    if (event.keysym == "3" and data.powerups["Lady Gaga"] > 0):
        data.currPowerup = "Lady Gaga"
        callLadyGaga(data)
    if (event.keysym == "Return" and data.powerups["Pride Parade"] > 0):
        data.currPowerup = "Pride Parade"
        prideParade(data)

def timerFired(data):
    # Does nothing if game is over
    if (data.gameOver == True or data.startScreen == True):
        if (data.gameOver == True):
            setHighScore(data)
        return
    # Moves forward rupaul graphics
    if (data.ruPaulIndex < 22):
        data.ruPaulIndex += 1
        data.counter += 1
        return
    # Moves forward rAlan Turing graphics
    if (data.AlanTuringIndex < 22):
        data.AlanTuringIndex += 1
        data.counter += 1
        return
    # Moves forward Lady Gaga graphics
    if (data.LadyGagaIndex < 34):
        data.LadyGagaIndex += 1
        data.counter += 1
        return
    # Player Timer Fired Actions
    data.player.onTimerFired(data)
    # Flag Timer Fired Actions
    for flag in data.rainbowFlagList:
        flag.onTimerFired(data)
    # Chad Timer Fired Actions
    for enemy in data.enemies:
        enemy.onTimerFired(data)
    # Projectile Timer Fired Actions
    for projectile in data.projectiles:
        projectile.onTimerFired(data)
    # Spawn Location Timer Fired actions
    for spawnLocation in data.spawnLocations:
        spawnLocation.onTimerFired(data)
    # Creates chad
    createChad(data)
    # Keeps track of how long a powerup has left
    if (data.ruPaulShow > 0):
        data.ruPaulShow -= 1
    if (data.stunCounter > 0):
        data.stunCounter -= 1
    if (data.prideCounter > 0):
        data.prideCounter -= 1
    # Resets the used powerup string
    data.powerup = ""
    # If all spawners are destroyed player advances to the next level and 
    # The player gains 50 points
    if (len(data.spawnLocations) == 0):
        data.score += 50
        data.level+=1
        nextLevel(data, data.level)
    # Ends game is time runs out
    if (data.timeRemaining <= 0):
        data.gameOver = True
    # Decrements time left
    data.timeRemaining -= 1
    # Increases the counter for various actions
    data.counter += 1
    
def redrawAll(canvas, data):
    # Draws start screen at beginning
    if (data.startScreen == True):
        drawStartScreen(canvas, data)
        return
    # Draws start screen if player clicked past start screen
    if (data.instructionScreen == True):
        drawInstructionScreen(canvas, data)
        return
    # Draws game over screen if the game is over
    if (data.gameOver == True):
        drawGameOver(canvas, data)
        return
    # Draws rupaul gif
    if (data.ruPaulIndex < 22):
        drawRuPaul(canvas, data)
        return
    # Draws Alan Turing gif
    if (data.AlanTuringIndex < 22):
        drawAlanTuring(canvas, data)
        return
    # Draws Lady Gaga gif
    if (data.LadyGagaIndex < 34):
        drawLadyGaga(canvas, data)
        return
    # Draws board
    makeBoard(canvas, data)
    # Draws flags
    for index in range(0, len(data.rainbowFlagList), 1):
        data.rainbowFlagList[index].draw(canvas)
    # Draws player
    data.player.draw(canvas, data)
    # Draws enemies
    for enemy in data.enemies:
        enemy.draw(canvas, data)
    # Draws projectiles
    for projectile in data.projectiles:
        projectile.draw(canvas, data)
    # Draws pride parade
    if (data.prideCounter > 0):
        drawPrideParade(canvas, data)
    drawBottomScreen(canvas, data)
    
#################################################################
# Run (Taken from 112 course website)
#################################################################

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    root = Tk()
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.configure(bd=0, highlightthickness=0)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed

run(1200, 600)