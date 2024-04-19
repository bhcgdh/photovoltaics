import json
import logging
import datetime
import numpy as np
from fields import ModelInfo
from fields.model_fields import ModelInputFields, ModelOutputFields
from flask_restplus import Namespace, Resource
from src import pvPred

logger = logging.getLogger(__name__)

"""
Define namespace for model
"""
# simulation_result = Blueprint('get_simulation_result', __name__, url_prefix='/getsimulationresult')
# simulation_result = Blueprint('pv_power_predict', __name__, url_prefix='/pvpowerpredict')

model_api = Namespace('pv_power', description='Pv Power Scenes')

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

class ModelController(Resource):
    """
    Model controller to accept restful request
    """

    # builder factory to create builder object

    @model_api.expect(ModelInputFields().create_api_model(model_api), validate=False)
    @model_api.marshal_with(ModelOutputFields().create_api_model(model_api), skip_none=True)
    def post(self):
        logger.info('被调用API:  %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        request_object = model_api.payload
        try:
            result = pvPred(request_object).do()
            logger.info(json.dumps( ModelInfo(result, 2, "success").to_json(), indent=4,allow_nan=True) )
            return ModelInfo(result, 2, "success").to_json()

        except Exception as error:
            
            return ModelInfo([], 0, str(error)).to_json()

"""
Add resource for model
"""
model_api.add_resource(ModelController, '', endpoint='')
