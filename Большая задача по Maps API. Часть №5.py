import os
import sys
import time
import pygame
import requests
import pygame_gui
import pygame_textinput


class RESP:

    def __init__(self):
        self.loc = 0.01
        self.name = "map.png"
        self.delta = 1.5
        self.max_loc = 180
        self.x_delta = 0.01
        self.y_delta = 0.01
        self.poisk_string = 'Москва'
        self.poisk_cor()
        self.type_map = 'map'
        self.types = {'схема': 'map', 'спутник': 'sat', 'гибрид': 'sat,skl'}

    def poisk_cor(self):
        map_request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={self.poisk_string}&format=json"
        response = requests.get(map_request)
        if response:
            s = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                "Point"]['pos']
            self.x, self.y = map(float, s.split())
            return self.poisk_string
        else:
            return 'Ничего не найдено'

    def get(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.x},{self.y}&spn={self.loc},{self.loc}&l={self.type_map}&geocode={self.poisk_string}"
        print(map_request)
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
        else:
            self.response = response

    def get_lock(self, delta_loc):
        if delta_loc == -1:
            self.loc /= self.delta
        elif delta_loc == 1:
            self.loc *= self.delta
        self.loc = round(self.loc, 3)
        if self.loc >= self.max_loc:
            self.loc = self.max_loc
        self.get()

    def cor(self, xc, yc):
        self.x += xc * self.x_delta
        self.y += yc * self.y_delta
        self.get()

    def new_type(self, new):
        self.type_map = self.types.get(new, self.type_map)
        self.get()
        self.save()

    def types_in(self, new):
        return new in self.types

    def poisk(self, new_poisk):
        self.poisk_string = new_poisk
        self.poisk_cor()
        self.get()
        self.save()

    def save(self):
        with open(self.name, "wb") as file:
            file.write(self.response.content)


map_resp = RESP()
map_resp.get()
map_resp.save()

WIDTH, HEIGHT = 600, 450

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT))
time_delta = clock.tick(30) / 1000.0
text = [['схема', 'спутник', 'гибрид'],
        ['искать']]
button = []
wb = 100
hb = 50
for i in range(len(text)):
    for j in range(len(text[i])):
        button.append([])
        button[i].append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((i * wb + 1, j * hb), (wb - 2, hb - 2)),
                                                      text=text[i][j],
                                                      manager=manager)
                         )
textinput = pygame_textinput.TextInputVisualizer()
while True:
    clock.tick(30)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                for i in range(len(button)):
                    for j in range(len(button[i])):
                        if event.ui_element == button[i][j]:
                            if map_resp.types_in(button[i][j].text):
                                map_resp.new_type(button[i][j].text)
                            elif button[i][j].text == 'искать':
                                textinput.value = map_resp.poisk(textinput.value)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                map_resp.get_lock(+1)
                map_resp.save()
            if event.key == pygame.K_PAGEDOWN:
                map_resp.get_lock(-1)
                map_resp.save()
            if event.key == pygame.K_UP:
                map_resp.cor(0, 1)
                map_resp.save()
            if event.key == pygame.K_DOWN:
                map_resp.cor(0, -1)
                map_resp.save()
            if event.key == pygame.K_RIGHT:
                map_resp.cor(1, 0)
                map_resp.save()
            if event.key == pygame.K_LEFT:
                map_resp.cor(-1, 0)
                map_resp.save()
        manager.process_events(event)
    manager.update(time_delta)
    textinput.update(events)
    screen.fill((0, 0, 0))
    screen.blit(pygame.image.load(map_resp.name), (0, 0))
    manager.draw_ui(screen)
    screen.blit(textinput.surface, (2 * wb, 10))
    pygame.display.flip()