# -*- coding: utf-8 -*-
"""
Created on Thu Aug 07 17:36:00 2014

@author: Lior
"""

from flask import Flask
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)

class HelloWorld(restful.Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)