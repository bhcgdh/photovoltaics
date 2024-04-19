from flask import Blueprint
from flask_restplus import Api
from api import model_controller

"""
Create Blueprint for API V1
For each api, it should have a blueprint
"""

# simulation_result = Blueprint('get_simulation_result', __name__, url_prefix='/getsimulationresult')
pv_power = Blueprint('pv_power_predict', __name__, url_prefix='/pvpowerpredict')

"""
Create corresponding api with blueprint
Also contains doc path, title, version, description
"""
api = Api(pv_power,
          doc="/documentation",
          title='data API',
          version='1.0',
          description='Call the algorithm for power training and prediction')

"""
Add namespace for model api
"""
api.add_namespace(model_controller.model_api)

