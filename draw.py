import plotly.plotly as py
import plotly.graph_objs as go


class Drawer(object):

    def __init__(self):
        self.sign_in()

    @staticmethod
    def sign_in():
        py.sign_in('dey10101', 'Y6xZppqxbJHCVe1vE0VD')

    def draw_data(self, data):
      
        keys = [key[0] for key in data.keys()]        
        values = [data[value]['positive'] for value in data]        
        draw_data = [go.Bar(
                    x=keys,
                    y=values
            )]

        py.plot(draw_data, filename='test')
