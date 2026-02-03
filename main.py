from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Ellipse, Rectangle, Line, PushMatrix, PopMatrix, Rotate, Translate
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.vector import Vector
from kivy.metrics import dp
from kivy.animation import Animation
import random
import math

Window.size = (800, 600)
Window.clearcolor = (0.05, 0.05, 0.1, 1)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 3
        self.health = 100
        self.max_health = 100
        self.angle = 0
        self.damage = 25
        self.fire_rate = 0.15
        self.speed_level = 1
        self.damage_level = 1
        self.health_level = 1
        self.weapon = "pistol"
        self.weapons = {
            "pistol": {"damage": 25, "fire_rate": 0.15, "name": "Пистолет", "cost": 0},
            "rifle": {"damage": 40, "fire_rate": 0.1, "name": "Винтовка", "cost": 50},
            "shotgun": {"damage": 60, "fire_rate": 0.3, "name": "Дробовик", "cost": 80},
            "machine_gun": {"damage": 20, "fire_rate": 0.05, "name": "Пулемёт", "cost": 120}
        }
        
class Zombie:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 35
        self.speed = 1.2
        self.health = 50
        self.max_health = 50
        self.angle = 0
        self.death_animation = 0
        self.is_dying = False
        
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.size = 10
        self.speed = 15
        self.angle = angle
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.lifetime = 0
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime += 1

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        with layout.canvas.before:
            Color(0.1, 0.05, 0.2)
            Rectangle(size=(2000, 2000))
        
        title = Label(text='ZOMBIE SHOOTER', 
                     pos_hint={'center_x': 0.5, 'center_y': 0.8},
                     font_size=dp(48), 
                     color=(1, 0.2, 0.2, 1),
                     bold=True)
        
        start_btn = Button(text='НАЧАТЬ ИГРУ',
                          size_hint=(0.3, 0.1),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5},
                          font_size=dp(20),
                          background_color=(0.2, 0.7, 0.2, 1))
        start_btn.bind(on_press=self.start_game)
        
        exit_btn = Button(text='ВЫХОД',
                         size_hint=(0.3, 0.1),
                         pos_hint={'center_x': 0.5, 'center_y': 0.35},
                         font_size=dp(20),
                         background_color=(0.7, 0.2, 0.2, 1))
        exit_btn.bind(on_press=self.exit_game)
        
        layout.add_widget(title)
        layout.add_widget(start_btn)
        layout.add_widget(exit_btn)
        self.add_widget(layout)
    
    def start_game(self, instance):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_new_game()
    
    def exit_game(self, instance):
        App.get_running_app().stop()

class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        
        with self.layout.canvas.before:
            Color(0.2, 0.05, 0.05)
            Rectangle(size=(2000, 2000))
        
        self.game_over_label = Label(text='ИГРА ОКОНЧЕНА!',
                                    pos_hint={'center_x': 0.5, 'center_y': 0.7},
                                    font_size=dp(42),
                                    color=(1, 0, 0, 1),
                                    bold=True)
        
        self.stats_label = Label(text='',
                                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                font_size=dp(24),
                                color=(1, 1, 1, 1))
        
        menu_btn = Button(text='В МЕНЮ',
                         size_hint=(0.6, 0.15),
                         pos_hint={'center_x': 0.5, 'center_y': 0.2},
                         font_size=dp(18),
                         background_color=(0.7, 0.7, 0.2, 1))
        menu_btn.bind(on_press=self.to_menu)
        
        self.layout.add_widget(self.game_over_label)
        self.layout.add_widget(self.stats_label)
        self.layout.add_widget(menu_btn)
        self.add_widget(self.layout)
    
    def show_stats(self, wave, money):
        self.stats_label.text = f'Волна: {wave}\\nДеньги заработано: {money}'
        
        anim = Animation(opacity=0, duration=0.5) + Animation(opacity=1, duration=0.5)
        anim.repeat = True
        anim.start(self.game_over_label)
    
    def restart_game(self, instance):
        self.manager.current = 'game'
        self.manager.get_screen('game').start_new_game()
    
    def to_menu(self, instance):
        self.manager.current = 'menu'

