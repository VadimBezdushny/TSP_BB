import numpy as np
from flask import Flask, render_template, request, jsonify
import json

from ComplexEncoder import ComplexEncoder
from TSPSolver import TSPSolver

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate')
def calculate():
    try:
        size = request.args.get('width', 1, type=int)
        matrix = np.array([request.args.getlist('matrix[{}][]'.format(i), ) for i in range(size)], dtype=np.dtype(int))
        x = TSPSolver(matrix)
        json_result = x.run()
    except:
        return jsonify(message="Something went wrong :(", ok=False)
    return json.dumps(dict(result=json_result, message="Calculated", ok=True), cls=ComplexEncoder)
    # return jsonify(matrix=[[(x) for x in v] for v in j], message="Successfully calculated!", ok=True)


if __name__ == '__main__':
    app.run(port=7321)
