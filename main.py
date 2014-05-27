import json
import random
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.listview import ListItemButton
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty, ListProperty, StringProperty, NumericProperty

#Classe widget abstrato
class Conditions(BoxLayout):
        conditions = StringProperty()

#Classe que vai redenrizar a animação e a parte grafica da condição do tempo
class SnowConditions(Conditions):
        flake_size = 5
        num_flakes = 60
        flake_area = flake_size * num_flakes
        flake_interval = 1.0/5.0

        def __init__(self, **kwargs):
                super(SnowConditions, self).__init__(**kwargs)
                self.flakes = [[x * self.flake_size, 0] for x in range(self.num_flakes)]
                Clock.schedule_interval(self.update_flakes, self.flake_interval)

        def update_flakes(self, time):
                for f in self.flakes:
                        f[0] += random.choice([-1, 1])
                        f[1] = random.randint(0, self.flake_size)
                        if f[1] <=0:
                                f[1] = random.randint(0, int(self.height))
                
                self.canvas.before.clear()
                with self.canvas.before:
                        widget_x = self.center_x - self.flake_area/2
                        widget_y = self.pos[1]
                        for x_flake, y_flake in self.flakes:
                                x = widget_x + x_flake
                                y = widget_y + y_flake
                                
                                Color(0.9, 0.9, 1.0)
                                Ellipse(pos=(x,y), size=(self.flake_size, self.flake_size))

#Classe que armazena os dados da temperatura da cidade corrente
class CurrentWeather(BoxLayout):
        location = ListProperty(['New York', 'US'])
        conditions = ObjectProperty()
        temp = NumericProperty()
        temp_min = NumericProperty()
        temp_max = NumericProperty()

        def update_weather(self):
                weather_template = "http://api.openweathermap.org/data/2.5/weather?q={},{}&units=metric"
                weather_url = weather_template.format(*self.location)
                request = UrlRequest(weather_url, self.weather_retrieved)
        
        def weather_retrieved(self, request, data):
                data = json.loads(data.decode()) if not isinstance(data, dict) else data                
                self.render_conditions(data['weather'][0]['description'])
                self.temp = data['main']['temp']
                self.temp_min = data['main']['temp_min']
                self.temp_max = data['main']['temp_max']

        def render_conditions(self, conditions_description):
                if "clear" in conditions_description.lower():
                        conditions_widget = Factory.ClearConditions()
                elif "snow" in conditions_description.lower():
                        conditions_widget = SnowConditions()
                else:
                        conditions_widget = Factory.UnknownConditions()
                conditions_widget.conditions = conditions_description
                self.conditions.clear_widgets()
                self.conditions.add_widget(conditions_widget)

#Classe que controla a lista de botões do listItem
class LocationButton(ListItemButton):
        location = ListProperty()

#Classe que é responsável pelos forms e suas exibições
class WeatherRoot(BoxLayout):
        current_weather = ObjectProperty()
        
        def show_current_weather(self, location=None):
                self.clear_widgets()

                if self.current_weather is None:
                        self.current_weather = CurrentWeather()
                
                if location is not None:
                        self.current_weather.location = location

                self.current_weather.update_weather()
                self.add_widget(self.current_weather)
                
        def show_add_location_form(self):
                self.clear_widgets()
                self.add_widget(AddLocationForm())

#Classe que representa o form de pesquisa da cidade
class AddLocationForm(BoxLayout):
        search_input = ObjectProperty()
        
        def search_location(self):
                search_template = "http://api.openweathermap.org/data/2.5/find?q={}&type=like"
                search_url = search_template.format(self.search_input.text)
                request = UrlRequest(search_url, self.found_location)

        def found_location(self, request, data):
                data = json.loads(data.decode()) if not isinstance(data,dict) else data
                cities = ["{} ({})".format(d['name'], d['sys']['country'])
                          for d in data['list']]
                self.search_results.item_strings = cities
                self.search_results.adapter.data.clear()
                self.search_results.adapter.data.extend(cities)
                self.search_results._trigger_reset_populate()
                
        def args_converter(self, index, data_item):
                city = data_item.split(" (")[0]
                country = data_item.split(" (")[1][0:-1]
                
                return {'location': (city, country)}

#Classe App onde é startada a aplicação
class WeatherApp(App):
        pass

if __name__ == '__main__':
        WeatherApp().run()