class Joystick(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_radius = 60
        self.stick_radius = 25
        self.center_x = 0
        self.center_y = 0
        self.stick_x = 0
        self.stick_y = 0
        self.active = False
        self.touch_id = None
        
    def get_direction(self):
        if not self.active:
            return Vector(0, 0)
        dx = self.stick_x - self.center_x
        dy = self.stick_y - self.center_y
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 5:
            return Vector(0, 0)
        return Vector(dx / self.base_radius, dy / self.base_radius)
    
    def get_angle(self):
        if not self.active:
            return None
        dx = self.stick_x - self.center_x
        dy = self.stick_y - self.center_y
        if abs(dx) < 5 and abs(dy) < 5:
            return None
        return math.atan2(dy, dx)
class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.map_width = 2000
        self.map_height = 2000
        
        self.player = Player(self.map_width / 2, self.map_height / 2)
        self.zombies = []
        self.bullets = []
        self.money = 0
        self.game_over = False
        self.paused = False
        self.in_intermission = False
        
        self.current_wave = 1
        self.max_waves = 10
        self.zombies_per_wave = 5
        self.zombies_spawned_this_wave = 0
        self.wave_complete = False
        self.intermission_timer = 0
        self.intermission_duration = 10
        
        self.camera_x = 0
        self.camera_y = 0
        
        self.move_joystick = None
        self.shoot_joystick = None
        self.last_shoot_time = 0
        
        self.game_screen = None
        
        Clock.schedule_interval(self.update, 1/60)
        Clock.schedule_interval(self.spawn_zombie_wave, 1)
    
    def start_new_game(self):
        self.__init__()
        if self.game_screen:
            self.move_joystick = self.game_screen.move_joystick
            self.shoot_joystick = self.game_screen.shoot_joystick
        
    def spawn_zombie_wave(self, dt):
        if self.game_over or self.paused or self.wave_complete or self.in_intermission:
            return
        
        if self.zombies_spawned_this_wave >= self.zombies_per_wave:
            if len(self.zombies) == 0:
                self.wave_complete = True
                self.start_intermission()
            return
        
        angle = random.uniform(0, 2 * math.pi)
        distance = random.randint(600, 800)
        x = self.player.x + math.cos(angle) * distance
        y = self.player.y + math.sin(angle) * distance
        x = max(50, min(self.map_width - 50, x))
        y = max(50, min(self.map_height - 50, y))
        
        zombie = Zombie(x, y)
        zombie.health += (self.current_wave - 1) * 10
        zombie.max_health = zombie.health
        zombie.speed += (self.current_wave - 1) * 0.2
        
        self.zombies.append(zombie)
        self.zombies_spawned_this_wave += 1
    
    def start_intermission(self):
        self.in_intermission = True
        self.intermission_timer = self.intermission_duration
        heal_amount = min(25, self.player.max_health - self.player.health)
        self.player.health += heal_amount
    
    def update_intermission(self, dt):
        if not self.in_intermission:
            return
        
        self.intermission_timer -= dt
        if self.intermission_timer <= 0:
            self.next_wave()
    
    def next_wave(self):
        if self.current_wave >= self.max_waves:
            self.game_over = True
            if self.game_screen:
                Clock.schedule_once(self.game_screen.go_to_menu, 4)
            return
        
        self.current_wave += 1
        self.zombies_per_wave = 5 + (self.current_wave - 1) * 3
        self.zombies_spawned_this_wave = 0
        self.wave_complete = False
        self.in_intermission = False
        self.intermission_timer = 0
        
    def shoot(self, angle):
        if self.game_over or self.paused or self.in_intermission:
            return
        current_time = Clock.get_time()
        weapon_stats = self.player.weapons[self.player.weapon]
        if current_time - self.last_shoot_time < weapon_stats["fire_rate"]:
            return
        self.last_shoot_time = current_time
        bullet = Bullet(self.player.x, self.player.y, angle)
        self.bullets.append(bullet)

    def update(self, dt):
        self.update_intermission(dt)
        
        if self.game_over or self.paused or self.in_intermission:
            return
            
        if self.move_joystick:
            direction = self.move_joystick.get_direction()
            if direction.length() > 0:
                self.player.x += direction.x * self.player.speed
                self.player.y += direction.y * self.player.speed
                self.player.angle = math.atan2(direction.y, direction.x)
            
        self.player.x = max(self.player.size, min(self.map_width - self.player.size, self.player.x))
        self.player.y = max(self.player.size, min(self.map_height - self.player.size, self.player.y))
        
        if self.shoot_joystick:
            angle = self.shoot_joystick.get_angle()
            if angle is not None:
                self.shoot(angle)
        
        self.camera_x = self.player.x - Window.width / 2
        self.camera_y = self.player.y - Window.height / 2
        
        for zombie in self.zombies[:]:
            if zombie.is_dying:
                zombie.death_animation -= 1
                zombie.size *= 0.95
                if zombie.death_animation <= 0:
                    self.zombies.remove(zombie)
                continue
                
            dx = self.player.x - zombie.x
            dy = self.player.y - zombie.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                zombie.x += (dx / dist) * zombie.speed
                zombie.y += (dy / dist) * zombie.speed
                zombie.angle = math.atan2(dy, dx)
                
            if dist < self.player.size + zombie.size:
                self.player.health -= 0.5
                if self.player.health <= 0:
                    self.game_over = True
                    if self.game_screen:
                        Clock.schedule_once(self.game_screen.go_to_menu, 3)
                    
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.lifetime > 120:
                self.bullets.remove(bullet)
                continue
                
            for zombie in self.zombies[:]:
                if zombie.is_dying:
                    continue
                dx = bullet.x - zombie.x
                dy = bullet.y - zombie.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist < zombie.size:
                    weapon_stats = self.player.weapons[self.player.weapon]
                    zombie.health -= weapon_stats["damage"]
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if zombie.health <= 0:
                        zombie.is_dying = True
                        zombie.death_animation = 30
                        self.money += random.randint(3, 8)
                    break
                    
        self.canvas.clear()
        self.draw()
        
    def draw(self):
        with self.canvas:
            Color(0.1, 0.15, 0.1)
            Rectangle(pos=(-self.camera_x, -self.camera_y), 
                     size=(self.map_width, self.map_height))
            
            Color(0.05, 0.1, 0.05)
            grid_size = 100
            for i in range(0, self.map_width, grid_size):
                Line(points=[i - self.camera_x, -self.camera_y, 
                           i - self.camera_x, self.map_height - self.camera_y], width=1)
            for i in range(0, self.map_height, grid_size):
                Line(points=[-self.camera_x, i - self.camera_y, 
                           self.map_width - self.camera_x, i - self.camera_y], width=1)
            
            Color(0, 0, 0, 0.3)
            for zombie in self.zombies:
                if self.is_visible(zombie.x, zombie.y):
                    shadow_alpha = 0.3 if not zombie.is_dying else 0.3 * (zombie.death_animation / 30)
                    Color(0, 0, 0, shadow_alpha)
                    Ellipse(pos=(zombie.x - self.camera_x - zombie.size/2 + 3, 
                               zombie.y - self.camera_y - zombie.size/2 - 3),
                           size=(zombie.size, zombie.size))
            
            for zombie in self.zombies:
                if self.is_visible(zombie.x, zombie.y):
                    if zombie.is_dying:
                        alpha = zombie.death_animation / 30
                        Color(0.8, 0.2, 0.2, alpha)
                    else:
                        Color(0.2, 0.6, 0.2)
                    Ellipse(pos=(zombie.x - self.camera_x - zombie.size/2, 
                               zombie.y - self.camera_y - zombie.size/2),
                           size=(zombie.size, zombie.size))
                    
                    if not zombie.is_dying:
                        Color(1, 0, 0)
                        eye_offset = zombie.size * 0.2
                        Ellipse(pos=(zombie.x - self.camera_x - 4 + math.cos(zombie.angle) * eye_offset, 
                                   zombie.y - self.camera_y - 4 + math.sin(zombie.angle) * eye_offset),
                               size=(8, 8))
                        
                        health_percent = zombie.health / zombie.max_health
                        Color(1, 0, 0)
                        Rectangle(pos=(zombie.x - self.camera_x - zombie.size/2, 
                                     zombie.y - self.camera_y + zombie.size/2 + 5),
                                 size=(zombie.size, 3))
                        Color(0, 1, 0)
                        Rectangle(pos=(zombie.x - self.camera_x - zombie.size/2, 
                                     zombie.y - self.camera_y + zombie.size/2 + 5),
                                 size=(zombie.size * health_percent, 3))
            
            for bullet in self.bullets:
                if self.is_visible(bullet.x, bullet.y):
                    Color(1, 1, 0.3, 0.8)
                    Ellipse(pos=(bullet.x - self.camera_x - bullet.size/2, 
                               bullet.y - self.camera_y - bullet.size/2),
                           size=(bullet.size, bullet.size))
                    Color(1, 0.8, 0, 0.5)
                    Ellipse(pos=(bullet.x - self.camera_x - bullet.size/2 - 2, 
                               bullet.y - self.camera_y - bullet.size/2 - 2),
                           size=(bullet.size + 4, bullet.size + 4))
            
            Color(0, 0, 0, 0.4)
            Ellipse(pos=(self.player.x - self.camera_x - self.player.size/2 + 4, 
                       self.player.y - self.camera_y - self.player.size/2 - 4),
                   size=(self.player.size, self.player.size))
            
            Color(0.2, 0.4, 0.9)
            Ellipse(pos=(self.player.x - self.camera_x - self.player.size/2, 
                       self.player.y - self.camera_y - self.player.size/2),
                   size=(self.player.size, self.player.size))
            
            Color(0.3, 0.3, 0.3)
            weapon_angle = self.player.angle if self.move_joystick and self.move_joystick.get_direction().length() > 0 else 0
            if self.shoot_joystick and self.shoot_joystick.get_angle() is not None:
                weapon_angle = self.shoot_joystick.get_angle()
            weapon_length = self.player.size * 0.7
            Line(points=[self.player.x - self.camera_x, self.player.y - self.camera_y,
                        self.player.x - self.camera_x + math.cos(weapon_angle) * weapon_length,
                        self.player.y - self.camera_y + math.sin(weapon_angle) * weapon_length],
                 width=3)
            
            Color(1, 1, 1)
            Ellipse(pos=(self.player.x - self.camera_x - 5, 
                       self.player.y - self.camera_y - 5),
                   size=(10, 10))
            Color(0, 0, 0)
            Ellipse(pos=(self.player.x - self.camera_x - 3, 
                       self.player.y - self.camera_y - 3),
                   size=(6, 6))
    
    def is_visible(self, x, y):
        screen_x = x - self.camera_x
        screen_y = y - self.camera_y
        return -100 < screen_x < Window.width + 100 and -100 < screen_y < Window.height + 100
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root = FloatLayout()
        self.game = GameWidget()
        self.game.game_screen = self
        self.root.add_widget(self.game)
        
        self.wave_label = Label(text='Волна: 1/10', 
                                pos_hint={'center_x': 0.5, 'top': 0.99},
                                size_hint=(None, None),
                                font_size=dp(24),
                                color=(1, 0.8, 0, 1),
                                bold=True)
        
        self.money_label = Label(text='Деньги: 0', 
                                pos_hint={'x': 0.02, 'top': 0.99},
                                size_hint=(None, None),
                                font_size=dp(18),
                                color=(1, 0.84, 0, 1),
                                bold=True)
        
        self.weapon_label = Label(text='Оружие: Пистолет', 
                                 pos_hint={'x': 0.02, 'top': 0.94},
                                 size_hint=(None, None),
                                 font_size=dp(16),
                                 color=(0.8, 0.8, 1, 1),
                                 bold=True)
        
        self.health_label = Label(text='Здоровье: 100/100', 
                                 pos_hint={'right': 0.98, 'top': 0.99},
                                 size_hint=(None, None),
                                 font_size=dp(18),
                                 color=(0, 1, 0, 1),
                                 bold=True)
        self.zombies_label = Label(text='Зомби: 0/5', 
                                   pos_hint={'right': 0.98, 'top': 0.94},
                                   size_hint=(None, None),
                                   font_size=dp(16),
                                   color=(1, 0.5, 0.5, 1),
                                   bold=True)
        
        self.intermission_label = Label(text='', 
                                       pos_hint={'center_x': 0.5, 'center_y': 0.6},
                                       size_hint=(None, None),
                                       font_size=dp(32),
                                       color=(0, 1, 1, 1),
                                       bold=True)
        self.intermission_timer_label = Label(text='', 
                                             pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                             size_hint=(None, None),
                                             font_size=dp(48),
                                             color=(1, 1, 1, 1),
                                             bold=True)
        self.intermission_info_label = Label(text='', 
                                            pos_hint={'center_x': 0.5, 'center_y': 0.4},
                                            size_hint=(None, None),
                                            font_size=dp(18),
                                            color=(0.8, 0.8, 0.8, 1))
        
        self.game_over_overlay = Label(text='', 
                                      pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                      size_hint=(None, None),
                                      font_size=dp(36),
                                      color=(1, 0, 0, 1),
                                      bold=True)
        
        self.shop_btn = Button(text='Магазин', 
                              size_hint=(None, None),
                              size=(dp(100), dp(35)),
                              pos_hint={'x': 0.02, 'top': 0.88},
                              background_color=(0.4, 0.3, 0.2, 1),
                              font_size=dp(14))
        self.shop_btn.bind(on_press=self.open_shop)
        
        self.upgrade_btn = Button(text='Улучшения', 
                                 size_hint=(None, None),
                                 size=(dp(100), dp(35)),
                                 pos_hint={'x': 0.02, 'top': 0.82},
                                 background_color=(0.2, 0.4, 0.3, 1),
                                 font_size=dp(14))
        self.upgrade_btn.bind(on_press=self.open_upgrades)
        
        self.root.add_widget(self.wave_label)
        self.root.add_widget(self.money_label)
        self.root.add_widget(self.weapon_label)
        self.root.add_widget(self.health_label)
        self.root.add_widget(self.zombies_label)
        self.root.add_widget(self.intermission_label)
        self.root.add_widget(self.intermission_timer_label)
        self.root.add_widget(self.intermission_info_label)
        self.root.add_widget(self.game_over_overlay)
        self.root.add_widget(self.shop_btn)
        self.root.add_widget(self.upgrade_btn)
        
        joy_size = min(Window.width, Window.height) * 0.25
        
        self.move_joystick = Joystick(size_hint=(None, None), 
                                     size=(joy_size, joy_size),
                                     pos_hint={'x': 0.02, 'y': 0.02})
        self.move_joystick.center_x = joy_size / 2 + dp(20)
        self.move_joystick.center_y = joy_size / 2 + dp(20)
        self.move_joystick.stick_x = self.move_joystick.center_x
        self.move_joystick.stick_y = self.move_joystick.center_y
        self.root.add_widget(self.move_joystick)
        self.game.move_joystick = self.move_joystick
        
        self.shoot_joystick = Joystick(size_hint=(None, None), 
                                      size=(joy_size, joy_size),
                                      pos_hint={'right': 0.98, 'y': 0.02})
        self.shoot_joystick.center_x = Window.width - joy_size / 2 - dp(20)
        self.shoot_joystick.center_y = joy_size / 2 + dp(20)
        self.shoot_joystick.stick_x = self.shoot_joystick.center_x
        self.shoot_joystick.stick_y = self.shoot_joystick.center_y
        self.root.add_widget(self.shoot_joystick)
        self.game.shoot_joystick = self.shoot_joystick
        
        self.move_joystick.bind(on_touch_down=self.on_joystick_touch_down)
        self.move_joystick.bind(on_touch_move=self.on_joystick_touch_move)
        self.move_joystick.bind(on_touch_up=self.on_joystick_touch_up)
        
        self.shoot_joystick.bind(on_touch_down=self.on_joystick_touch_down)
        self.shoot_joystick.bind(on_touch_move=self.on_joystick_touch_move)
        self.shoot_joystick.bind(on_touch_up=self.on_joystick_touch_up)
        
        Clock.schedule_interval(self.update_ui, 1/30)
        Clock.schedule_interval(self.draw_joysticks, 1/60)
        
        Window.bind(on_resize=self.on_window_resize)
        
        self.add_widget(self.root)
    
    def start_new_game(self):
        self.game.start_new_game()
        self.game.move_joystick = self.move_joystick
        self.game.shoot_joystick = self.shoot_joystick
    
    def show_game_over(self):
        game_over_screen = self.manager.get_screen('game_over')
        game_over_screen.show_stats(self.game.current_wave, self.game.money)
        self.manager.current = 'game_over'
    
    def go_to_menu(self, dt=None):
        self.manager.current = 'menu'
    
    def on_window_resize(self, instance, width, height):
        joy_size = min(width, height) * 0.25
        self.move_joystick.center_x = joy_size / 2 + dp(20)
        self.move_joystick.center_y = joy_size / 2 + dp(20)
        self.shoot_joystick.center_x = width - joy_size / 2 - dp(20)
        self.shoot_joystick.center_y = joy_size / 2 + dp(20)
    
    def open_shop(self, instance):
        if self.game.game_over:
            return
        
        self.game.paused = True
        
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text='МАГАЗИН ОРУЖИЯ', font_size=dp(22), size_hint_y=0.1, bold=True))
        content.add_widget(Label(text=f'Деньги: {self.game.money}', font_size=dp(18), size_hint_y=0.1))
        
        weapons_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=0.6)
        
        for weapon_id, weapon_data in self.game.player.weapons.items():
            if weapon_id == "pistol":
                continue
            
            owned = weapon_id == self.game.player.weapon
            btn_text = f'{weapon_data["name"]} - {weapon_data["cost"]} руб.'
            if owned:
                btn_text += ' (ЭКИПИРОВАНО)'
            
            weapon_btn = Button(text=btn_text, font_size=dp(16), size_hint_y=0.25)
            if owned:
                weapon_btn.background_color = (0.2, 0.7, 0.2, 1)
            else:
                weapon_btn.bind(on_press=lambda x, w=weapon_id: self.buy_weapon(w, popup))
            weapons_layout.add_widget(weapon_btn)
        
        upgrades_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=0.6)
        
        damage_cost = self.game.player.damage_level * 15
        damage_btn = Button(text=f'Урон (Ур.{self.game.player.damage_level}) - {damage_cost} руб.',
                           font_size=dp(16), size_hint_y=0.33)
        damage_btn.bind(on_press=lambda x: self.upgrade_stat('damage', damage_cost, popup))
        upgrades_layout.add_widget(damage_btn)
        
        speed_cost = self.game.player.speed_level * 15
        speed_btn = Button(text=f'Скорость (Ур.{self.game.player.speed_level}) - {speed_cost} руб.',
                          font_size=dp(16), size_hint_y=0.33)
        speed_btn.bind(on_press=lambda x: self.upgrade_stat('speed', speed_cost, popup))
        upgrades_layout.add_widget(speed_btn)
        
        health_cost = self.game.player.health_level * 20
        health_btn = Button(text=f'Макс. здоровье (Ур.{self.game.player.health_level}) - {health_cost} руб.',
                           font_size=dp(16), size_hint_y=0.33)
        health_btn.bind(on_press=lambda x: self.upgrade_stat('health', health_cost, popup))
        upgrades_layout.add_widget(health_btn)
        
        content.add_widget(weapons_layout)
        
        close_btn = Button(text='Закрыть', font_size=dp(18), size_hint_y=0.1)
        close_btn.bind(on_press=lambda x: self.close_shop(popup))
        content.add_widget(close_btn)
        
        popup = Popup(title='', content=content, size_hint=(0.9, 0.8), auto_dismiss=False)
        popup.open()
    
    def open_upgrades(self, instance):
        if self.game.game_over:
            return
        
        self.game.paused = True
        
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(Label(text='УЛУЧШЕНИЯ', font_size=dp(22), size_hint_y=0.15, bold=True))
        content.add_widget(Label(text=f'Деньги: {self.game.money}', font_size=dp(18), size_hint_y=0.1))
        
        upgrades = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=0.6)
        
        damage_cost = self.game.player.damage_level * 15
        damage_btn = Button(text=f'Урон (Ур.{self.game.player.damage_level}) - {damage_cost} руб.',
                           font_size=dp(16), size_hint_y=0.33)
        damage_btn.bind(on_press=lambda x: self.upgrade_stat('damage', damage_cost, popup))
        upgrades.add_widget(damage_btn)
        
        speed_cost = self.game.player.speed_level * 15
        speed_btn = Button(text=f'Скорость (Ур.{self.game.player.speed_level}) - {speed_cost} руб.',
                          font_size=dp(16), size_hint_y=0.33)
        speed_btn.bind(on_press=lambda x: self.upgrade_stat('speed', speed_cost, popup))
        upgrades.add_widget(speed_btn)
        
        health_cost = self.game.player.health_level * 20
        health_btn = Button(text=f'Макс. здоровье (Ур.{self.game.player.health_level}) - {health_cost} руб.',
                           font_size=dp(16), size_hint_y=0.33)
        health_btn.bind(on_press=lambda x: self.upgrade_stat('health', health_cost, popup))
        upgrades.add_widget(health_btn)
        
        content.add_widget(upgrades)
        
        close_btn = Button(text='Закрыть', font_size=dp(18), size_hint_y=0.15)
        close_btn.bind(on_press=lambda x: self.close_shop(popup))
        content.add_widget(close_btn)
        
        popup = Popup(title='', content=content, size_hint=(0.85, 0.7), auto_dismiss=False)
        popup.open()
    
    def buy_weapon(self, weapon_id, popup):
        weapon_data = self.game.player.weapons[weapon_id]
        if self.game.money >= weapon_data["cost"]:
            self.game.money -= weapon_data["cost"]
            self.game.player.weapon = weapon_id
            popup.dismiss()
            self.open_shop(None)
    
    def upgrade_stat(self, stat, cost, popup):
        if self.game.money < cost:
            return
        
        self.game.money -= cost
        
        if stat == 'damage':
            self.game.player.damage_level += 1
            for weapon in self.game.player.weapons.values():
                weapon["damage"] += 10
        elif stat == 'speed':
            self.game.player.speed_level += 1
            self.game.player.speed += 1
        elif stat == 'health':
            self.game.player.health_level += 1
            self.game.player.max_health += 25
            self.game.player.health = self.game.player.max_health
        
        popup.dismiss()
        self.open_upgrades(None)
    
    def close_shop(self, popup):
        popup.dismiss()
        self.game.paused = False
    
    def on_joystick_touch_down(self, instance, touch):
        if instance.collide_point(*touch.pos):
            if not instance.active:
                instance.active = True
                instance.touch_id = touch.uid
                instance.stick_x = touch.x
                instance.stick_y = touch.y
                return True
        return False
    
    def on_joystick_touch_move(self, instance, touch):
        if instance.active and instance.touch_id == touch.uid:
            dx = touch.x - instance.center_x
            dy = touch.y - instance.center_y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > instance.base_radius:
                dx = dx / dist * instance.base_radius
                dy = dy / dist * instance.base_radius
            instance.stick_x = instance.center_x + dx
            instance.stick_y = instance.center_y + dy
            return True
        return False
    
    def on_joystick_touch_up(self, instance, touch):
        if instance.active and instance.touch_id == touch.uid:
            instance.active = False
            instance.touch_id = None
            instance.stick_x = instance.center_x
            instance.stick_y = instance.center_y
            return True
        return False
    
    def draw_joysticks(self, dt):
        self.move_joystick.canvas.clear()
        with self.move_joystick.canvas:
            Color(0.3, 0.3, 0.3, 0.5)
            Ellipse(pos=(self.move_joystick.center_x - self.move_joystick.base_radius,
                        self.move_joystick.center_y - self.move_joystick.base_radius),
                   size=(self.move_joystick.base_radius * 2, self.move_joystick.base_radius * 2))
            Color(0.5, 0.5, 0.5, 0.8)
            Ellipse(pos=(self.move_joystick.stick_x - self.move_joystick.stick_radius,
                        self.move_joystick.stick_y - self.move_joystick.stick_radius),
                   size=(self.move_joystick.stick_radius * 2, self.move_joystick.stick_radius * 2))
        
        self.shoot_joystick.canvas.clear()
        with self.shoot_joystick.canvas:
            Color(0.5, 0.2, 0.2, 0.5)
            Ellipse(pos=(self.shoot_joystick.center_x - self.shoot_joystick.base_radius,
                        self.shoot_joystick.center_y - self.shoot_joystick.base_radius),
                   size=(self.shoot_joystick.base_radius * 2, self.shoot_joystick.base_radius * 2))
            Color(0.8, 0.3, 0.3, 0.8)
            Ellipse(pos=(self.shoot_joystick.stick_x - self.shoot_joystick.stick_radius,
                        self.shoot_joystick.stick_y - self.shoot_joystick.stick_radius),
                   size=(self.shoot_joystick.stick_radius * 2, self.shoot_joystick.stick_radius * 2))
    
    def update_ui(self, dt):
        self.wave_label.text = f'Волна: {self.game.current_wave}/{self.game.max_waves}'
        self.money_label.text = f'Деньги: {self.game.money}'
        weapon_name = self.game.player.weapons[self.game.player.weapon]["name"]
        self.weapon_label.text = f'Оружие: {weapon_name}'
        health = max(0, int(self.game.player.health))
        self.health_label.text = f'Здоровье: {health}/{self.game.player.max_health}'
        killed = self.game.zombies_spawned_this_wave - len(self.game.zombies)
        self.zombies_label.text = f'Зомби: {killed}/{self.game.zombies_per_wave}'
        
        if self.game.in_intermission:
            if self.game.current_wave >= self.game.max_waves:
                self.intermission_label.text = 'ПОБЕДА!'
                self.intermission_timer_label.text = 'Все волны пройдены!'
                self.intermission_info_label.text = f'Финальный счёт: {self.game.money} рублей'
            else:
                self.intermission_label.text = f'Подготовка к волне {self.game.current_wave + 1}'
                timer = int(self.game.intermission_timer)
                self.intermission_timer_label.text = f'{timer:02d}'
                next_zombies = 5 + self.game.current_wave * 3
                self.intermission_info_label.text = f'Следующая волна: {next_zombies} зомби | +25 здоровья | Используйте магазин!'
        else:
            self.intermission_label.text = ''
            self.intermission_timer_label.text = ''
            self.intermission_info_label.text = ''
        
        if self.game.game_over:
            self.wave_label.text = 'ИГРА ОКОНЧЕНА!'
            self.wave_label.color = (1, 0, 0, 1)
            if self.game.current_wave >= self.game.max_waves:
                self.game_over_overlay.text = 'ПОБЕДА!\nВозврат в меню через 4 сек...'
                self.game_over_overlay.color = (0, 1, 0, 1)
            else:
                self.game_over_overlay.text = 'ПОРАЖЕНИЕ!\nВозврат в меню через 3 сек...'
                self.game_over_overlay.color = (1, 0, 0, 1)
        else:
            self.game_over_overlay.text = ''

class ZombieShooterApp(App):
    def build(self):
        sm = ScreenManager()
        
        menu_screen = MenuScreen(name='menu')
        game_screen = GameScreen(name='game')
        game_over_screen = GameOverScreen(name='game_over')
        
        sm.add_widget(menu_screen)
        sm.add_widget(game_screen)
        sm.add_widget(game_over_screen)
        
        return sm

if __name__ == '__main__':
    ZombieShooterApp().run()