import os
import sys
import time
import pygame
import requests


class RESP:

    def __init__(self):
        self.loc = 0.01
        self.name = "map.png"
        self.delta = 1.5
        self.max_loc = 180

    def get(self, delta_loc):
        if delta_loc == -1:
            self.loc /= self.delta
        elif delta_loc == 1:
            self.loc *= self.delta
        self.loc = round(self.loc, 3)
        if self.loc >= self.max_loc:
            self.loc = self.max_loc
        map_request = f"https://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=Москва&format=json"
        s = \
        requests.get(map_request).json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
            'pos']
        x, y = map(str, s.split())
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={x},{y}&spn={self.loc},{self.loc}&l=map&geocode=Москва"
        print(map_request)
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.response = response

    def save(self):
        with open(self.name, "wb") as file:
            file.write(self.response.content)


map_resp = RESP()
map_resp.get(1)
map_resp.save()

pygame.init()
screen = pygame.display.set_mode((600, 450))
clock = pygame.time.Clock()
while True:
    clock.tick(30)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                map_resp.get(+1)
                map_resp.save()
            if event.key == pygame.K_PAGEDOWN:
                map_resp.get(-1)
                map_resp.save()
    screen.fill((0, 0, 0))
    screen.blit(pygame.image.load(map_resp.name), (0, 0))
    pygame.display.flip()
    pygame.display.flip()