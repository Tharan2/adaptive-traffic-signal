import pygame
import random
import time
import threading
import sys

# Default values of signal timers
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultYellow = 5
pygame.init()
simulation = pygame.sprite.Group()

signals = []
noOfSignals = 4
currentGreen = 0
nextGreen = (currentGreen + 1) % noOfSignals
currentYellow = 0
time_in_yellow = 0

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}
buttonCoordinates = {'right': (250, 250), 'down': (830, 140), 'left': (1000, 550), 'up': (450, 700)}
buttonColors = {'right': (255, 0, 0), 'down': (0, 255, 0), 'left': (0, 0, 255), 'up': (255, 255, 0)}
# Coordinates of vehicles' start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}
go_button_pressed = False
GO_BUTTON_EVENT = pygame.USEREVENT + 1

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
stoppingGap =15
movingGap=15
goButtonColor = (0, 255, 0)  # Green color for the button
goButtonRect = pygame.Rect(1000, 700, 100, 50)  # Adjust the position and size as needed
waitingVehicles = [0, 0, 0, 0]
# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

pygame.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.image = pygame.image.load(path)

        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index - 1].stop - \
                            vehicles[direction][lane][self.index - 1].image.get_rect().width - stoppingGap
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index - 1].stop + \
                            vehicles[direction][lane][self.index - 1].image.get_rect().width + stoppingGap
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index - 1].stop - \
                            vehicles[direction][lane][self.index - 1].image.get_rect().height - stoppingGap
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index - 1].stop + \
                            vehicles[direction][lane][self.index - 1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]

        if direction == 'right':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))
    def move(self):
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                if currentYellow == 0 or (currentYellow == 1 and time_in_yellow < 3):
                    waitingVehicles[self.direction_number] -= 1  # Decrement waiting vehicles count
            if (self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or
                    (currentGreen == 0 and currentYellow == 0)) and (
                    self.index == 0 or self.x + self.image.get_rect().width < (
                    vehicles[self.direction][self.lane][self.index - 1].x - movingGap)):
                self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
                if currentYellow == 0 or (currentYellow == 1 and time_in_yellow < 3):
                    waitingVehicles[self.direction_number] -= 1  # Decrement waiting vehicles count
            if (self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or
                    (currentGreen == 1 and currentYellow == 0)) and (
                    self.index == 0 or self.y + self.image.get_rect().height < (
                    vehicles[self.direction][self.lane][self.index - 1].y - movingGap)):
                self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                if currentYellow == 0 or (currentYellow == 1 and time_in_yellow < 3):
                    waitingVehicles[self.direction_number] -= 1  # Decrement waiting vehicles count
            if (self.x >= self.stop or self.crossed == 1 or
                    (currentGreen == 2 and currentYellow == 0)) and (
                    self.index == 0 or self.x > (
                    vehicles[self.direction][self.lane][self.index - 1].x +
                    vehicles[self.direction][self.lane][self.index - 1].image.get_rect().width + movingGap)):
                self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                if currentYellow == 0 or (currentYellow == 1 and time_in_yellow < 3):
                    waitingVehicles[self.direction_number] -= 1  # Decrement waiting vehicles count
            if (self.y >= self.stop or self.crossed == 1 or
                    (currentGreen == 3 and currentYellow == 0)) and (
                    self.index == 0 or self.y > (
                    vehicles[self.direction][self.lane][self.index - 1].y +
                    vehicles[self.direction][self.lane][self.index - 1].image.get_rect().height + movingGap)):
                self.y -= self.speed

# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
    signals.append(ts4)
    repeat()
def repeat():
    global currentGreen, currentYellow, nextGreen,go_button_pressed
    green_timer = 0  # Timer for the green signal
    yellow_timer = 0  # Timer for the yellow signal
    while True:
        # Check if the "Go" button is pressed

        # Green phase
        while ((green_timer < 3 or waitingVehicles[currentGreen] >= 5) and green_timer <= 25):
            updateValues()
            time.sleep(1)
            green_timer += 1
            # Reset the flag
            if waitingVehicles[currentGreen] < 5:
                yellow_timer = 0  # Reset yellow timer if waiting count drops below 5
            if go_button_pressed:
                go_button_pressed=False
                break
        currentYellow = 1
        for i in range(0, 3):
            for vehicle in vehicles[directionNumbers[currentGreen]][i]:
                vehicle.stop = defaultStop[directionNumbers[currentGreen]]

        # Yellow phase
        while yellow_timer < 2:
            updateValues()
            time.sleep(1)
            yellow_timer += 1

        currentYellow = 0
        signals[currentGreen].green = defaultGreen[currentGreen]
        signals[currentGreen].yellow = defaultYellow
        signals[currentGreen].red = defaultRed

        # Do not reset waiting vehicles count for the current signal

        currentGreen = nextGreen
        nextGreen = (currentGreen + 1) % noOfSignals
        signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green

        # Reset timers for the next iteration
        green_timer = 0
        yellow_timer = 0

def updateValues():
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        vehicle_type = random.randint(0, 3)
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number])
        
        # Increment waitingVehicles for the corresponding signal
        waitingVehicles[direction_number] += 1
        
        time.sleep(1)
def increaseTrafficDensity(direction):
    # Add a new vehicle to the selected side
    lane_number = random.randint(1, 2)
    vehicle_type = random.randint(0, 3)
    direction_number = list(directionNumbers.keys())[list(directionNumbers.values()).index(direction)]
    Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, direction)

    # Increment waitingVehicles for the corresponding signal
    waitingVehicles[direction_number] += 1

class Main:
    global go_button_pressed
    thread1 = threading.Thread(name="initialization", target=initialize, args=())
    thread1.daemon = True
    thread1.start()

    black = (0, 0, 0)
    white = (255, 255, 255)

    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    background = pygame.image.load('images/intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
    thread2.daemon = True
    thread2.start()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if any density increase button is clicked
                for direction, coordinates in buttonCoordinates.items():
                    if pygame.Rect(coordinates, (50, 50)).collidepoint(mouse_pos):
                        # Increase traffic density on the selected side
                        
                        increaseTrafficDensity(direction)

                # Check if the "Go" button is pressed
                if goButtonRect.collidepoint(mouse_pos):
                # Switch the green signal when the "Go" button is pressed
                    
                    go_button_pressed = True
            
       
        screen.blit(background, (0, 0))

        
        for i in range(0, noOfSignals):
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])

            # Display the number of waiting vehicles next to each signal
            waitingText = font.render(f"Waiting: {waitingVehicles[i]}", True, white, black)
            screen.blit(waitingText, (signalCoods[i][0], signalCoods[i][1] + 50))
 
        

        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()

        # Draw the "Go" button
        pygame.draw.rect(screen, goButtonColor, goButtonRect)
        goButtonText = font.render("Go", True, (0, 0, 0))
        screen.blit(goButtonText, (goButtonRect.x + 20, goButtonRect.y + 15))


        # Draw the density increase buttons
        for direction, coordinates in buttonCoordinates.items():
            pygame.draw.rect(screen, buttonColors[direction], pygame.Rect(coordinates, (50, 50)))
            densityText = font.render(f"Increase {direction}", True, (0, 0, 0))
            screen.blit(densityText, (coordinates[0] + 5, coordinates[1] + 15))

        pygame.display.flip()


if __name__ == "__main__":
    Main()